# 11 · Multi-Framework Crosswalk

> **Pillar:** Compliance efficiency. The single biggest time-saver in GRC: **map your controls once, report against many frameworks.** This pillar builds a crosswalk so one control test simultaneously demonstrates ISO 27001, NIST CSF, SOC 2, PCI DSS, and GDPR coverage.

---

## 1. What to automate

- **Control-to-framework mapping** maintained in one place.
- **Per-framework coverage reports** generated automatically.
- **Gap detection** — framework requirements with no mapped control.
- **"Test once, satisfy many"** evidence reuse reporting.

## 2. Data model — `crosswalk.csv`

A long/tidy table: one row per (control, framework, clause).

| Column | Example |
|---|---|
| ControlID | CTRL-AC-001 |
| Framework | ISO27001 |
| Clause | A.8.2 |
| ClauseTitle | Privileged access rights |

This format scales: adding PCI DSS just means adding rows with `Framework=PCIDSS`.

## 3. The automation

### 3a. Build crosswalk + per-framework coverage (Python, uses grclib)

```python
# scripts/python/build_crosswalk.py
import pandas as pd
from grclib import load_register

cw = load_register("crosswalk.csv")
controls = load_register("control-matrix.csv")[["ControlID", "LastResult"]]
merged = cw.merge(controls, on="ControlID", how="left")

# Coverage per framework: which clauses have a passing control?
summary = (merged.assign(Passing=lambda d: d.LastResult.eq("Pass"))
                 .groupby("Framework")
                 .agg(Clauses=("Clause", "nunique"),
                      Controls=("ControlID", "nunique"),
                      PassingControls=("Passing", "sum"))
                 .reset_index())
summary.to_csv("framework-coverage-summary.csv", index=False)

# Reusable evidence: controls that satisfy 2+ frameworks
reuse = (merged.groupby("ControlID").Framework.nunique()
               .reset_index(name="FrameworksCovered")
               .query("FrameworksCovered >= 2")
               .sort_values("FrameworksCovered", ascending=False))
reuse.to_csv("control-reuse.csv", index=False)

print(summary.to_string(index=False))
print("\nHigh-leverage controls (satisfy multiple frameworks):")
print(reuse.to_string(index=False))
```

### 3b. Framework gap report

Supply a master clause list per framework (e.g. `iso27001-clauses.csv`) and diff against mapped clauses:

```python
import pandas as pd
from grclib import load_register

cw = load_register("crosswalk.csv")
master = load_register("iso27001-clauses.csv")   # all Annex A clauses
mapped = set(cw[cw.Framework == "ISO27001"].Clause)
gaps = master[~master.Clause.isin(mapped)]
gaps.to_csv("iso27001-gaps.csv", index=False)
print(f"{len(gaps)} ISO 27001 clauses have NO mapped control")
```

## 4. Seeding the crosswalk

The toolkit ships a starter `templates/crosswalk.csv` with common mappings across ISO 27001:2022, NIST CSF, SOC 2 TSC, PCI DSS v4, and GDPR. Extend it to your control set. Maintain it as your single mapping source — every coverage report derives from it.

> **Caveat:** crosswalks are interpretive. Treat auto-mappings as a **starting point** that a human compliance owner validates. Mappings are not legal equivalence.

## 5. Scheduling & ownership

- **Owner:** Compliance Manager.
- Regenerate coverage + reuse + gap reports **monthly** and before any certification/audit.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Mapping | Per-framework spreadsheets | Single tidy crosswalk |
| Coverage | Manual tallies | Auto per-framework summary |
| Efficiency | Re-test per framework | "Test once, satisfy many" reuse report |
| Gaps | Found at audit | Auto gap report vs. master clause list |

**Next:** `docs/12-incident-management.md`
