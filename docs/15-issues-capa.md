# 15 · Issues, Exceptions & Corrective Actions (CAPA)

> **Pillar:** Closing the loop. Findings from audits, control failures, incidents, and risk assessments all generate *actions* - and those actions are where programs quietly fail. This pillar centralizes issues, exceptions/waivers, and corrective/preventive actions, then automates aging, escalation, and expiry.

---

## 1. What to automate

- **Unified issue/finding register** - one place for findings from any source.
- **Corrective & Preventive Action (CAPA)** tracking to closure.
- **Exception/waiver lifecycle** - risk-accepted deviations with **mandatory expiry**.
- **Aging & overdue escalation** - by severity and owner.
- **Root-cause and recurrence** analysis.

## 2. Data models

`issue-register.csv`

| Column | Notes |
|---|---|
| IssueID | ISS-031 |
| Source | Audit / Control test / Incident / Risk / Self-identified |
| SourceRef | AUD-2026-1 / CTRL-BK-001 / INC-2026-014 |
| Title | Backups not tested for payroll |
| Severity | Critical / High / Medium / Low |
| Owner | IT Manager |
| RootCause | text |
| ActionPlan | text |
| DueDate | 2026-06-30 |
| Status | Open / In Progress / Closed / Overdue |
| ClosedDate | |
| LinkedRisk | RISK-004 |

`exception-register.csv`

| Column | Notes |
|---|---|
| ExceptionID | EXC-007 |
| ControlID | CTRL-BK-001 |
| Reason | Compensating control in place |
| RiskAccepted | text |
| ApprovedBy | CISO |
| ApprovalDate | 2026-03-01 |
| ExpiryDate | 2026-09-01 (MANDATORY) |
| Status | Active / Expired / Withdrawn |

## 3. The automation

### 3a. Issue aging & overdue escalation (Python, uses grclib)

```python
# scripts/python/issue_tracker.py
import pandas as pd
from grclib import load_register, days_left

ESCALATE_DAYS = {"Critical": 0, "High": 0, "Medium": 7, "Low": 14}

iss = load_register("issue-register.csv")
rows = []
for _, i in iss.iterrows():
    if i.Status == "Closed":
        continue
    dl = days_left(i.DueDate)
    overdue = dl < 0
    escalate = overdue or dl <= ESCALATE_DAYS.get(i.Severity, 7)
    rows.append({"IssueID": i.IssueID, "Title": i.Title, "Severity": i.Severity,
                 "Owner": i.Owner, "DueDate": i.DueDate, "DaysLeft": dl,
                 "State": "OVERDUE" if overdue else ("ESCALATE" if escalate else "On track")})
report = pd.DataFrame(rows).sort_values("DaysLeft")
report.to_csv("issue-aging.csv", index=False)
print(report.to_string(index=False))
print("\nOverdue by severity:")
print(report[report.State == "OVERDUE"].Severity.value_counts())
```

### 3b. Exception expiry monitor (Python)

```python
# scripts/python/exception_monitor.py
import pandas as pd
from grclib import load_register, days_left

exc = load_register("exception-register.csv")
for _, e in exc[exc.Status == "Active"].iterrows():
    dl = days_left(e.ExpiryDate)
    if dl <= 30:
        flag = "EXPIRED" if dl < 0 else f"expires in {dl}d"
    print(f"{e.ExceptionID} ({e.ControlID}) -> {flag} | approved by {e.ApprovedBy}")
```

> **Why mandatory expiry matters:** an exception without an expiry is a permanent hole. Forcing re-approval keeps risk acceptance honest. The monitor chases owners before expiry via `Send-GrcNotification`.

### 3c. Recurrence analysis

Group issues by `RootCause` / `SourceRef` to find repeat offenders - the same control failing every quarter signals a systemic problem, not a one-off.

## 4. The hub of the toolkit

This register is the **convergence point**: control failures (docs/04), incidents (docs/12), BCM gaps (docs/13), audit findings (docs/16), and risk treatments (docs/03) all create issues here. One overdue-action report covers the whole program.

## 5. Scheduling & ownership

- **Owner:** GRC Manager (register), action owners (closure).
- Aging + escalation **weekly**; exception expiry **weekly**; recurrence review **monthly**.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Issues | Per-source lists | Unified register, all sources |
| CAPA | Forgotten | Aging + auto escalation |
| Exceptions | Permanent holes | Mandatory expiry + re-approval chase |
| Learning | None | Recurrence / root-cause analysis |

**Next:** `docs/16-internal-audit.md`
