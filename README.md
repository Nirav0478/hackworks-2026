# The Guilt Receipt
Track your weekly driving, food, water, and energy usage and read it in an organized reciept!

## Features:
- Export as a PDF
- Compare your stats to the averages in the US
- Export/Import JSON files to keep a history

## [See it in action!](https://guiltreciept-hackworks2026.streamlit.app/)

...or you can run it locally like so:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## How the numbers work

All conversion factors are sourced from EPA, USDA, and DOE published data hardcoded into the app as constants.

| Factor | Source | Value |
|--------|--------|-------|
| Cost per mile (driving) | IRS 2024 | $0.21/mile |
| Water per beef meal | USDA | 660 gal |
| Water per chicken meal | USDA | 330 gal |
| Water per shower minute | EPA | 2.1 gal/min |
| AC energy use | DOE avg | 1.5 kWh/hr |
| Electricity rate | EIA US avg | $0.13/kWh |

## Team

- Aditya - Designed frontend and .pdf export. Curated project demo.
- Nirav - Repo owner and project manager. Assisted other team members with any problems.
- Josh - Designed history and .json import/export features.
