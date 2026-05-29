"""
incident_monitor.py - SLA timers and regulatory breach-clock monitor for incidents.

Run frequently during an active incident (e.g. every 15-30 min via Task Scheduler).
Writes incident-alerts.csv and prints alerts for the IR lead / DPO.

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B7).

Governance rule: this tracks timers and reminds humans. Declaring a breach and
notifying a regulator is a human/legal decision - never automate the notification.

Usage: python incident_monitor.py
Requires: pandas, grclib
"""
import os
import pandas as pd
from datetime import datetime
from grclib import load_register, require_columns

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Folder that holds your live register CSVs. Replace the token (keep quotes).
# Leave as "." if you run this script from inside your registers folder
# (the daily orchestrator does that for you).
# ----------------------------------------------------------------------------

REGISTER_DIR = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\registers>>"   # CHANGE ME

# SLA hours per severity (optional - tune to your IR policy):
SLA_HOURS = {
    "Critical": {"ack": 1,  "contain": 4,  "resolve": 24},    # CHANGE ME (optional)
    "High":     {"ack": 4,  "contain": 12, "resolve": 72},    # CHANGE ME (optional)
    "Medium":   {"ack": 8,  "contain": 48, "resolve": 168},   # CHANGE ME (optional)
    "Low":      {"ack": 24, "contain": 96, "resolve": 336},   # CHANGE ME (optional)
}

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

if REGISTER_DIR and REGISTER_DIR != "." and "CHANGE_ME" not in REGISTER_DIR:
    os.chdir(REGISTER_DIR)


def hrs(a, b):
    return (pd.to_datetime(b) - pd.to_datetime(a)).total_seconds() / 3600


def main():
    inc = load_register("incident-register.csv")
    require_columns(inc, ["Status", "Severity", "DetectedAt"], "incident register")
    now = datetime.now()
    alerts = []
    for _, r in inc.iterrows():
        if r.Status in ("Resolved", "Closed"):
            continue
        sla = SLA_HOURS.get(r.Severity, SLA_HOURS["Medium"])
        elapsed = hrs(r.DetectedAt, now)
        if pd.isna(r.get("AcknowledgedAt")) and elapsed > sla["ack"]:
            alerts.append((r.IncidentID, "ACK SLA breached", round(elapsed, 1)))
        if pd.isna(r.get("ContainedAt")) and elapsed > sla["contain"]:
            alerts.append((r.IncidentID, "CONTAIN SLA breached", round(elapsed, 1)))
        if str(r.get("Reportable")) == "Yes" and pd.notna(r.get("BreachClockStart")):
            deadline_h = float(r.get("NotificationDeadlineHours", 72))
            used = hrs(r.BreachClockStart, now)
            remaining = deadline_h - used
            if remaining <= 24:
                alerts.append((r.IncidentID,
                               f"BREACH NOTIFICATION due in {round(remaining, 1)}h",
                               round(used, 1)))
    pd.DataFrame(alerts, columns=["IncidentID", "Alert", "Hours"]).to_csv("incident-alerts.csv", index=False)
    if alerts:
        for a in alerts:
            print("ALERT:", a)
    else:
        print("No SLA/breach-clock alerts.")


if __name__ == "__main__":
    main()
