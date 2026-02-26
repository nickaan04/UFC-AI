"""
UFC raw data scraper (stage 1).

This script creates exactly two datasets:
1) data/raw_total_fight_data.csv   -> one row per fight (red/blue fight stats + fight metadata)
2) data/raw_fighter_details.csv    -> one row per fighter (name, height_cm, weight_lbs, reach_in, stance, DOB)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_TOTAL_FIGHTS_PATH = DATA_DIR / "raw_total_fight_data.csv"
RAW_FIGHTER_DETAILS_PATH = DATA_DIR / "raw_fighter_details.csv"


@dataclass
class FightStats:
    R_fighter: str
    B_fighter: str
    R_KD: Optional[int]
    B_KD: Optional[int]
    R_SIG_STR_landed: Optional[int]
    B_SIG_STR_landed: Optional[int]
    R_SIG_STR_pct: Optional[float]
    B_SIG_STR_pct: Optional[float]
    R_total_STR_landed: Optional[int]
    B_total_STR_landed: Optional[int]
    R_total_STR_pct: Optional[float]
    B_total_STR_pct: Optional[float]
    R_TD_landed: Optional[int]
    B_TD_landed: Optional[int]
    R_TD_pct: Optional[float]
    B_TD_pct: Optional[float]
    R_SUB_ATT: Optional[int]
    B_SUB_ATT: Optional[int]
    R_REV: Optional[int]
    B_REV: Optional[int]
    R_CTRL_time_seconds: Optional[int]
    B_CTRL_time_seconds: Optional[int]
    R_HEAD_STR_landed: Optional[int]
    B_HEAD_STR_landed: Optional[int]
    R_HEAD_STR_pct: Optional[float]
    B_HEAD_STR_pct: Optional[float]
    R_BODY_STR_landed: Optional[int]
    B_BODY_STR_landed: Optional[int]
    R_BODY_STR_pct: Optional[float]
    B_BODY_STR_pct: Optional[float]
    R_LEG_STR_landed: Optional[int]
    B_LEG_STR_landed: Optional[int]
    R_LEG_STR_pct: Optional[float]
    B_LEG_STR_pct: Optional[float]
    R_DISTANCE_STR_landed: Optional[int]
    B_DISTANCE_STR_landed: Optional[int]
    R_DISTANCE_STR_pct: Optional[float]
    B_DISTANCE_STR_pct: Optional[float]
    R_CLINCH_STR_landed: Optional[int]
    B_CLINCH_STR_landed: Optional[int]
    R_CLINCH_STR_pct: Optional[float]
    B_CLINCH_STR_pct: Optional[float]
    R_GND_STR_landed: Optional[int]
    B_GND_STR_landed: Optional[int]
    R_GND_STR_pct: Optional[float]
    B_GND_STR_pct: Optional[float]


class UFCRawDataScraper:
    EVENTS_URL = "http://ufcstats.com/statistics/events/completed?page=all"

    def __init__(self, start_year: int = 2010):
        self.start_year = start_year
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; UFC-AI-Scraper/1.0)"}
        )

    def _soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def run(self):
        fight_df = self.scrape_raw_total_fight_data()
        fight_df.to_csv(RAW_TOTAL_FIGHTS_PATH, sep=";", index=False)
        print(f"Saved {len(fight_df)} fights -> {RAW_TOTAL_FIGHTS_PATH}")

        fighters = sorted(
            set(fight_df["R_fighter"].dropna().tolist())
            | set(fight_df["B_fighter"].dropna().tolist())
        )
        fighter_df = self.scrape_raw_fighter_details(fighters)
        fighter_df.to_csv(RAW_FIGHTER_DETAILS_PATH, index=False)
        print(f"Saved {len(fighter_df)} fighters -> {RAW_FIGHTER_DETAILS_PATH}")

    # ----------------------
    # Fight-level scraping
    # ----------------------
    def scrape_raw_total_fight_data(self) -> pd.DataFrame:
        event_links = self._get_event_links()
        rows: List[Dict] = []

        for event_url in tqdm(event_links, desc="Events"):
            event_meta = self._get_event_meta(event_url)
            if event_meta is None:
                continue
            event_date, fight_links = event_meta
            if event_date.year < self.start_year:
                continue

            for fight_url in fight_links:
                row = self._scrape_single_fight(fight_url, event_date)
                if row is not None:
                    rows.append(row)

        # Explicit final column order.
        columns = [
            "R_fighter",
            "B_fighter",
            "R_KD",
            "B_KD",
            "R_SIG_STR_landed",
            "B_SIG_STR_landed",
            "R_SIG_STR_pct",
            "B_SIG_STR_pct",
            "R_total_STR_landed",
            "B_total_STR_landed",
            "R_total_STR_pct",
            "B_total_STR_pct",
            "R_TD_landed",
            "B_TD_landed",
            "R_TD_pct",
            "B_TD_pct",
            "R_SUB_ATT",
            "B_SUB_ATT",
            "R_REV",
            "B_REV",
            "R_CTRL_time_seconds",
            "B_CTRL_time_seconds",
            "R_HEAD_STR_landed",
            "B_HEAD_STR_landed",
            "R_HEAD_STR_pct",
            "B_HEAD_STR_pct",
            "R_BODY_STR_landed",
            "B_BODY_STR_landed",
            "R_BODY_STR_pct",
            "B_BODY_STR_pct",
            "R_LEG_STR_landed",
            "B_LEG_STR_landed",
            "R_LEG_STR_pct",
            "B_LEG_STR_pct",
            "R_DISTANCE_STR_landed",
            "B_DISTANCE_STR_landed",
            "R_DISTANCE_STR_pct",
            "B_DISTANCE_STR_pct",
            "R_CLINCH_STR_landed",
            "B_CLINCH_STR_landed",
            "R_CLINCH_STR_pct",
            "B_CLINCH_STR_pct",
            "R_GND_STR_landed",
            "B_GND_STR_landed",
            "R_GND_STR_pct",
            "B_GND_STR_pct",
            "method",
            "last_round",
            "format",
            "date",
            "winner",
            "title_bout",
            "weight_class",
        ]

        return pd.DataFrame(rows, columns=columns)

    def _get_event_links(self) -> List[str]:
        soup = self._soup(self.EVENTS_URL)
        links: List[str] = []
        for td in soup.find_all("td", {"class": "b-statistics__table-col"}):
            a = td.find("a")
            if a and a.get("href"):
                links.append(a["href"])
        return links

    def _get_event_meta(self, event_url: str) -> Optional[Tuple[datetime, List[str]]]:
        try:
            soup = self._soup(event_url)
        except Exception:
            return None

        info_nodes = soup.find_all("li", {"class": "b-list__box-list-item"})
        if len(info_nodes) < 1:
            return None

        date_text = info_nodes[0].get_text(" ", strip=True).replace("Date:", "").strip()
        event_date = pd.to_datetime(date_text, errors="coerce")
        if pd.isna(event_date):
            return None

        fight_links: List[str] = []
        for tr in soup.find_all(
            "tr",
            {
                "class": "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click"
            },
        ):
            href = tr.get("data-link")
            if href:
                fight_links.append(href)

        return event_date.to_pydatetime(), fight_links

    def _scrape_single_fight(
        self, fight_url: str, event_date: datetime
    ) -> Optional[Dict]:
        try:
            soup = self._soup(fight_url)
            fight_stats = self._parse_fight_stat_tables(soup)
            fight_meta = self._parse_fight_meta(soup)
            if fight_stats is None or fight_meta is None:
                return None

            row = {
                **fight_stats.__dict__,
                **fight_meta,
                "date": event_date.strftime("%Y-%m-%d"),
            }
            return row
        except Exception:
            return None

    def _parse_fight_stat_tables(self, soup: BeautifulSoup) -> Optional[FightStats]:
        tables = soup.find_all("tbody")
        if len(tables) < 3:
            return None

        # Table 0 (totals) and table 2 (Significant strike distribution) include the data we need.
        totals_row = tables[0].find("tr")
        SIG_row = tables[2].find("tr")
        if totals_row is None or SIG_row is None:
            return None

        totals = self._flatten_row_cells(totals_row)
        SIGs = self._flatten_row_cells(SIG_row)[6:]  # Skip duplicate identity columns.
        merged = totals + SIGs

        # These names mirror the canonical raw_total_fight_data layout.
        keys = [
            "R_fighter",
            "B_fighter",
            "R_KD",
            "B_KD",
            "R_SIG_STR",
            "B_SIG_STR",
            "R_SIG_STR_pct",
            "B_SIG_STR_pct",
            "R_TOTAL_STR",
            "B_TOTAL_STR",
            "R_TD",
            "B_TD",
            "R_TD_pct",
            "B_TD_pct",
            "R_SUB_ATT",
            "B_SUB_ATT",
            "R_REV",
            "B_REV",
            "R_CTRL",
            "B_CTRL",
            "R_HEAD",
            "B_HEAD",
            "R_BODY",
            "B_BODY",
            "R_LEG",
            "B_LEG",
            "R_DISTANCE",
            "B_DISTANCE",
            "R_CLINCH",
            "B_CLINCH",
            "R_GROUND",
            "B_GROUND",
        ]
        if len(merged) < len(keys):
            return None
        data = {keys[i]: merged[i].strip() for i in range(len(keys))}

        # Parse "x of y" style fields into landed and percentage.
        r_SIG_landed, r_SIG_attempted = self._parse_landed_attempted(data["R_SIG_STR"])
        b_SIG_landed, b_SIG_attempted = self._parse_landed_attempted(data["B_SIG_STR"])
        r_total_landed, r_total_attempted = self._parse_landed_attempted(data["R_TOTAL_STR"])
        b_total_landed, b_total_attempted = self._parse_landed_attempted(data["B_TOTAL_STR"])
        r_td_landed, r_td_attempted = self._parse_landed_attempted(data["R_TD"])
        b_td_landed, b_td_attempted = self._parse_landed_attempted(data["B_TD"])
        r_head_landed, r_head_attempted = self._parse_landed_attempted(data["R_HEAD"])
        b_head_landed, b_head_attempted = self._parse_landed_attempted(data["B_HEAD"])
        r_body_landed, r_body_attempted = self._parse_landed_attempted(data["R_BODY"])
        b_body_landed, b_body_attempted = self._parse_landed_attempted(data["B_BODY"])
        r_leg_landed, r_leg_attempted = self._parse_landed_attempted(data["R_LEG"])
        b_leg_landed, b_leg_attempted = self._parse_landed_attempted(data["B_LEG"])
        r_distance_landed, r_distance_attempted = self._parse_landed_attempted(
            data["R_DISTANCE"]
        )
        b_distance_landed, b_distance_attempted = self._parse_landed_attempted(
            data["B_DISTANCE"]
        )
        r_clinch_landed, r_clinch_attempted = self._parse_landed_attempted(data["R_CLINCH"])
        b_clinch_landed, b_clinch_attempted = self._parse_landed_attempted(data["B_CLINCH"])
        r_ground_landed, r_ground_attempted = self._parse_landed_attempted(data["R_GROUND"])
        b_ground_landed, b_ground_attempted = self._parse_landed_attempted(data["B_GROUND"])

        return FightStats(
            R_fighter=data["R_fighter"],
            B_fighter=data["B_fighter"],
            R_KD=self._to_int(data["R_KD"]),
            B_KD=self._to_int(data["B_KD"]),
            R_SIG_STR_landed=r_SIG_landed,
            B_SIG_STR_landed=b_SIG_landed,
            R_SIG_STR_pct=self._parse_pct(data["R_SIG_STR_pct"]),
            B_SIG_STR_pct=self._parse_pct(data["B_SIG_STR_pct"]),
            R_total_STR_landed=r_total_landed,
            B_total_STR_landed=b_total_landed,
            R_total_STR_pct=self._pct_from_counts(r_total_landed, r_total_attempted),
            B_total_STR_pct=self._pct_from_counts(b_total_landed, b_total_attempted),
            R_TD_landed=r_td_landed,
            B_TD_landed=b_td_landed,
            R_TD_pct=self._parse_pct(data["R_TD_pct"]),
            B_TD_pct=self._parse_pct(data["B_TD_pct"]),
            R_SUB_ATT=self._to_int(data["R_SUB_ATT"]),
            B_SUB_ATT=self._to_int(data["B_SUB_ATT"]),
            R_REV=self._to_int(data["R_REV"]),
            B_REV=self._to_int(data["B_REV"]),
            R_CTRL_time_seconds=self._time_to_seconds(data["R_CTRL"]),
            B_CTRL_time_seconds=self._time_to_seconds(data["B_CTRL"]),
            R_HEAD_STR_landed=r_head_landed,
            B_HEAD_STR_landed=b_head_landed,
            R_HEAD_STR_pct=self._pct_from_counts(r_head_landed, r_head_attempted),
            B_HEAD_STR_pct=self._pct_from_counts(b_head_landed, b_head_attempted),
            R_BODY_STR_landed=r_body_landed,
            B_BODY_STR_landed=b_body_landed,
            R_BODY_STR_pct=self._pct_from_counts(r_body_landed, r_body_attempted),
            B_BODY_STR_pct=self._pct_from_counts(b_body_landed, b_body_attempted),
            R_LEG_STR_landed=r_leg_landed,
            B_LEG_STR_landed=b_leg_landed,
            R_LEG_STR_pct=self._pct_from_counts(r_leg_landed, r_leg_attempted),
            B_LEG_STR_pct=self._pct_from_counts(b_leg_landed, b_leg_attempted),
            R_DISTANCE_STR_landed=r_distance_landed,
            B_DISTANCE_STR_landed=b_distance_landed,
            R_DISTANCE_STR_pct=self._pct_from_counts(
                r_distance_landed, r_distance_attempted
            ),
            B_DISTANCE_STR_pct=self._pct_from_counts(
                b_distance_landed, b_distance_attempted
            ),
            R_CLINCH_STR_landed=r_clinch_landed,
            B_CLINCH_STR_landed=b_clinch_landed,
            R_CLINCH_STR_pct=self._pct_from_counts(r_clinch_landed, r_clinch_attempted),
            B_CLINCH_STR_pct=self._pct_from_counts(b_clinch_landed, b_clinch_attempted),
            R_GND_STR_landed=r_ground_landed,
            B_GND_STR_landed=b_ground_landed,
            R_GND_STR_pct=self._pct_from_counts(r_ground_landed, r_ground_attempted),
            B_GND_STR_pct=self._pct_from_counts(b_ground_landed, b_ground_attempted),
        )

    def _parse_fight_meta(self, soup: BeautifulSoup) -> Optional[Dict]:
        details_block = soup.find("div", {"class": "b-fight-details__content"})
        if details_block is None:
            return None

        vals = []
        for p in details_block.find_all("p", {"class": "b-fight-details__text"}):
            txt = p.get_text(" ", strip=True)
            txt = txt.replace("Method:", "").replace("Round:", "")
            txt = txt.replace("Time:", "").replace("Time format:", "")
            txt = txt.replace("Referee:", "").strip()
            vals.append(txt)
        if len(vals) < 4:
            return None

        winner = ""
        for div in soup.find_all("div", {"class": "b-fight-details__person"}):
            status = div.find(
                "i",
                {
                    "class": "b-fight-details__person-status b-fight-details__person-status_style_green"
                },
            )
            if status is not None:
                h3 = div.find("h3", {"class": "b-fight-details__person-name"})
                if h3:
                    winner = h3.get_text(" ", strip=True)

        fight_title = soup.find("i", {"class": "b-fight-details__fight-title"})
        fight_type = fight_title.get_text(" ", strip=True) if fight_title else ""

        title_bout = "Title Bout" in fight_type
        weight_class = self._extract_weight_class(fight_type)
        if weight_class is None:
            return None

        return {
            "method": vals[0],
            "last_round": self._to_int(vals[1]),
            "format": vals[3],
            "winner": winner,
            "title_bout": title_bout,
            "weight_class": weight_class,
        }

    @staticmethod
    def _extract_weight_class(fight_type: str) -> Optional[str]:
        text = str(fight_type)
        known_classes = [
            "Women's Strawweight",
            "Women's Bantamweight",
            "Women's Featherweight",
            "Women's Flyweight",
            "Lightweight",
            "Welterweight",
            "Middleweight",
            "Light Heavyweight",
            "Heavyweight",
            "Featherweight",
            "Bantamweight",
            "Flyweight",
        ]
        for weight_class in known_classes:
            if weight_class in text:
                return weight_class
        if "Catch Weight" in text or "Catchweight" in text:
            return "Catchweight"
        return None

    @staticmethod
    def _flatten_row_cells(row) -> List[str]:
        values = []
        for td in row.find_all("td"):
            text = (
                td.get_text("\n", strip=True)
                .replace("\n", ",")
                .replace(", ", ",")
                .replace(" ,", ",")
            )
            values.append(text)
        return ",".join(values).split(",")

    @staticmethod
    def _to_int(value: str) -> Optional[int]:
        text = str(value).strip()
        if text in {"", "--", "---", "nan", "None"}:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None

    @staticmethod
    def _parse_pct(value: str) -> Optional[float]:
        text = str(value).strip()
        if text in {"", "--", "---", "nan", "None"}:
            return None
        text = text.replace("%", "")
        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _parse_landed_attempted(value: str) -> Tuple[Optional[int], Optional[int]]:
        text = str(value).strip().replace(" ", "")
        if "of" not in text:
            return None, None
        landed, attempted = text.split("of", maxsplit=1)
        try:
            return int(landed), int(attempted)
        except ValueError:
            return None, None

    @staticmethod
    def _pct_from_counts(
        landed: Optional[int], attempted: Optional[int]
    ) -> Optional[float]:
        if landed is None or attempted is None or attempted == 0:
            return None
        return round((landed / attempted) * 100.0, 2)

    @staticmethod
    def _time_to_seconds(value: str) -> Optional[int]:
        text = str(value).strip()
        if text in {"", "--", "---", "nan", "None"} or ":" not in text:
            return None
        mins, secs = text.split(":")
        try:
            return int(mins) * 60 + int(secs)
        except ValueError:
            return None

    # ----------------------
    # Fighter-level scraping
    # ----------------------
    def scrape_raw_fighter_details(self, fighters_needed: List[str]) -> pd.DataFrame:
        fighter_url_map = self._get_all_fighter_links()
        rows = []
        for name in tqdm(fighters_needed, desc="Fighters"):
            url = fighter_url_map.get(name)
            if not url:
                rows.append(
                    {
                        "name": name,
                        "height_cm": None,
                        "weight_lbs": None,
                        "reach_in": None,
                        "stance": None,
                        "DOB": None,
                    }
                )
                continue

            details = self._scrape_single_fighter(url)
            if details is None:
                rows.append(
                    {
                        "name": name,
                        "height_cm": None,
                        "weight_lbs": None,
                        "reach_in": None,
                        "stance": None,
                        "DOB": None,
                    }
                )
                continue

            rows.append({"name": name, **details})

        return pd.DataFrame(
            rows,
            columns=[
                "name",
                "height_cm",
                "weight_lbs",
                "reach_in",
                "stance",
                "DOB",
            ],
        )

    def _get_all_fighter_links(self) -> Dict[str, str]:
        fighter_links: Dict[str, str] = {}
        for ch in tqdm([chr(i) for i in range(ord("a"), ord("z") + 1)], desc="FighterIndex"):
            url = f"http://ufcstats.com/statistics/fighters?char={ch}&page=all"
            try:
                soup = self._soup(url)
            except Exception:
                continue
            table = soup.find("tbody")
            if table is None:
                continue

            names = table.find_all("a", {"class": "b-link b-link_style_black"}, href=True)
            fighter_name = ""
            for idx, item in enumerate(names):
                if (idx + 1) % 3 != 0:
                    first_or_last = item.get_text(strip=True)
                    fighter_name = (
                        first_or_last if fighter_name == "" else f"{fighter_name} {first_or_last}"
                    )
                else:
                    fighter_links[fighter_name] = item["href"]
                    fighter_name = ""

        return fighter_links

    def _scrape_single_fighter(self, fighter_url: str) -> Optional[Dict]:
        try:
            soup = self._soup(fighter_url)
        except Exception:
            return None

        items = soup.find_all(
            "li", {"class": "b-list__box-list-item b-list__box-list-item_type_block"}
        )
        if len(items) < 8:
            return None

        # The first profile block contains all core biographic fields.
        values = []
        for i, node in enumerate(items):
            if i == 9:
                # UFCStats includes one empty row in this segment.
                continue
            txt = node.get_text(" ", strip=True)
            txt = txt.replace("Height:", "").replace("Weight:", "")
            txt = txt.replace("Reach:", "").replace("STANCE:", "")
            txt = txt.replace("DOB:", "").strip()
            values.append(txt)
            if len(values) >= 5:
                break

        if len(values) < 5:
            return None

        height_raw, weight_raw, reach_raw, stance_raw, dob_raw = values
        return {
            "height_cm": self._height_to_cm(height_raw),
            "weight_lbs": self._weight_to_lbs(weight_raw),
            "reach_in": self._reach_to_inches(reach_raw),
            "stance": stance_raw if stance_raw not in {"", "--"} else None,
            "DOB": self._normalize_dob(dob_raw),
        }

    @staticmethod
    def _height_to_cm(height: str) -> Optional[float]:
        text = str(height).strip()
        if text in {"", "--", "nan", "None"}:
            return None
        if "'" in text:
            feet, inches = text.split("'")
            inches = inches.replace('"', "").strip()
            try:
                total_inches = int(feet) * 12 + int(inches)
                return round(total_inches * 2.54, 2)
            except ValueError:
                return None
        return None

    @staticmethod
    def _weight_to_lbs(weight: str) -> Optional[float]:
        text = str(weight).replace("lbs.", "").replace("lbs", "").strip()
        if text in {"", "--", "nan", "None"}:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _reach_to_inches(reach: str) -> Optional[float]:
        text = str(reach).replace('"', "").strip()
        if text in {"", "--", "nan", "None"}:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _normalize_dob(dob: str) -> Optional[str]:
        text = str(dob).strip()
        if text in {"", "--", "nan", "None"}:
            return None
        dt = pd.to_datetime(text, errors="coerce")
        if pd.isna(dt):
            return None
        return dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    scraper = UFCRawDataScraper(start_year=2010)
    scraper.run()
