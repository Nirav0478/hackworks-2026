import json
from datetime import date

import streamlit as st

from utils.calculator import (
    calculate_driving,
    calculate_energy,
    calculate_food,
    calculate_savings,
    calculate_water,
)
from utils.history import export_history_json, import_history_json
from utils.pdf_generator import generate_receipt_pdf

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="The Guilt Receipt", page_icon="🧾", layout="centered")

# ── session state init ─────────────────────────────────────────────────────────
if "receipt_history" not in st.session_state:
    st.session_state.receipt_history = []

# ── styles ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .receipt-total {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-top: 8px;
        background: #2d2d2d;
        color: #f5f5f5;
        padding: 16px;
        border-radius: 8px;
    }
    .receipt-savings {
        background: #1e4d2b;
        border-left: 4px solid #4caf50;
        padding: 10px 16px;
        border-radius: 4px;
        font-size: 14px;
        margin-top: 16px;
        color: #e8f5e9;
    }
    .receipt-tagline {
        text-align: center;
        font-size: 12px;
        color: #888;
        margin-top: 12px;
    }
    .target-user-badge {
        background: #2a2550;
        border-left: 4px solid #7c6af7;
        padding: 8px 14px;
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 16px;
        color: #ddd8ff;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── header ─────────────────────────────────────────────────────────────────────
st.title("🧾 The Guilt Receipt")
st.markdown("*Enter a week of your habits. We'll hand you the bill.*")

st.markdown(
    """
<div class="target-user-badge">
    🎯 <b>Built for:</b> College students & young renters who want to make smarter choices —
    without the climate guilt trip.
</div>
""",
    unsafe_allow_html=True,
)

# ── JSON import (top of page) ──────────────────────────────────────────────────
with st.expander("📂 Load a previously saved receipt history"):
    uploaded = st.file_uploader(
        "Upload your guilt_receipts.json to restore past receipts",
        type=["json"],
        key="history_upload",
    )
    if uploaded is not None:
        ok, msg = import_history_json(uploaded.read().decode("utf-8"))
        if ok:
            # No st.rerun() here — history renders below on the same pass
            st.success(f"✅ {msg} Scroll down to see your history.")
        else:
            st.error(f"❌ {msg}")

st.divider()

# ── inputs ─────────────────────────────────────────────────────────────────────
st.subheader("🚗 Getting Around")
miles_driven = st.slider("Miles driven this week", 0, 500, 80)
rideshare_trips = st.number_input("Rideshare trips (Uber/Lyft) this week", 0, 30, 2)

st.subheader("🍔 What You Ate")
burgers = st.slider("Beef meals this week", 0, 21, 4)
chicken_meals = st.slider("Chicken meals this week", 0, 21, 5)

st.subheader("🚿 Showers")
shower_minutes = st.slider("Average shower length (minutes)", 1, 30, 10)
showers_per_week = st.slider("Showers per week", 0, 14, 7)

st.subheader("❄️ Home Energy")
ac_hours = st.slider("Hours AC ran this week", 0, 168, 40)
devices_left_on = st.number_input(
    "Devices/chargers left plugged in when not in use", 0, 20, 5
)

st.divider()

# ── calculations ───────────────────────────────────────────────────────────────
driving = calculate_driving(miles_driven, rideshare_trips)
food = calculate_food(burgers, chicken_meals)
water = calculate_water(shower_minutes, showers_per_week)
energy = calculate_energy(ac_hours, devices_left_on)
savings = calculate_savings(
    miles_driven, burgers, shower_minutes, showers_per_week, ac_hours
)

total_cost = (
    driving["drive_cost"]
    + driving["rideshare_cost"]
    + energy["ac_cost"]
    + energy["phantom_cost"]
)
total_water = water["shower_gallons"] + food["total_water_food"]

inputs = {
    "miles_driven": miles_driven,
    "rideshare_trips": rideshare_trips,
    "burgers": burgers,
    "chicken_meals": chicken_meals,
    "shower_minutes": shower_minutes,
    "showers_per_week": showers_per_week,
    "ac_hours": ac_hours,
    "devices_left_on": devices_left_on,
}

# ── live receipt (updates as sliders move) ─────────────────────────────────────
st.markdown("---")
st.markdown("### 🧾 YOUR RECEIPT — LIVE")
st.caption(f"Week of {date.today().strftime('%B %d, %Y')} | Updates as you go 💚")

# Driving
st.markdown("##### 🚗 Getting Around")
col1, col2 = st.columns([3, 1])
col1.write(f"Driving ({miles_driven} mi)")
col2.write(f"**${driving['drive_cost']:.2f}**")
col1, col2 = st.columns([3, 1])
col1.write("Gas burned")
col2.write(f"**{driving['gas_gallons']:.1f} gal**")
col1, col2 = st.columns([3, 1])
col1.write(f"Rideshare ({rideshare_trips} trips)")
col2.write(f"**${driving['rideshare_cost']:.2f}**")
col1, col2 = st.columns([3, 1])
col1.write("Time stuck in traffic")
col2.write(f"**{driving['hours_in_traffic']} hrs**")
st.caption(f"🕐 That's {driving['hours_in_traffic']} hours you'll never get back.")

st.divider()

# Food
st.markdown("##### 🍔 What You Ate")
col1, col2 = st.columns([3, 1])
col1.write(f"Beef meals ({burgers}x)")
col2.write(f"**{food['water_beef']:,} gal water**")
col1, col2 = st.columns([3, 1])
col1.write(f"Chicken meals ({chicken_meals}x)")
col2.write(f"**{food['water_chicken']:,} gal water**")
st.caption(
    f"🐄 Your meals alone used {food['total_water_food']:,} gallons of water this week."
)

st.divider()

# Showers
st.markdown("##### 🚿 Showers")
col1, col2 = st.columns([3, 1])
col1.write(f"{showers_per_week} showers × {shower_minutes} min")
col2.write(f"**{water['shower_gallons']:.0f} gal**")
st.caption(f"💧 That's enough to fill {water['bathtubs']} bathtubs.")

st.divider()

# Energy
st.markdown("##### ❄️ Home Energy")
col1, col2 = st.columns([3, 1])
col1.write(f"AC ({ac_hours} hrs)")
col2.write(f"**${energy['ac_cost']:.2f}**")
col1, col2 = st.columns([3, 1])
col1.write(f"Phantom devices ({devices_left_on} plugged in)")
col2.write(f"**${energy['phantom_cost']:.2f}**")
st.caption(f"🔌 = {energy['charger_equiv']} phone chargers left plugged in all month.")

st.divider()

# Totals
st.markdown(
    f"""
<div class="receipt-total">
    💸 Weekly Cost to You: ${total_cost:.2f} &nbsp;|&nbsp; 💰 That's ${total_cost * 52:,.0f}/year<br>
    💧 Total Water Used: {total_water:,.0f} gallons<br>
    🕐 Time Lost to Traffic: {driving["hours_in_traffic"]} hrs this week
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# Savings / behavior change
st.markdown("#### 🌱 Small Swaps, Real Savings")
st.markdown(
    f"""
<div class="receipt-savings">
✅ Replace <b>30% of driving</b> with transit or walking → save <b>${savings["saved_drive"]:.2f}/week</b> (${savings["saved_drive_yearly"]:.0f}/year)<br><br>
✅ Swap <b>half your beef meals</b> for chicken → save <b>{savings["saved_water_food"]:,.0f} gallons</b> of water/week<br><br>
✅ Cut your <b>shower by {savings["shower_minutes_cut"]} min</b> → save <b>{savings["saved_shower"]:.0f} gallons</b> this week<br><br>
✅ Turn <b>AC down 25%</b> → save <b>${savings["saved_ac"]:.2f}/week</b> (${savings["saved_ac_yearly"]:.0f}/year)
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="receipt-tagline">
    Data sourced from EPA, USDA & EIA &nbsp;|&nbsp; Not here to judge. Just here to show you the math. 🧾
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ── save & export buttons ──────────────────────────────────────────────────────
st.markdown("#### 💾 Save This Receipt")

col_pdf, col_json = st.columns(2)

# JSON — lightweight, safe to generate every render
with col_json:
    single_receipt = {
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
    st.download_button(
        label="📋 Download JSON",
        data=json.dumps(single_receipt, indent=2),
        file_name=f"guilt_receipt_{date.today().strftime('%Y-%m-%d')}.json",
        mime="application/json",
        use_container_width=True,
    )

# PDF — generated lazily only when the button is clicked, avoiding
# MediaFileStorageError that occurs when blobs are pre-generated on every render
with col_pdf:
    if st.button("📄 Generate & Download PDF", use_container_width=True):
        pdf_buffer = generate_receipt_pdf(
            driving, food, water, energy, savings, total_cost, total_water, inputs
        )
        st.download_button(
            label="📥 Click here to save PDF",
            data=pdf_buffer,
            file_name=f"guilt_receipt_{date.today().strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="pdf_save",
        )

# ── full history section (only shown when history exists) ──────────────────────
if st.session_state.receipt_history:
    st.divider()
    st.markdown("#### 📋 Receipt History")
    col_dl, col_clr = st.columns([3, 1])
    with col_dl:
        st.download_button(
            label="💾 Export full history as JSON",
            data=export_history_json(),
            file_name="guilt_receipts.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_clr:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.receipt_history = []
            st.rerun()

    for i, receipt in enumerate(st.session_state.receipt_history):
        r = receipt["results"]
        inp = receipt.get("inputs", {})
        label = (
            f"🧾 {receipt['week_of']}  |  "
            f"${r['total_cost']:.2f} cost  |  "
            f"{r['total_water']:,.0f} gal water"
        )
        with st.expander(label, expanded=(i == 0)):
            st.caption(f"Saved at {receipt['saved_at']}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Weekly Cost", f"${r['total_cost']:.2f}")
            m2.metric("Water Used", f"{r['total_water']:,.0f} gal")
            m3.metric(
                "Traffic Hours", f"{r['driving'].get('hours_in_traffic', '—')} hrs"
            )
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
