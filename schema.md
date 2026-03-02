# `data/data.csv` Schema

`R_` and `B_` represent mirrored feature sets for red and blue fighters

## Targets

- `winner` (`categorical`) -> fight winner side (`red`, `blue`, `draw`)
- `win_type` (`categorical`) -> high-level result (`finish`, `decision`)
- `finish_type` (`categorical`) -> finish subtype when `win_type=finish` (`KO/TKO`, `SUB`)
- `decision_type` (`categorical`) -> decision subtype when `win_type=decision` (`unanimous`, `majority`, `split`)
- `last_round` (`int`) -> round number where fight ended

## Training Features

- `height` (`float`) -> fighter height in centimeters
- `reach` (`float`) -> fighter reach in inches
- `stance` (`categorical`) -> fighter stance (`Orthodox`, `Southpaw`, etc.)
- `age` (`int`) -> fighter age at fight date
- `title_bout` (`bool`) -> whether the bout is a title fight
- `format` (`int`) -> scheduled number of rounds
- `weight_class` (`categorical`) -> bout division label

## Pre-fight average feature families (`float`)

For each side (`R_` and `B_`), each stat has two columns:

- `<side>_avg_<stat>` -> fighter's own pre-fight average for that stat
- `<side>_avg_opp_<stat>` -> pre-fight average of opponents' values in that stat (strength-of-competition context)

Stats:

- `KD` -> knockdowns
- `SIG_STR_landed` -> significant strikes landed
- `SIG_STR_pct` -> significant strike accuracy percentage
- `total_STR_landed` -> total strikes landed
- `total_STR_pct` -> total strike accuracy percentage
- `TD_landed` -> takedowns landed
- `TD_pct` -> takedown accuracy percentage
- `SUB_ATT` -> submission attempts
- `REV` -> reversals
- `CTRL_time_seconds` -> control time in seconds
- `HEAD_STR_landed` -> significant head strikes landed
- `HEAD_STR_pct` -> head strike landed/attempted percentage
- `BODY_STR_landed` -> significant body strikes landed
- `BODY_STR_pct` -> body strike landed/attempted percentage
- `LEG_STR_landed` -> significant leg strikes landed
- `LEG_STR_pct` -> leg strike landed/attempted percentage
- `DISTANCE_STR_landed` -> significant distance strikes landed
- `DISTANCE_STR_pct` -> distance strike landed/attempted percentage
- `CLINCH_STR_landed` -> significant clinch strikes landed
- `CLINCH_STR_pct` -> clinch strike landed/attempted percentage
- `GND_STR_landed` -> significant ground strikes landed
- `GND_STR_pct` -> ground strike landed/attempted percentage

## Cumulative pre-fight counters

- `current_lose_streak` (`int`) -> current consecutive losses entering the fight
- `current_win_streak` (`int`) -> current consecutive wins entering the fight
- `draws` (`int`) -> career draw count before current fight
- `wins` (`int`) -> career win count before current fight
- `losses` (`int`) -> career loss count before current fight
- `total_time_fought_seconds` (`int`) -> total prior fight time in seconds
- `total_title_bouts` (`int`) -> number of title bouts before current fight
- `win_by_MD` (`int`) -> prior wins by majority decision
- `win_by_SD` (`int`) -> prior wins by split decision
- `win_by_UD` (`int`) -> prior wins by unanimous decision
- `win_by_KO/TKO` (`int`) -> prior wins by KO/TKO
- `win_by_SUB` (`int`) -> prior wins by submission
