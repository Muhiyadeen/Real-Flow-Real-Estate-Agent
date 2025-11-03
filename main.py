# main.py  (rename to app.py if you prefer; adjust gunicorn entry accordingly)

import os
import json
import glob
import time
from flask import Flask, request, jsonify
from utils import ensure_logs_dir, extract_and_update_call_state

# --- Config ---
BASE_DIR = os.path.abspath(os.getcwd())
LOG_DIR = os.path.join(BASE_DIR, "logs", "call_logs")
READ_TOKEN = os.getenv("READ_TOKEN", "").strip()        # optional: set in Railway Variables
MASK_PII = os.getenv("MASK_PII", "false").lower() == "true"

# --- App ---
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["JSON_SORT_KEYS"] = False
ensure_logs_dir()



# ---------- Helpers (masking for read-only views) ----------

def _mask_phone(phone: str) -> str:
    if not isinstance(phone, str) or len(phone) < 5:
        return "•••"
    return phone[:2] + "•••" + phone[-2:]

def _mask_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return "•••"
    local, _, domain = email.partition("@")
    shown_local = local[:2] + "•••" if len(local) > 2 else "•••"
    return f"{shown_local}@{domain}"

def _scrub_doc(doc: dict) -> dict:
    if not MASK_PII:
        return doc
    try:
        d = json.loads(json.dumps(doc))  # deep copy
        args = d["call_details"]["Set_Lead_Field"]["arguments"]
        if "phone" in args:
            args["phone"] = _mask_phone(args["phone"])
        if "email" in args:
            args["email"] = _mask_email(args["email"])
        return d
    except Exception:
        return doc


# ---------- Routes ----------

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "Webhook server running ✅"}), 200


@app.route("/ping", methods=["POST"])
def ping():
    return jsonify({"ok": True}), 200


# POST: Vapi -> your webhook (store/update call logs)
@app.route("/webhook", methods=["POST"])
def receive_webhook():
    try:
        # Use silent=True to avoid exceptions on wrong/missing Content-Type
        data = request.get_json(silent=True)

        if data is None:
            app.logger.warning("No/invalid JSON body or wrong Content-Type")
            return jsonify({"status": "bad request", "reason": "invalid json"}), 400

        updated = extract_and_update_call_state(data)
        if not updated:
            app.logger.warning("No call_id or no relevant toolCalls")
            return jsonify({"status": "invalid payload"}), 400

        call_id = updated.get("call_id", "unknown")
        app.logger.info(f"✅ Updated log for call_id={call_id}")
        return jsonify({"status": "webhook received", "call_id": call_id}), 200

    except Exception as e:
        app.logger.exception("/webhook error")
        return jsonify({"status": "error", "message": str(e)}), 500


# GET: Read-only viewer on the same endpoint
#   - GET /webhook                   -> list recent logs (up to 20)
#   - GET /webhook?call_id=<id>      -> fetch a specific log

@app.route("/webhook", methods=["GET"])
def list_or_get_logs():
    # Optional token gate for demo security
    if READ_TOKEN and request.args.get("token") != READ_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    os.makedirs(LOG_DIR, exist_ok=True)
    call_id = request.args.get("call_id")

    # --- Specific log view ---
    if call_id:
        path = os.path.join(LOG_DIR, f"{call_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                doc = json.load(f)
            # ✅ Force pretty-printed JSON
            pretty = json.dumps(_scrub_doc(doc), indent=4, ensure_ascii=False)
            return app.response_class(
                response=pretty,
                status=200,
                mimetype="application/json"
            )
        return jsonify({"error": "not found", "call_id": call_id}), 404

    # --- List view (latest logs) ---
    files = []
    for p in glob.glob(os.path.join(LOG_DIR, "*.json")):
        ts = os.path.getmtime(p)
        files.append({
            "call_id": os.path.splitext(os.path.basename(p))[0],
            "modified": int(ts),
            "modified_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
        })

    files.sort(key=lambda x: x["modified"], reverse=True)
    pretty = json.dumps({"count": len(files), "latest": files[:20]}, indent=4, ensure_ascii=False)
    return app.response_class(response=pretty, status=200, mimetype="application/json")


# ---------- Entrypoint ----------
if __name__ == "__main__":
    # Railway/Render inject PORT; default to 8080 for local dev
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
