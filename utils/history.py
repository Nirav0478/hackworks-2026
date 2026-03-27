import json
from datetime import datetime
import streamlit as st


def save_receipt(inputs, results):
    entry = {
        "week_of": results.get("week_of", ""),
        "saved_at": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "inputs": inputs,
        "results": results,
    }
    st.session_state.receipt_history.append(entry)


def export_history_json():
    return json.dumps(st.session_state.receipt_history, indent=2)


def import_history_json(raw):
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return False, "File doesn't look right — expected a receipt or list of receipts."
        # patch any entries missing saved_at
        for entry in data:
            if "saved_at" not in entry:
                entry["saved_at"] = entry.get("week_of", "unknown")
        st.session_state.receipt_history = data
        return True, f"Loaded {len(data)} receipt(s)."
    except json.JSONDecodeError:
        return False, "Couldn't parse the file. Make sure it's a valid JSON export."