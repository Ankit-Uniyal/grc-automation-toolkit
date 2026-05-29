# 16 · Internal Audit Management

> **Pillar:** Independent assurance. This pillar automates the audit universe, risk-based audit planning, sampling, and finding management — the internal-audit lifecycle — distinct from the always-on *audit readiness* in docs/08.

---

## 1. What to automate

- **Audit universe** — auditable entities scored by risk to drive the plan.
- **Risk-based plan** — auto-rank what to audit and when.
- **Reproducible sampling** — defensible, seed-based sample selection.
- **Workpaper indexing** — consistent structure and completeness checks.
- **Finding management** — push findings straight into the issue/CAPA register.

## 2. Data model — `audit-universe.csv`

| Column | Notes |
|---|---|
| EntityID | AU-009 |
| Entity | Access management process |
| RiskScore | 1-25 (inherent) |
| LastAuditDate | 2024-11-01 |
| AuditFrequencyMonths | 24 |
| Regulated | Yes / No |
| Owner | Process owner |

## 3. The automation

### 3a. Risk-based audit plan (Python, uses grclib)

```python
# scripts/python/audit_plan.py
import pandas as pd
from grclib import load_register, next_due, days_left

au = load_register("audit-universe.csv")
rows = []
for _, e in au.iterrows():
    due = next_due(e.LastAuditDate, int(e.AuditFrequencyMonths))
    # Priority = risk, boosted if regulated or overdue
    priority = float(e.RiskScore)
    if str(e.get("Regulated")) == "Yes":
        priority += 5
    if days_left(due) < 0:
        priority += 5
    rows.append({"EntityID": e.EntityID, "Entity": e.Entity, "RiskScore": e.RiskScore,
                 "NextAuditDue": due, "DaysToDue": days_left(due),
                 "PlanPriority": round(priority, 1)})
plan = pd.DataFrame(rows).sort_values("PlanPriority", ascending=False)
plan.to_csv("audit-plan.csv", index=False)
print(plan.to_string(index=False))
```

### 3b. Reproducible sampling

```python
# scripts/python/audit_sample.py
import pandas as pd
import sys

population = pd.read_csv(sys.argv[1])          # e.g. all change records
n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
sample = population.sample(n=min(n, len(population)), random_state=seed)
sample.to_csv("audit-sample.csv", index=False)
print(f"Selected {len(sample)} of {len(population)} (seed={seed}, reproducible)")
```

A fixed seed lets you prove the sample was not cherry-picked.

### 3c. Workpaper completeness (PowerShell)

```powershell
# Each engagement folder must contain the standard workpapers
$required = 'planning','riskassessment','testing','findings','report'
Get-ChildItem "\\fileserver\GRC\07_Audits" -Directory | ForEach-Object {
  $files = (Get-ChildItem $_.FullName -File).Name -join ' '
  $missing = $required | Where-Object { $files -notmatch $_ }
  if ($missing) { "INCOMPLETE: $($_.Name) missing -> $($missing -join ', ')" }
}
```

### 3d. Finding -> issue register

Each audit finding is appended to `issue-register.csv` (docs/15) with `Source=Audit`, so corrective actions are tracked in the same engine as everything else and never live only in a PDF report.

## 4. Scheduling & ownership

- **Owner:** Internal Audit (independent of control owners).
- Plan refresh **quarterly**; workpaper checks **per engagement**; finding sync **at report issuance**.

## 5. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Universe | None | Risk-scored auditable entities |
| Plan | Calendar-based | Risk-based auto-prioritized |
| Sampling | Manual | Reproducible seeded |
| Findings | Trapped in reports | Synced to central CAPA |

**Next:** `docs/17-vulnerability-management.md`
