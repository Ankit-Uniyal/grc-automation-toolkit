"""
vuln_ingest.py - Normalize a vulnerability scanner export and assign severity-based SLAs.

Reads a raw scanner CSV (any vendor: Nessus, Qualys, OpenVAS, Defender, etc.), maps the
columns you care about into the toolkit's vuln-register.csv schema, derives Severity from
CVSS, and computes a remediation DueDate from the SLA table. The output feeds vuln_sla.py.

Governance: report / collect / track only. This script ingests and records scanner output.
It does NOT run the scanner and it does NOT apply patches - those are IT operations actions
under your change process.

Usage:
    python vuln_ingest.py <scanner-export.csv>

Convention: ../../CONVENTIONS.md   Walkthrough: ../../DIY-GUIDE.md
Edit the CHANGE ME block below before first run (Ctrl+F -> CHANGE_ME).
"""
import sys
import os
from datetime import date, timedelta
import pandas as pd

try:
    from grclib import save_register
except ImportError:  # allow running standalone
    def save_register(df, path):
        df.to_csv(path, index=False)

# vvv CHANGE ME vvv ---------------------------------------------------------
# Map your scanner's column names to the toolkit fields. Look at the header row
# of your export and put the matching column name on the right (keep the quotes).
COLUMN_MAP = {
    "VulnID":   "<<CHANGE_ME: CVE>>",       # CHANGE ME - scanner column holding the CVE / finding ID
    "Asset":    "<<CHANGE_ME: Host>>",      # CHANGE ME - scanner column holding the hostname / asset
    "CVSS":     "<<CHANGE_ME: CVSS>>",      # CHANGE ME - scanner column holding the CVSS base score
}

# Where to write the normalized register. "." = current working directory.
OUTPUT_REGISTER = "<<CHANGE_ME: vuln-register.csv>>"   # CHANGE ME

# Remediation SLA (calendar days) per severity band. Tune to your policy.
SLA_DAYS = {"Critical": 7, "High": 30, "Medium": 90, "Low": 180}   # CHANGE ME (optional)
# ^^^ CHANGE ME ^^^ ---------------------------------------------------------


def severity_from_cvss(score):
    """Map a CVSS base score (0-10) to a severity band."""
    try:
        c = float(score)
    except (TypeError, ValueError):
        return "Low"
    if c >= 9:
        return "Critical"
    if c >= 7:
        return "High"
    if c >= 4:
        return "Medium"
    return "Low"


def _pick(raw, wanted, fallback_index=None):
    """Return the requested column if present, else a positional fallback."""
    if wanted in raw.columns:
        return raw[wanted]
    if fallback_index is not None and raw.shape[1] > fallback_index:
        return raw.iloc[:, fallback_index]
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python vuln_ingest.py <scanner-export.csv>")
        sys.exit(1)

    src = sys.argv[1]
    if not os.path.exists(src):
        print("Scanner export not found:", src)
        sys.exit(1)

    raw = pd.read_csv(src)

    vuln_id = _pick(raw, COLUMN_MAP["VulnID"], 0)
    asset   = _pick(raw, COLUMN_MAP["Asset"], 1)
    cvss    = _pick(raw, COLUMN_MAP["CVSS"])
    if cvss is None:
        cvss = pd.Series([5.0] * len(raw))   # default mid score if not present

    out = pd.DataFrame({
        "VulnID": vuln_id,
        "Asset": asset,
        "CVSS": cvss,
    })
    out["Severity"] = out["CVSS"].apply(severity_from_cvss)
    out["FirstDetected"] = date.today().isoformat()
    out["SLA_Days"] = out["Severity"].map(SLA_DAYS)
    out["DueDate"] = out.apply(
        lambda r: (date.today() + timedelta(days=int(r["SLA_Days"]))).isoformat(),
        axis=1,
    )
    out["Status"] = "Open"
    out["RemediatedDate"] = ""

    save_register(out, OUTPUT_REGISTER)
    print("Wrote", len(out), "rows to", OUTPUT_REGISTER)
    print(out["Severity"].value_counts())


if __name__ == "__main__":
    main()
