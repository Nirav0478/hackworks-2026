# All conversion factors are sourced from EPA, USDA, and DOE published data.

# --- Driving ---
COST_PER_MILE        = 0.21    # IRS 2024 standard mileage rate ($/mile)
GAS_PRICE_PER_GALLON = 3.20    # US avg gas price
MPG_AVERAGE          = 28      # avg US passenger car fuel economy (EPA)
RIDESHARE_TRIP_AVG   = 14.00   # avg Uber/Lyft trip cost in USD
# --- Food & Water (USDA) ---
WATER_PER_BURGER = 660  # gallons per beef meal
WATER_PER_CHICKEN = 330  # gallons per chicken meal
WATER_PER_VEGGIE = 75   # gallons per vegetarian meal (avg of legumes/tofu/veg)

# --- Showers (EPA WaterSense) ---
WATER_PER_SHOWER_MIN = 2.1     # gallons per minute (standard showerhead)

# --- Home Energy (DOE / EIA) ---
KWH_PER_AC_HOUR      = 1.5     # avg window AC unit kWh/hr
ELECTRICITY_RATE     = 0.13    # US avg electricity rate $/kWh (EIA 2024)
CHARGER_WATTS        = 5       # watts a phone charger draws when left plugged in
HOURS_IN_WEEK        = 168
HOURS_PER_MONTH      = 730