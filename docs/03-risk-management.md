# 03 · Risk Management Automation

> **Pillar:** Risk. A risk register on a shared drive rots fast — scores go stale, treatments are never followed up, and the heatmap is rebuilt by hand before every board meeting. Automate the math and the chasing; keep the judgment human.

---

## 1. What to automate

- **Scoring** — compute inherent and residual risk from likelihood × impact, consistently.
- **Heatmap & dashboard** — regenerate the risk matrix automatically.
- **Treatment tracking** — flag overdue mitigation actions and owners.
- **Aging & review** — surface risks not reviewed within their cadence.
- **Roll-ups** — summarize by category, owner, business unit for reporting.

## 2. Data model — `risk-register.csv`

| Column | Notes |
|---|---|
| RiskID | RISK-014 |
| Title | Ransomware via phishing |
| Category | Cyber / Operational / Compliance |
| Owner | IT Manager |
| Likelihood | 1–5 |
| Impact | 1–5 |
| InherentScore | = Likelihood × Impact (auto) |
| ControlIDs | CTRL-AC-001; CTRL-AW-003 |
| ResidualLikelihood | 1–5 (post-control) |
| ResidualImpact | 1–5 |
| ResidualScore | auto |
| Treatment | Mitigate / Accept / Transfer / Avoid |
| ActionDueDate | 2026-06-30 |
| Status | Open / In Progress / Closed |
| LastReviewed | 2026-04-01 |
| ReviewFrequencyMonths | 6 |

## 3. The automation

### 3a. Scoring + heatmap generator (Python)

```python
# scripts/python/risk_engine.py
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("risk-register.csv")
df["InherentScore"] = df.Likelihood * df.Impact
df["ResidualScore"] = df.ResidualLikelihood * df.ResidualImpact

def band(s):
    if s >= 15: return "Critical"
    if s >= 8:  return "High"
    if s >= 4:  return "Medium"
    return "Low"
df["ResidualBand"] = df.ResidualScore.apply(band)
df.to_csv("risk-register-scored.csv", index=False)

# 5x5 heatmap of residual risk counts
grid = np.zeros((5,5), dtype=int)
for _, r in df.iterrows():
    grid[5-int(r.ResidualImpact), int(r.ResidualLikelihood)-1] += 1
plt.imshow(grid, cmap="RdYlGn_r")
plt.colorbar(label="Number of risks")
plt.xlabel("Likelihood"); plt.ylabel("Impact")
plt.xticks(range(5), range(1,6)); plt.yticks(range(5), range(5,0,-1))
for i in range(5):
    for j in range(5):
        if grid[i,j]: plt.text(j, i, grid[i,j], ha="center", va="center")
plt.title("Residual Risk Heatmap")
plt.tight_layout(); plt.savefig("risk-heatmap.png", dpi=120)
print(df.ResidualBand.value_counts())
```

Drop `risk-heatmap.png` straight into your board deck — no manual matrix building.

### 3b. Overdue treatment chaser (PowerShell)

```powershell
# scripts/powershell/Get-OverdueRiskActions.ps1
param([string]$RegisterPath = "\\fileserver\GRC\02_Risk\risk-register.csv")
$today = Get-Date
Import-Csv $RegisterPath |
  Where-Object { $_.Status -ne 'Closed' -and [datetime]$_.ActionDueDate -lt $today } |
  Select-Object RiskID, Title, Owner, ActionDueDate, Treatment |
  Sort-Object ActionDueDate
```

Pipe the result into the same Outlook reminder pattern from `docs/02` to nudge each owner.

### 3c. Review-aging check

```powershell
Import-Csv $RegisterPath | ForEach-Object {
  $due = ([datetime]$_.LastReviewed).AddMonths([int]$_.ReviewFrequencyMonths)
  if ($due -lt (Get-Date)) { "$($_.RiskID) review overdue (due $($due.ToString('yyyy-MM-dd')))" }
}
```

### 3d. Excel + Power Query (no-code dashboard)

For analysts who prefer Excel:
1. **Data → Get Data → From Text/CSV** → load `risk-register.csv`.
2. Add custom columns for InherentScore and ResidualScore in Power Query.
3. Build a **PivotTable + PivotChart** for the heatmap and category roll-ups.
4. **Data → Refresh All** (or set *Refresh on open*) regenerates everything from the latest CSV.

This gives non-coders a self-refreshing dashboard tied to the same source of truth.

## 4. Linking risk to controls

`ControlIDs` ties each risk to the controls that mitigate it (see `docs/04`). A small join lets you answer "if CTRL-AC-001 fails its test, which risks just became under-treated?" — invaluable for board reporting and the Statement of Applicability.

```python
risks = pd.read_csv("risk-register.csv")
failed_control = "CTRL-AC-001"
affected = risks[risks.ControlIDs.str.contains(failed_control, na=False)]
print(affected[["RiskID","Title","ResidualScore"]])
```

## 5. Scheduling & ownership

- **Owner:** Risk Manager.
- Run `risk_engine.py` **nightly/weekly** (writes scored CSV + heatmap to `02_Risk`).
- Run overdue/aging checks **weekly**, email owners.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Scoring | Manual formulas | Auto-scored + banded nightly |
| Heatmap | Hand-built | Auto-generated PNG/dashboard |
| Treatment | Manual follow-up | Auto overdue detection + owner nudges |
| Linkage | None | Risk↔control join for impact analysis |

**Next:** `docs/04-control-testing.md`
