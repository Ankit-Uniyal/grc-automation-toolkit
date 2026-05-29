# 19 · Data Protection & Privacy

> **Pillar:** Privacy governance. Privacy work is register- and deadline-heavy: the Record of Processing Activities (RoPA), DPIAs, data subject requests (DSARs) with statutory clocks, and retention enforcement. All of it automates well on a shared drive.

---

## 1. What to automate

- **RoPA / data inventory** — processing activities, lawful basis, data categories, locations, transfers.
- **DPIA workflow** — screening, tracking, and review of impact assessments.
- **DSAR tracking** — statutory deadline countdown (e.g. ~30-day windows under several regimes).
- **Retention enforcement** — flag data past its retention period for review.
- **Data-flow / transfer mapping** — where personal data lives and moves.

## 2. Data models

`ropa-register.csv`

| Column | Notes |
|---|---|
| ActivityID | RPA-014 |
| Activity | Payroll processing |
| Controller | Company |
| LawfulBasis | Contract / Consent / Legitimate interest |
| DataCategories | Identity, financial |
| DataSubjects | Employees |
| Recipients | VEN-001 |
| StorageLocation | AST-002 |
| RetentionMonths | 84 |
| CrossBorderTransfer | No / Yes (+ safeguard) |
| DPIARequired | Yes / No |

`dsar-register.csv`

| Column | Notes |
|---|---|
| RequestID | DSAR-2026-009 |
| Type | Access / Erasure / Rectification / Portability |
| ReceivedDate | 2026-05-15 |
| StatutoryDays | 30 |
| DueDate | auto |
| Status | Open / Fulfilled / Refused |
| Owner | DPO |

## 3. The automation

### 3a. DSAR deadline monitor (Python, uses grclib)

```python
# scripts/python/dsar_monitor.py
import pandas as pd
from grclib import load_register, next_due, days_left

d = load_register("dsar-register.csv")
for _, r in d[d.Status == "Open"].iterrows():
    due = next_due(r.ReceivedDate, 0)  # placeholder; compute below in days
```

(For day-based deadlines, compute `DueDate = ReceivedDate + StatutoryDays` directly:)

```python
import pandas as pd
from datetime import timedelta
from grclib import load_register, days_left

d = load_register("dsar-register.csv")
d["DueDate"] = (pd.to_datetime(d.ReceivedDate) + pd.to_timedelta(d.StatutoryDays, unit="D")).dt.date.astype(str)
open_d = d[d.Status == "Open"].copy()
open_d["DaysLeft"] = open_d.DueDate.apply(days_left)
open_d.sort_values("DaysLeft").to_csv("dsar-due.csv", index=False)
print(open_d[["RequestID","Type","DueDate","DaysLeft","Owner"]].to_string(index=False))
```

DSARs within 7 days (or overdue) trigger `Send-GrcNotification` to the DPO.

### 3b. Retention enforcement candidates (Python)

```python
# Flag processing activities whose data should be reviewed for deletion.
import pandas as pd
from grclib import load_register

ropa = load_register("ropa-register.csv")
print(ropa[["ActivityID","Activity","RetentionMonths","StorageLocation"]].to_string(index=False))
# Pair with the docs/01 stale-file scripts to find files older than RetentionMonths
# in each StorageLocation. Deletion is ALWAYS human-approved.
```

### 3c. DPIA screening & tracking

Maintain `dpia-register.csv` (DPIAID, ActivityID, ScreeningOutcome, Status, Reviewer, ReviewDate, NextReview). Auto-flag RoPA activities where `DPIARequired=Yes` but no DPIA exists — a compliance gap.

```python
ropa = load_register("ropa-register.csv")
dpia = load_register("dpia-register.csv")
have = set(dpia.ActivityID)
missing = ropa[(ropa.DPIARequired == "Yes") & (~ropa.ActivityID.isin(have))]
print("Activities needing a DPIA:\n", missing[["ActivityID","Activity"]].to_string(index=False))
```

## 4. Important guardrails

- Retention enforcement and DSAR **erasure** involve deletion — the toolkit **identifies candidates and tracks deadlines**, but the actual deletion is a human-approved action under your process.
- Never store the contents of DSAR responses (which contain personal data) in this register — keep only metadata and a link to the securely-stored response.

## 5. Scheduling & ownership

- **Owner:** DPO / Privacy Officer.
- DSAR monitor **daily**; RoPA review **annually**; DPIA gap check **quarterly**; retention review **quarterly**.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| RoPA | Static doc | Living register |
| DSAR | Manual diary | Auto statutory countdown |
| DPIA | Ad hoc | Auto gap detection |
| Retention | Never enforced | Candidate flagging (human deletes) |

**Next:** `docs/20-people-awareness-sod.md`
