"""
issue_tracker.py - Issue/CAPA aging + exception expiry monitor.

Produces:
  issue-aging.csv       open issues with state (OVERDUE / ESCALATE / On track)
  exception-expiry.csv  active exceptions expiring within 30 days or expired

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B9).

Governance rule: this only AGES and FLAGS items. It never closes an issue or
approves an exception - those stay human decisions.

Usage: python issue_tracker.py
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

# Days-left threshold at which an open issue is escalated, per severity:
ESCALATE_DAYS = {"Critical": 0, "High": 0, "Medium": 7, "Low": 14}   # CHANGE ME (optional)

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

if REGISTER_DIR and REGISTER_DIR != "." and "CHANGE_ME" not in REGISTER_DIR:
    os.chdir(REGISTER_DIR)


def aging():
    iss = load_register("issue-register.csv")
    rows = []
    for _, i in iss.iterrows():
        if i.Status == "Closed":
            continue
        dl = days_left(i.DueDate)
        is_overdue = dl < 0
        escalate = is_overdue or dl <= ESCALATE_DAYS.get(i.Severity, 7)
        rows.append({"IssueID": i.IssueID, "Title": i.Title, "Severity": i.Severity,
                     "Owner": i.Owner, "DueDate": i.DueDate, "DaysLeft": dl,
                     "State": "OVERDUE" if is_overdue else ("ESCALATE" if escalate else "On track")})
    report = pd.DataFrame(rows).sort_values("DaysLeft")
    report.to_csv("issue-aging.csv", index=False)
    print("== Issue aging ==")
    print(report.to_string(index=False))
    print("\nOverdue by severity:")
    print(report[report.State == "OVERDUE"].Severity.value_counts())


def expiry():
    exc = load_register("exception-register.csv")
    rows = []
    for _, e in exc[exc.Status == "Active"].iterrows():
        dl = days_left(e.ExpiryDate)
        if dl <= 30:
            rows.append({"ExceptionID": e.ExceptionID, "ControlID": e.ControlID,
                         "ExpiryDate": e.ExpiryDate, "DaysLeft": dl,
                         "State": "EXPIRED" if dl < 0 else "expiring",
                         "ApprovedBy": e.ApprovedBy})
    report = pd.DataFrame(rows).sort_values("DaysLeft") if rows else pd.DataFrame()
    report.to_csv("exception-expiry.csv", index=False)
    print("\n== Exceptions expiring/expired ==")
    print(report.to_string(index=False) if rows else "none within 30 days")


if __name__ == "__main__":
    aging()
    expiry()
