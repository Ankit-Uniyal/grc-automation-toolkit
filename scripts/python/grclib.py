"""
grclib.py - Shared helpers for the GRC Automation Toolkit (Python side).

Reusable foundation so every Python automation behaves consistently:
    * Register I/O (load/save CSV)
    * Date helpers (next-due, days-left, overdue)
    * Reference splitting (semicolon-separated framework refs / control IDs)
    * SHA-256 hashing for evidence integrity
    * Simple run logging

Import:  from grclib import load_register, next_due, days_left, overdue
Requires: pandas
"""
from __future__ import annotations
import hashlib
import os
from datetime import date, datetime

import pandas as pd


def load_register(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Register not found: {path}")
    return pd.read_csv(path)


def save_register(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)


def split_refs(value) -> list[str]:
    return [r.strip() for r in str(value).split(";") if r and r.strip()]


def _parse(d) -> date:
    if isinstance(d, (datetime, date)):
        return d if isinstance(d, date) and not isinstance(d, datetime) else d.date() if isinstance(d, datetime) else d
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def next_due(last: str, frequency_months: int) -> str:
    base = _parse(last)
    month = base.month - 1 + int(frequency_months)
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, 28)
    return date(year, month, day).isoformat()


def days_left(due: str, as_of: date | None = None) -> int:
    as_of = as_of or date.today()
    return (_parse(due) - as_of).days


def overdue(due: str, as_of: date | None = None) -> bool:
    return days_left(due, as_of) < 0


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(message: str, log_dir: str = "logs") -> None:
    os.makedirs(log_dir, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"{stamp}  {message}"
    with open(os.path.join(log_dir, f"grc_{date.today().isoformat()}.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def band(score: int, thresholds=(15, 8, 4), labels=("Critical", "High", "Medium", "Low")) -> str:
    """Generic banding used by risk/vendor scoring."""
    for t, lbl in zip(thresholds, labels):
        if score >= t:
            return lbl
    return labels[-1]
