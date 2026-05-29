# 21 · Metrics, KRIs/KPIs & Management Review

> **Pillar:** Governance oversight. Leadership needs a single, trustworthy view of GRC health, and standards like ISO 27001 require a documented **management review**. This pillar aggregates metrics from every other pillar into KRIs/KPIs and auto-generates the management-review and board pack.

---

## 1. What to automate

- **Metric collection** - pull headline numbers from each pillar's register.
- **KRI/KPI dashboard** - thresholds with RAG (red/amber/green) status.
- **Trend tracking** - store monthly snapshots to show direction.
- **Management-review pack** - assemble the standing agenda inputs automatically.
- **Board summary** - one page of the numbers that matter.

## 2. Example KRIs/KPIs (define yours in `kri-register.csv`)

| Metric | Source pillar | Green | Amber | Red |
|---|---|---|---|---|
| Overdue control tests | docs/04 | 0 | 1-3 | 4+ |
| Critical risks (residual) | docs/03 | 0 | 1-2 | 3+ |
| Overdue CAPA actions | docs/15 | 0 | 1-5 | 6+ |
| Expired exceptions | docs/15 | 0 | 1 | 2+ |
| SLA-breached vulns (Critical/High) | docs/17 | 0 | 1-5 | 6+ |
| Training completion % | docs/20 | >=95 | 85-94 | <85 |
| Overdue obligations/filings | docs/10 | 0 | 1 | 2+ |
| Open audit findings (High+) | docs/16 | 0 | 1-2 | 3+ |

## 3. The automation

### 3a. Metrics aggregator (Python, uses grclib)

```python
# scripts/python/grc_metrics.py
import pandas as pd
from datetime import date
from grclib import load_register, days_left, overdue

def safe(fn, default=0):
    try: return fn()
    except Exception: return default

metrics = {}
# Controls overdue
ctl = safe(lambda: load_register("control-matrix.csv"), pd.DataFrame())
metrics["overdue_control_tests"] = safe(
    lambda: int(ctl[ctl.NextTestDate.notna()].NextTestDate.apply(overdue).sum()))
# Critical residual risks
rk = safe(lambda: load_register("risk-register.csv"), pd.DataFrame())
metrics["critical_residual_risks"] = safe(
    lambda: int(((rk.ResidualLikelihood * rk.ResidualImpact) >= 15).sum()))
# Overdue CAPA
iss = safe(lambda: load_register("issue-register.csv"), pd.DataFrame())
metrics["overdue_capa"] = safe(
    lambda: int(iss[iss.Status != "Closed"].DueDate.apply(overdue).sum()))

def rag(value, green, amber):
    if value <= green: return "GREEN"
    if value <= amber: return "AMBER"
    return "RED"

THRESH = {"overdue_control_tests": (0, 3), "critical_residual_risks": (0, 2), "overdue_capa": (0, 5)}
rows = []
for k, v in metrics.items():
    g, a = THRESH.get(k, (0, 999))
    rows.append({"Metric": k, "Value": v, "Status": rag(v, g, a), "AsOf": date.today().isoformat()})
out = pd.DataFrame(rows)
out.to_csv("grc-metrics.csv", index=False)
# Append to history for trends
out.to_csv("grc-metrics-history.csv", mode="a", header=False, index=False)
print(out.to_string(index=False))
```

### 3b. Management-review pack assembler (Python)

```python
# scripts/python/management_review_pack.py  -- builds a Markdown pack from the standing agenda
from datetime import date
from grclib import load_register

m = load_register("grc-metrics.csv")
lines = [f"# Management Review Pack - {date.today().isoformat()}", ""]
lines.append("## 1. KRI/KPI dashboard")
for _, r in m.iterrows():
    lines.append(f"- **{r.Metric}**: {r.Value} ({r.Status})")
lines += ["", "## 2. Standing agenda (ISO 27001 cl. 9.3 style)",
          "- Status of actions from previous reviews (docs/15)",
          "- Changes in internal/external issues",
          "- Feedback on security performance (metrics above)",
          "- Results of audits (docs/16) and risk assessment (docs/03)",
          "- Opportunities for improvement"]
with open(f"management-review-{date.today().isoformat()}.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Wrote management review pack")
```

### 3c. Excel / Power Query dashboard

For a self-refreshing visual dashboard, load `grc-metrics-history.csv` via **Data → Get Data → From Text/CSV**, build PivotCharts for trend lines and a RAG summary, and set **Refresh on open**. See `templates/dashboards/README.md`.

## 4. Scheduling & ownership

- **Owner:** GRC Manager (reports to CISO/board).
- Metrics aggregation **monthly** (snapshot for trends); management-review pack **per review cycle** (quarterly/biannual); board summary **per board meeting**.

## 5. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Metrics | Hand-tallied | Auto-aggregated from all pillars |
| KRIs | None | RAG thresholds + trends |
| Mgmt review | Manual deck | Auto-assembled pack |
| Board | Ad hoc | Standing one-page summary |

**This completes the pillar set.** See `docs/09-implementation-roadmap.md` for rollout and the root `README.md` for the full map.
