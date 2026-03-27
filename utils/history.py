"""
utils/history.py
Manages receipt history within the session and provides JSON export/import.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

import streamlit as st


def _init_history() -> None:
    """Ensure session_state has a history list."""
    if "receipt_history" not in st.session_state:
        st.session_state.receipt_history = []


def save_receipt(
    inputs: dict[str, Any],
    driving: dict[str, Any],
    food: dict[str, Any],
    water: dict[str, Any],
    energy: dict[str, Any],
    savings: dict[str, Any],
    total_cost: float,
    total_water: float,
) -> None:
    """Append a receipt snapshot to the in-session history."""
    _init_history()
    receipt = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "week_of": date.today().strftime("%B %d, %Y"),
        "inputs": inputs,
        "results": {
            "driving": driving,
            "food": food,
            "water": water,
            "energy": energy,
            "savings": savings,
            "total_cost": total_cost,
            "total_water": total_water,
        },
    }
    st.session_state.receipt_history.insert(0, receipt)  # newest first


def export_history_json() -> str:
    """Return the full history as a JSON string for download."""
    _init_history()
    return json.dumps(st.session_state.receipt_history, indent=2)


def import_history_json(raw: str) -> tuple[bool, str]:
    """
    Load history from a JSON string the user uploaded.
    Handles two formats:
      - A single receipt object  {"week_of": ..., "inputs": ..., "results": ...}
      - A list of receipt objects [{"saved_at": ..., "results": ...}, ...]
    Returns (success, message).
    """
    _init_history()
    try:
        data = json.loads(raw)

        # ── Normalise: wrap a single receipt dict into a list ──────────────
        if isinstance(data, dict):
            if "results" not in data:
                return False, "File does not look like a valid receipt."
            # Inject a saved_at if missing (single-receipt exports don't have one)
            if "saved_at" not in data:
                data["saved_at"] = data.get("week_of", "unknown")
            data = [data]

        if not isinstance(data, list):
            return False, "File must be a receipt object or a list of receipts."

        # ── Validate each entry ────────────────────────────────────────────
        for item in data:
            if "results" not in item:
                return False, "One or more receipts have an unexpected format."
            if "saved_at" not in item:
                item["saved_at"] = item.get("week_of", "unknown")

        # ── Merge, deduplicating by saved_at ──────────────────────────────
        existing_keys = {r["saved_at"] for r in st.session_state.receipt_history}
        new_entries = [r for r in data if r["saved_at"] not in existing_keys]
        st.session_state.receipt_history = (
            new_entries + st.session_state.receipt_history
        )
        st.session_state.receipt_history.sort(key=lambda r: r["saved_at"], reverse=True)
        return True, f"Loaded {len(new_entries)} new receipt(s)."
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON file: {exc}"


def render_history_panel() -> None:
    """
    Render the full history sidebar / expander section.
    Call this from app.py after the main receipt block.
    """
    _init_history()
    history = st.session_state.receipt_history

    st.divider()
    st.subheader("📋 Receipt History")

    # ── Import ──────────────────────────────────────────────────────────────
    with st.expander("📂 Load a saved history file"):
        uploaded = st.file_uploader(
            "Upload your guilt_receipts.json",
            type=["json"],
            key="history_upload",
        )
        if uploaded is not None:
            ok, msg = import_history_json(uploaded.read().decode("utf-8"))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    if not history:
        st.info("No receipts yet. Print one above and it will appear here!")
        return

    # ── Export ──────────────────────────────────────────────────────────────
    col_exp, col_clr = st.columns([3, 1])
    with col_exp:
        st.download_button(
            label="💾 Save history to my computer",
            data=export_history_json(),
            file_name="guilt_receipts.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_clr:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.receipt_history = []
            st.rerun()

    # ── Receipt cards ────────────────────────────────────────────────────────
    for i, receipt in enumerate(history):
        r = receipt["results"]
        inp = receipt.get("inputs", {})
        label = (
            f"🧾 {receipt['week_of']}  |  "
            f"${r['total_cost']:.2f} cost  |  "
            f"{r['total_water']:,.0f} gal water"
        )
        with st.expander(label, expanded=(i == 0)):
            st.caption(f"Saved at {receipt['saved_at']}")

            # Key numbers at a glance
            m1, m2, m3 = st.columns(3)
            m1.metric("Weekly Cost", f"${r['total_cost']:.2f}")
            m2.metric("Water Used", f"{r['total_water']:,.0f} gal")
            m3.metric(
                "Traffic Hours",
                f"{r['driving'].get('hours_in_traffic', '—')} hrs",
            )

            # Inputs summary
            if inp:
                st.markdown("**Your inputs that week:**")
                ic1, ic2 = st.columns(2)
                ic1.write(f"🚗 Miles driven: **{inp.get('miles_driven', '—')}**")
                ic1.write(f"🚕 Rideshare trips: **{inp.get('rideshare_trips', '—')}**")
                ic1.write(f"🍔 Beef meals: **{inp.get('burgers', '—')}**")
                ic1.write(f"🍗 Chicken meals: **{inp.get('chicken_meals', '—')}**")
                ic2.write(
                    f"🚿 Shower: **{inp.get('shower_minutes', '—')} min × {inp.get('showers_per_week', '—')}**"
                )
                ic2.write(f"❄️ AC hours: **{inp.get('ac_hours', '—')}**")
                ic2.write(f"🔌 Phantom devices: **{inp.get('devices_left_on', '—')}**")

            # Top saving tip
            sv = r.get("savings", {})
            if sv:
                best_money = max(
                    sv.get("saved_drive_yearly", 0), sv.get("saved_ac_yearly", 0)
                )
                st.markdown(
                    f"<div style='margin-top:8px;padding:8px 12px;"
                    f"background:#1e4d2b;border-left:3px solid #4caf50;"
                    f"border-radius:4px;font-size:13px;color:#e8f5e9'>"
                    f"💡 Top opportunity: up to <b>${best_money:.0f}/year</b> in savings</div>",
                    unsafe_allow_html=True,
                )
