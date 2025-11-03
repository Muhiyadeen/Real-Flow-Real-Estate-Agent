import os
import json

def ensure_logs_dir():
    os.makedirs("logs/call_logs", exist_ok=True)

def to_jsonl_line(data):
    return json.dumps(data)

def save_json_to_file(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_json_if_exists(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None

def extract_and_update_call_state(data):
    """
    Extracts call_id from data['call']['id'] and updates logs for Set_Lead_Field / Submit_Lead.
    Handles toolCalls inside data['message'].
    """

    call_id = data.get("message",{}).get("call", {}).get("id")
    if not call_id:
        print("No call_id found in webhook data.")
        return None

    filepath = f"logs/call_logs/caller_id_{call_id}.json"

    existing = load_json_if_exists(filepath)
    if not existing:
        existing = {"call_id": call_id, "call_details": {}}

    tool_calls = []
    if "message" in data and "toolCalls" in data["message"]:
        tool_calls = data["message"]["toolCalls"]
    elif "toolCallList" in data:
        tool_calls = data["toolCallList"]
    elif "toolWithToolCallList" in data:
        tool_calls = data["toolWithToolCallList"]

    if not tool_calls:
        print(f" No toolCalls found for call {call_id}")
        return existing

    for call in tool_calls:
        func = call.get("function", {})
        func_name = func.get("name")
        args = func.get("arguments", {})

        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                continue

        if func_name in ["Set_Lead_Field", "Submit_Lead"]:
            if func_name not in existing["call_details"]:
                existing["call_details"][func_name] = {"name": func_name, "arguments": {}}

            if func_name == "Set_Lead_Field" and "field" in args and "value" in args:
                existing["call_details"][func_name]["arguments"][args["field"]] = args["value"]
            else:
                for k, v in args.items():
                    existing["call_details"][func_name]["arguments"][k] = v

    save_json_to_file(existing, filepath)
    return existing


