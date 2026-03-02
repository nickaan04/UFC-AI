# `data/data.csv` Schema

`R_` and `B_` represent mirrored feature sets for red and blue fighters

## Targets

- `winner` (`categorical`) --> red, blue, or draw
- `win_type` (`categorical`) --> finish or decision
- `finish_type` (`categorical`) --> KO/TKO or SUB
- `decision_type` (`categorical`) --> unanimous, majority, or split
- `last_round` (`int`)

## Training Features

- `height` (`float`)
- `reach` (`float`)
- `stance` (`categorical`)
- `age` (`float`)


- `title_bout` (`bool`)
- `format` (`int`)
- `weight_class` (`categorical`)

## Pre-fight average feature families (`float`)

For each side (`R_` and `B_`), each stat has two columns:

- `<side>_avg_<stat>`
- `<side>_avg_opp_<stat>`

Stats:

- `KD`
- `SIG_STR_landed`
- `SIG_STR_pct`
- `total_STR_landed`
- `total_STR_pct`
- `TD_landed`
- `TD_pct`
- `SUB_ATT`
- `REV`
- `CTRL_time_seconds`
- `HEAD_STR_landed`
- `HEAD_STR_pct`
- `BODY_STR_landed`
- `BODY_STR_pct`
- `LEG_STR_landed`
- `LEG_STR_pct`
- `DISTANCE_STR_landed`
- `DISTANCE_STR_pct`
- `CLINCH_STR_landed`
- `CLINCH_STR_pct`
- `GND_STR_landed`
- `GND_STR_pct`

## Cumulative pre-fight counters

- `current_lose_streak` (`int`)
- `current_win_streak` (`int`)
- `draw` (`int`)
- `wins` (`int`)
- `losses` (`int`)
- `total_time_fought_seconds` (`int`)
- `total_title_bouts` (`int`)
- `win_by_MD` (`int`)
- `win_by_SD` (`int`)
- `win_by_UD` (`int`)
- `win_by_KO/TKO` (`int`)
- `win_by_SUB` (`int`)
