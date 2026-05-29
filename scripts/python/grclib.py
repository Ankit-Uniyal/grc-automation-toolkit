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
    """Load a CSV register into a DataFrame with friendly errors.

    Instead of a raw stack trace, this prints a clear, actionable message
    when the file is missing so a new analyst knows exactly what to fix.
    """
    if not os.path.exists(path):
        raise SystemExit(
            f"ERROR: register file not found: {path}"
            "\n  - Check the path is correct (see the CHANGE ME line in this script)."
            "\n  - Try the sample data in templates/ first, e.g. copy"
            " templates/risk-register.csv next to the script and re-run."
        )
    return pd.read_csv(path)


def require_columns(df: pd.DataFrame, required, name: str = "the register") -> None:
    """Fail with a clear message if expected columns are missing.

    Call this right after load_register so a column typo or wrong file gives
    a readable explanation instead of a pandas KeyError traceback.
    Example: require_columns(df, ["RiskID", "Likelihood", "Impact"], "risk register")
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        have = ", ".join(map(str, df.columns)) or "(none)"
        raise SystemExit(
            f"ERROR: {name} is missing required column(s): {', '.join(missing)}"
            f"\n  - Columns found in the file: {have}"
            "\n  - Fix the CSV header (check spelling/case) and re-run."
            "\n  - Compare against the matching sample file in templates/."
        )


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
