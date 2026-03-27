import pandas as pd
import streamlit as st
from datetime import date

from utils.calculator import (
    calculate_driving,
    calculate_energy,
    calculate_food,
    calculate_savings,
    calculate_water,
)
from utils.pdf_generator import generate_receipt_pdf

st.set_page_config(page_title="The Guilt Receipt", page_icon="🧾", layout="centered")

st.markdown("""
<style>
    /* clean up default streamlit padding */
    .block-container { padding-top: 2rem; }

    .badge {
        background: #1e1b3a;
        border-left: 3px solid #7c6af7;
        padding: 8px 14px;
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 16px;
        color: #ccc;
    }
    .receipt-total {
        background: #1a1a1a;
        color: #f0f0f0;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        padding: 20px;
        border-radius: 6px;
        line-height: 2;
        letter-spacing: 0.3px;
    }
    .savings-box {
        background: #0f2d1a;
        border-left: 3px solid #2e7d32;
        padding: 14px 18px;
        border-radius: 4px;
        font-size: 14px;
        color: #c8e6c9;
        line-height: 2;
    }
    .footer-note {
        text-align: center;
        font-size: 11px;
        color: #555;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.title("The Guilt Receipt")
st.markdown("*Enter a week of your habits. We'll hand you the bill.*")

st.markdown("""
<div class="badge">
    Built for college students and young renters who want to make smarter choices — without the climate guilt trip.
</div>
""", unsafe_allow_html=True)

st.divider()

# inputs
st.subheader("Getting Around")
miles_driven = st.slider("Miles driven this week", 0, 500, 80)
rideshare_trips = st.number_input("Rideshare trips (Uber/Lyft) this week", 0, 30, 2)

st.subheader("What You Ate")
burgers = st.slider("Beef meals this week", 0, 21, 4)
chicken_meals = st.slider("Chicken meals this week", 0, 21, 5)

st.subheader("Showers")
shower_minutes = st.slider("Average shower length (minutes)", 1, 30, 10)
showers_per_week = st.slider("Showers per week", 0, 14, 7)

st.subheader("Home Energy")
ac_hours = st.slider("Hours AC ran this week", 0, 168, 40)
devices_left_on = st.number_input("Devices/chargers left plugged in when not in use", 0, 20, 5)

st.divider()

# run the numbers
driving = calculate_driving(miles_driven, rideshare_trips)
food = calculate_food(burgers, chicken_meals)
water = calculate_water(shower_minutes, showers_per_week)
energy = calculate_energy(ac_hours, devices_left_on)
savings = calculate_savings(miles_driven, burgers, shower_minutes, showers_per_week, ac_hours)

total_cost = driving["drive_cost"] + driving["rideshare_cost"] + energy["ac_cost"] + energy["phantom_cost"]
total_water = water["shower_gallons"] + food["total_water_food"]

tab1, tab2 = st.tabs(["My Receipt", "How I Compare"])

with tab1:
    st.markdown(f"### Your Receipt")
    st.caption(f"Week of {date.today().strftime('%B %d, %Y')}  —  updates as you adjust the sliders above.")

    st.markdown("**Getting Around**")
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
    st.caption(f"That's {driving['hours_in_traffic']} hours you'll never get back.")

    st.divider()

    st.markdown("**What You Ate**")
    col1, col2 = st.columns([3, 1])
    col1.write(f"Beef meals ({burgers}x)")
    col2.write(f"**{food['water_beef']:,} gal water**")
    col1, col2 = st.columns([3, 1])
    col1.write(f"Chicken meals ({chicken_meals}x)")
    col2.write(f"**{food['water_chicken']:,} gal water**")
    st.caption(f"Your meals alone used {food['total_water_food']:,} gallons of water this week.")

    st.divider()

    st.markdown("**Showers**")
    col1, col2 = st.columns([3, 1])
    col1.write(f"{showers_per_week} showers x {shower_minutes} min")
    col2.write(f"**{water['shower_gallons']:.0f} gal**")
    st.caption(f"That's enough to fill {water['bathtubs']} bathtubs.")

    st.divider()

    st.markdown("**Home Energy**")
    col1, col2 = st.columns([3, 1])
    col1.write(f"AC ({ac_hours} hrs)")
    col2.write(f"**${energy['ac_cost']:.2f}**")
    col1, col2 = st.columns([3, 1])
    col1.write(f"Phantom devices ({devices_left_on} plugged in)")
    col2.write(f"**${energy['phantom_cost']:.2f}**")
    st.caption(f"= {energy['charger_equiv']} phone chargers left plugged in all month.")

    st.divider()

    st.markdown(f"""
    <div class="receipt-total">
        Weekly Cost to You: ${total_cost:.2f} &nbsp;|&nbsp; That's ${total_cost * 52:,.0f} / year<br>
        Total Water Used: {total_water:,.0f} gallons<br>
        Time Lost to Traffic: {driving['hours_in_traffic']} hrs
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### Small Swaps, Real Savings")
    st.markdown(f"""
    <div class="savings-box">
        Replace 30% of driving with transit &rarr; save <b>${savings['saved_drive']:.2f}/week</b> (${savings['saved_drive_yearly']:.0f}/year)<br>
        Swap half your beef meals for chicken &rarr; save <b>{savings['saved_water_food']:,.0f} gallons</b> of water/week<br>
        Cut your shower by {savings['shower_minutes_cut']} min &rarr; save <b>{savings['saved_shower']:.0f} gallons</b> this week<br>
        Turn AC down 25% &rarr; save <b>${savings['saved_ac']:.2f}/week</b> (${savings['saved_ac_yearly']:.0f}/year)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-note">
        Data sourced from EPA, USDA & EIA &nbsp;|&nbsp; Not here to judge. Just here to show you the math.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

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
    pdf = generate_receipt_pdf(driving, food, water, energy, savings, total_cost, total_water, inputs)
    st.download_button(
        label="Download My Receipt as PDF",
        data=pdf,
        file_name=f"guilt_receipt_{date.today().strftime('%Y-%m-%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with tab2:
    import plotly.graph_objects as go

    st.markdown("### How I Compare")
    st.caption("Adjust the sliders above and come back here to see how you stack up against the average American.")

    # weekly US averages — FHWA, USDA, EPA, DOE
    avg_drive_cost = 0.21 * 238
    avg_food_water = 660 * 4.5
    avg_shower_gals = 2.1 * 8 * 7
    avg_energy_cost = 1.5 * 56 * 0.13 + (5 * 5 * 168 / 1000) * 0.13

    your_drive_cost = driving["drive_cost"] + driving["rideshare_cost"]
    your_food_water = food["total_water_food"]
    your_shower_gals = water["shower_gallons"]
    your_energy_cost = energy["ac_cost"] + energy["phantom_cost"]

    # colors: you = purple, avg = muted grey
    YOU_COLOR = "#7c6af7"
    AVG_COLOR = "#4a4a5a"

    def comparison_chart(your_val, avg_val, unit):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["You"],
            y=[your_val],
            marker_color=YOU_COLOR,
            name="You",
            text=[f"{your_val:,.1f} {unit}"],
            textposition="outside",
            textfont=dict(color="#cccccc", size=13),
        ))
        fig.add_trace(go.Bar(
            x=["Avg American"],
            y=[avg_val],
            marker_color=AVG_COLOR,
            name="Avg American",
            text=[f"{avg_val:,.1f} {unit}"],
            textposition="outside",
            textfont=dict(color="#cccccc", size=13),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=30, b=10, l=0, r=0),
            height=260,
            yaxis=dict(
                showgrid=True,
                gridcolor="#2a2a2a",
                tickfont=dict(color="#888"),
                zeroline=False,
            ),
            xaxis=dict(
                tickfont=dict(color="#ccc", size=13),
            ),
            bargap=0.4,
        )
        return fig

    st.markdown("**Weekly Driving Cost**")
    st.plotly_chart(comparison_chart(round(your_drive_cost, 2), round(avg_drive_cost, 2), "$"), use_container_width=True)
    diff = your_drive_cost - avg_drive_cost
    st.caption(f"You spend ${abs(diff):.2f} {'more' if diff > 0 else 'less'} than the average American on driving each week." + ("" if diff > 0 else " Nice."))

    st.divider()

    st.markdown("**Weekly Food Water Usage**")
    st.plotly_chart(comparison_chart(round(your_food_water), round(avg_food_water), "gal"), use_container_width=True)
    diff = your_food_water - avg_food_water
    st.caption(f"Your food choices use {abs(diff):,.0f} {'more' if diff > 0 else 'fewer'} gallons of water than the average American.")

    st.divider()

    st.markdown("**Weekly Shower Water Usage**")
    st.plotly_chart(comparison_chart(round(your_shower_gals), round(avg_shower_gals), "gal"), use_container_width=True)
    diff = your_shower_gals - avg_shower_gals
    st.caption(f"You use {abs(diff):.0f} {'more' if diff > 0 else 'fewer'} gallons in the shower than the average American per week.")

    st.divider()

    st.markdown("**Weekly Home Energy Cost**")
    st.plotly_chart(comparison_chart(round(your_energy_cost, 2), round(avg_energy_cost, 2), "$"), use_container_width=True)
    diff = your_energy_cost - avg_energy_cost
    st.caption(f"You spend ${abs(diff):.2f} {'more' if diff > 0 else 'less'} on home energy than the average American per week.")

    st.divider()
    st.caption("Averages sourced from FHWA, USDA, EPA WaterSense, DOE & EIA.")