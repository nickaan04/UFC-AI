# UFC-AI

## What this project currently does

- Scrapes UFCStats event/fight data for fights from 2010 onward.
- Builds `data/raw_total_fight_data.csv` (one row per fight, red/blue fight stats + metadata).
  - Excludes: `referee`, `location`
- Builds `data/raw_fighter_details.csv` (one row per fighter with:
  `name`, `height_cm`, `weight_lbs`, `reach_in`, `stance`, `DOB`).

## Files

- `build_ufc_dataset.py`: End-to-end pipeline script.

## Install

```bash
pip install pandas numpy requests beautifulsoup4 tqdm
```

## Run

```bash
python3 build_ufc_dataset.py
```

## Output

- `data/raw_total_fight_data.csv`
- `data/raw_fighter_details.csv`