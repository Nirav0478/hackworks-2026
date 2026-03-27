from utils.constants import (
    COST_PER_MILE, MPG_AVERAGE, RIDESHARE_TRIP_AVG,
    WATER_PER_BURGER, WATER_PER_CHICKEN,
    WATER_PER_SHOWER_MIN,
    KWH_PER_AC_HOUR, ELECTRICITY_RATE, CHARGER_WATTS, HOURS_IN_WEEK
)


def calculate_driving(miles_driven, rideshare_trips):
    drive_cost     = miles_driven * COST_PER_MILE
    gas_gallons    = miles_driven / MPG_AVERAGE
    rideshare_cost = rideshare_trips * RIDESHARE_TRIP_AVG
    # rough estimate: 20% of driving time is traffic at 25mph avg
    hours_in_traffic = round((miles_driven / 25) * 0.20, 1)
    return {
        "drive_cost": drive_cost,
        "gas_gallons": gas_gallons,
        "rideshare_cost": rideshare_cost,
        "hours_in_traffic": hours_in_traffic,
    }


def calculate_food(burgers, chicken_meals):
    water_beef    = burgers * WATER_PER_BURGER
    water_chicken = chicken_meals * WATER_PER_CHICKEN
    return {
        "water_beef": water_beef,
        "water_chicken": water_chicken,
        "total_water_food": water_beef + water_chicken,
    }


def calculate_water(shower_minutes, showers_per_week):
    shower_gallons = shower_minutes * showers_per_week * WATER_PER_SHOWER_MIN
    return {
        "shower_gallons": shower_gallons,
        "bathtubs": round(shower_gallons / 330, 1),
    }


def calculate_energy(ac_hours, devices_left_on):
    ac_kwh        = ac_hours * KWH_PER_AC_HOUR
    ac_cost       = ac_kwh * ELECTRICITY_RATE
    phantom_kwh   = (devices_left_on * CHARGER_WATTS * HOURS_IN_WEEK) / 1000
    phantom_cost  = phantom_kwh * ELECTRICITY_RATE
    charger_equiv = int((ac_kwh + phantom_kwh) / (CHARGER_WATTS * 730 / 1000))
    return {
        "ac_kwh": ac_kwh,
        "ac_cost": ac_cost,
        "phantom_kwh": phantom_kwh,
        "phantom_cost": phantom_cost,
        "charger_equiv": charger_equiv,
    }


def calculate_savings(miles_driven, burgers, shower_minutes, showers_per_week, ac_hours):
    saved_drive  = (miles_driven * 0.30) * COST_PER_MILE
    saved_water_food = burgers * 0.5 * WATER_PER_BURGER
    saved_shower = max(0, (shower_minutes - 7) * showers_per_week * WATER_PER_SHOWER_MIN)
    saved_ac     = (ac_hours * 0.25) * KWH_PER_AC_HOUR * ELECTRICITY_RATE
    return {
        "saved_drive": saved_drive,
        "saved_drive_yearly": saved_drive * 52,
        "saved_water_food": saved_water_food,
        "saved_shower": saved_shower,
        "saved_ac": saved_ac,
        "saved_ac_yearly": saved_ac * 52,
        "shower_minutes_cut": max(0, shower_minutes - 7),
    }