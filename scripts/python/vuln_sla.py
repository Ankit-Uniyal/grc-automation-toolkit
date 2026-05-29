"""
vuln_sla.py - Vulnerability SLA breach and aging report.

Reads vuln-register.csv (normalized by vuln_ingest.py) and reports open
vulnerabilities by severity and SLA state.

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B8).

Governance rule: this only REPORTS SLA state. It never patches or closes a
vulnerability - remediation stays a human action.

Usage: python vuln_sla.py
Outputs: vuln-sla-report.csv
Requires: pandas, grclib
"""
import os
import pandas as pd
from grclib import load_register, days_left

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Folder that holds your live register CSVs. Replace the token (keep quotes).
# Leave as "." if you run this from inside your registers folder.
# ----------------------------------------------------------------------------

REGISTER_DIR = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\registers>>"   # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

if REGISTER_DIR and REGISTER_DIR != "." and "CHANGE_ME" not in REGISTER_DIR:
    os.chdir(REGISTER_DIR)


def main():
    v = load_register("vuln-register.csv")
    open_v = v[v.Status == "Open"].copy()
    open_v["DaysLeft"] = open_v.DueDate.apply(days_left)
    open_v["SLA_State"] = open_v.DaysLeft.apply(lambda d: "BREACHED" if d < 0 else "On track")
    open_v.sort_values("DaysLeft").to_csv("vuln-sla-report.csv", index=False)
    print("Open vulnerabilities by severity:")
    print(open_v.Severity.value_counts())
    breached = open_v[open_v.SLA_State == "BREACHED"]
    print(f"\nSLA breached: {len(breached)}")
    if len(breached):
        print(breached[["VulnID", "Asset", "Severity", "DueDate", "DaysLeft"]].to_string(index=False))


if __name__ == "__main__":
    main()
