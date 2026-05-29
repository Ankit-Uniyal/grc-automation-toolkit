# 12 · Incident Management & Breach-Clock Tracking

> **Pillar:** Operational resilience. When an incident hits, the GRC-critical questions are: is it a reportable breach, what is the regulatory clock, and is the response on track? This pillar automates incident logging, SLA/breach-clock tracking, and post-incident review follow-up.

---

## 1. What to automate

- **Incident register** with severity, timestamps, and status.
- **SLA timers** - acknowledge/contain/resolve targets by severity.
- **Breach-clock** - if reportable, count down the regulatory notification deadline (e.g. 72-hour windows under several regimes).
- **Escalation** - alert when SLA or breach deadlines approach.
- **Post-incident review (PIR)** tracking and corrective-action linkage.

## 2. Data model - `incident-register.csv`

| Column | Notes |
|---|---|
| IncidentID | INC-2026-014 |
| Title | Phishing - credential compromise |
| Severity | Critical / High / Medium / Low |
| DetectedAt | 2026-05-20T09:15 |
| AcknowledgedAt | timestamp |
| ContainedAt | timestamp |
| ResolvedAt | timestamp |
| Reportable | Yes / No / TBD |
| BreachClockStart | when the regulatory clock started |
| NotificationDeadlineHours | 72 |
| Status | Open / Contained / Resolved / Closed |
| Owner | IR Lead |
| LinkedIssueID | ISS-031 (CAPA) |

## 3. The automation

### 3a. SLA & breach-clock monitor (Python, uses grclib)

```python
# scripts/python/incident_monitor.py
import pandas as pd
from datetime import datetime
from grclib import load_register

SLA_HOURS = {"Critical": {"ack": 1, "contain": 4, "resolve": 24},
             "High": {"ack": 4, "contain": 12, "resolve": 72},
             "Medium": {"ack": 8, "contain": 48, "resolve": 168},
             "Low": {"ack": 24, "contain": 96, "resolve": 336}}

def hrs(a, b):
    return (pd.to_datetime(b) - pd.to_datetime(a)).total_seconds() / 3600

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
    # breach clock
    if str(r.get("Reportable")) == "Yes" and pd.notna(r.get("BreachClockStart")):
        deadline_h = float(r.get("NotificationDeadlineHours", 72))
        used = hrs(r.BreachClockStart, now)
        remaining = deadline_h - used
        if remaining <= 24:
            alerts.append((r.IncidentID, f"BREACH NOTIFICATION due in {round(remaining,1)}h", round(used, 1)))

pd.DataFrame(alerts, columns=["IncidentID", "Alert", "Hours"]).to_csv("incident-alerts.csv", index=False)
for a in alerts:
    print(a)
```

Run this **frequently during an active incident** (e.g. every 15-30 min via Task Scheduler) and pipe `incident-alerts.csv` to `Send-GrcNotification` for the IR lead and (for breach clocks) the DPO.

### 3b. Metrics: MTTR / MTTD

```python
inc = load_register("incident-register.csv")
inc["TTD_h"] = (pd.to_datetime(inc.AcknowledgedAt) - pd.to_datetime(inc.DetectedAt)).dt.total_seconds()/3600
inc["TTR_h"] = (pd.to_datetime(inc.ResolvedAt) - pd.to_datetime(inc.DetectedAt)).dt.total_seconds()/3600
print(inc.groupby("Severity")[["TTD_h","TTR_h"]].mean().round(1))
```

## 4. Post-incident review & corrective actions

When an incident is resolved, auto-create a PIR checklist file in `08_Incidents/<IncidentID>/` and open a row in the **issue/CAPA register** (`docs/15`) so root-cause actions are tracked to closure rather than forgotten.

> **Important:** the toolkit tracks timers and reminds humans. The decision to declare a breach and notify a regulator is a **human/legal judgment** - never automate the notification itself.

## 5. Scheduling & ownership

- **Owner:** Incident Response Lead; **Breach decisions:** DPO/Legal.
- Monitor **continuously during incidents**; metrics report **monthly**.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Logging | Email/ticket | Structured incident register |
| SLA | Manual watch | Auto SLA timers + alerts |
| Breach clock | Mental math | Auto countdown + 24h warning |
| Learning | Forgotten | PIR + CAPA tracked to closure |

**Next:** `docs/13-business-continuity.md`
