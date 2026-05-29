# 13 · Business Continuity & Disaster Recovery (BCM/DR)

> **Pillar:** Resilience. BCM/DR programs decay quietly: BIAs go stale, RTO/RPO targets drift from reality, and test exercises slip. This pillar automates the BIA register, RTO/RPO tracking, and DR/BCP test scheduling and evidence.

---

## 1. What to automate

- **Business Impact Analysis (BIA) register** - processes, criticality, RTO/RPO, dependencies.
- **RTO/RPO vs. capability** - flag where recovery targets exceed proven capability.
- **DR/BCP test calendar** - schedule and chase tabletop/failover exercises.
- **Test evidence & after-action tracking** - capture results and corrective actions.
- **Dependency mapping** - link critical processes to assets and vendors.

## 2. Data model - `bia-register.csv`

| Column | Notes |
|---|---|
| ProcessID | BP-007 |
| Process | Payroll run |
| Owner | HR Manager |
| Criticality | Critical / High / Medium / Low |
| RTO_Hours | recovery time objective |
| RPO_Hours | recovery point objective |
| ProvenRTO_Hours | last tested actual |
| DependencyAssets | AST-002;AST-005 |
| DependencyVendors | VEN-001 |
| LastTested | 2026-02-15 |
| TestFrequencyMonths | 12 |
| NextTest | auto |

## 3. The automation

### 3a. RTO/RPO capability gap + test-due report (Python, uses grclib)

```python
# scripts/python/bcm_monitor.py
import pandas as pd
from grclib import load_register, next_due, days_left

bia = load_register("bia-register.csv")
rows = []
for _, p in bia.iterrows():
    nxt = next_due(p.LastTested, int(p.TestFrequencyMonths))
    gap = ""
    if pd.notna(p.get("ProvenRTO_Hours")) and str(p.ProvenRTO_Hours).strip():
        if float(p.ProvenRTO_Hours) > float(p.RTO_Hours):
            gap = f"RTO GAP: proven {p.ProvenRTO_Hours}h > target {p.RTO_Hours}h"
    rows.append({
        "ProcessID": p.ProcessID, "Process": p.Process, "Criticality": p.Criticality,
        "NextTest": nxt, "DaysToTest": days_left(nxt), "CapabilityGap": gap,
    })
report = pd.DataFrame(rows).sort_values("DaysToTest")
report.to_csv("bcm-status.csv", index=False)
print(report.to_string(index=False))
```

### 3b. Dependency roll-up

Join BIA dependencies to the asset and vendor registers to answer "if VEN-001 fails, which critical processes are affected and what are their RTOs?"

```python
import pandas as pd
from grclib import load_register, split_refs

bia = load_register("bia-register.csv")
target_vendor = "VEN-001"
hit = bia[bia.DependencyVendors.fillna("").apply(lambda v: target_vendor in split_refs(v))]
print(hit[["ProcessID","Process","Criticality","RTO_Hours"]].to_string(index=False))
```

## 4. Test scheduling & evidence

- The test-due report feeds `Send-GrcNotification` to remind process owners.
- After each exercise, file the after-action report in `07_Audits` or a dedicated `BCM` folder using the naming convention, and update `ProvenRTO_Hours` and `LastTested` so the capability gap recomputes automatically.
- Corrective actions go to the issue/CAPA register (`docs/15`).

## 5. Scheduling & ownership

- **Owner:** BCM Coordinator / Operations.
- Capability + test-due report **monthly**; BIA review **annually** (or after major change).

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| BIA | Static document | Living register with RTO/RPO |
| Capability | Assumed | Proven-vs-target gap flags |
| Testing | Slips silently | Auto test calendar + reminders |
| Dependencies | Tribal knowledge | Process↔asset↔vendor roll-up |

**Next:** `docs/14-change-management.md`
