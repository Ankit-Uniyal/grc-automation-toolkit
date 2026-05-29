"""
incident_monitor.py - SLA timers and regulatory breach-clock monitor for incidents.

Run frequently during an active incident (e.g. every 15-30 min via Task Scheduler).
Writes incident-alerts.csv and prints alerts for the IR lead / DPO.

Usage:  python incident_monitor.py
Requires: pandas, grclib

NOTE: This tracks timers and reminds humans. Declaring a breach and notifying a
regulator is a human/legal decision - never automate the notification itself.
"""
import pandas as pd
from datetime import datetime
from grclib import load_register

SLA_HOURS = {
    "Critical": {"ack": 1, "contain": 4, "resolve": 24},
    "High":     {"ack": 4, "contain": 12, "resolve": 72},
    "Medium":   {"ack": 8, "contain": 48, "resolve": 168},
    "Low":      {"ack": 24, "contain": 96, "resolve": 336},
}


def hrs(a, b):
    return (pd.to_datetime(b) - pd.to_datetime(a)).total_seconds() / 3600


def main():
    inc = load_register("incident-register.csv")
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
