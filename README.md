# 🧾 The Guilt Receipt

A week of your habits, handed back to you as a bill.

Enter your driving, food, water, and energy usage — the app converts it into real dollars, real gallons, and real hours of your life. No carbon math, no preachy stats. Just the actual cost of your week.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How the numbers work

All conversion factors are sourced from EPA, USDA, and DOE published data — hardcoded into the app as constants. No black box, no AI guessing. Just math on top of real research.

| Factor | Source | Value |
|--------|--------|-------|
| Cost per mile (driving) | IRS 2024 | $0.21/mile |
| Water per beef meal | USDA | 660 gal |
| Water per chicken meal | USDA | 330 gal |
| Water per shower minute | EPA | 2.1 gal/min |
| AC energy use | DOE avg | 1.5 kWh/hr |
| Electricity rate | EIA US avg | $0.13/kWh |

## Team

- Aditya — 
- Nirav — 
- Josh —