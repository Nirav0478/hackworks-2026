"""
Quick sanity checks on the calculator logic.
Run with: python test_calculator.py
"""

import sys

sys.path.insert(0, ".")

from utils.calculator import (
    calculate_driving,
    calculate_energy,
    calculate_food,
    calculate_savings,
    calculate_water,
)

PASS = "✅"
FAIL = "❌"


def check(name, condition):
    status = PASS if condition else FAIL
    print(f"  {status} {name}")
    return condition


print("\n── Driving ──────────────────────────────")
d = calculate_driving(100, 3)
check("drive_cost = 100 * 0.21 = $21.00", abs(d["drive_cost"] - 21.00) < 0.01)
check("gas_gallons = 100 / 28 ≈ 3.57", abs(d["gas_gallons"] - 3.571) < 0.01)
check("rideshare_cost = 3 * $14 = $42.00", abs(d["rideshare_cost"] - 42.00) < 0.01)
check("hours_in_traffic > 0", d["hours_in_traffic"] > 0)
check("zero miles → zero cost", calculate_driving(0, 0)["drive_cost"] == 0)

print("\n── Food ─────────────────────────────────")
f = calculate_food(4, 5)
check("water_beef = 4 * 660 = 2640 gal", f["water_beef"] == 2640)
check("water_chicken = 5 * 330 = 1650 gal", f["water_chicken"] == 1650)
check("total_water_food = 4290 gal", f["total_water_food"] == 4290)
check("zero meals → zero water", calculate_food(0, 0)["total_water_food"] == 0)

print("\n── Water ────────────────────────────────")
w = calculate_water(10, 7)
check(
    "shower_gallons = 10 * 7 * 2.1 = 147 gal", abs(w["shower_gallons"] - 147.0) < 0.01
)
check("bathtubs > 0", w["bathtubs"] > 0)
check(
    "1 min shower, 1 shower → 2.1 gal",
    abs(calculate_water(1, 1)["shower_gallons"] - 2.1) < 0.01,
)

print("\n── Energy ───────────────────────────────")
e = calculate_energy(40, 5)
check("ac_kwh = 40 * 1.5 = 60 kWh", abs(e["ac_kwh"] - 60.0) < 0.01)
check("ac_cost = 60 * 0.13 = $7.80", abs(e["ac_cost"] - 7.80) < 0.01)
check("phantom_kwh > 0", e["phantom_kwh"] > 0)
check("phantom_cost > 0", e["phantom_cost"] > 0)
check("charger_equiv > 0", e["charger_equiv"] > 0)
check("zero AC → zero ac_cost", calculate_energy(0, 0)["ac_cost"] == 0)

print("\n── Savings ──────────────────────────────")
s = calculate_savings(100, 4, 10, 7, 40)
check("saved_drive > 0", s["saved_drive"] > 0)
check(
    "saved_drive_yearly = saved_drive * 52",
    abs(s["saved_drive_yearly"] - s["saved_drive"] * 52) < 0.01,
)
check("saved_water_food > 0", s["saved_water_food"] > 0)
check("saved_shower > 0 (10 min > 7 min target)", s["saved_shower"] > 0)
check(
    "shower at 5 min → saved_shower = 0",
    calculate_savings(0, 0, 5, 7, 0)["saved_shower"] == 0,
)
check(
    "saved_ac_yearly = saved_ac * 52",
    abs(s["saved_ac_yearly"] - s["saved_ac"] * 52) < 0.01,
)

print("\n── Edge Cases ───────────────────────────")
check(
    "all zeros → no crashes",
    (
        calculate_driving(0, 0) is not None
        and calculate_food(0, 0) is not None
        and calculate_water(0, 0) is not None
        and calculate_energy(0, 0) is not None
    ),
)

print("\nAll done.\n")
