import os
from flask import Flask, request, jsonify
from utils import ensure_logs_dir, extract_and_update_call_state

app = Flask(__name__)
ensure_logs_dir()

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    try:
        # More forgiving than force=True; avoids exceptions on bad headers
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
        # Never let exceptions bubble up to Railway (prevents 502)
        app.logger.exception(f"/webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Webhook server running ✅"}), 200

if __name__ == "__main__":
    # Use Railway's injected PORT if available; default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
