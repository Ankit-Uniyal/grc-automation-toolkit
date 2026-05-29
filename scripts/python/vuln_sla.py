"""
vuln_sla.py - Vulnerability SLA breach and aging report.

Reads vuln-register.csv (normalized by vuln_ingest.py) and reports open
vulnerabilities by severity and SLA state.

Usage:  python vuln_sla.py
Outputs: vuln-sla-report.csv
Requires: pandas, grclib
"""
import pandas as pd
from grclib import load_register, days_left


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
