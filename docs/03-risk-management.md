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

> [!TIP]
> **Script:** [`scripts/python/risk_engine.py`](../scripts/python/risk_engine.py) — scores the register (inherent + residual), bands each risk, writes `risk-register-scored.csv`, and renders `risk-heatmap.png` for your board deck. Edit its `CHANGE ME` block, then run `python risk_engine.py`.

Drop `risk-heatmap.png` straight into your board deck — no manual matrix building.

### 3b. Overdue treatment chaser (PowerShell)

> [!TIP]
> **Script:** [`scripts/powershell/Get-OverdueRiskActions.ps1`](../scripts/powershell/Get-OverdueRiskActions.ps1) — reports treatment actions past their `ActionDueDate` **and** risks past their review cadence (`LastReviewed` + `ReviewFrequencyMonths`). Add `-Notify` to draft Outlook reminders to each owner. Edit its `CHANGE ME` block first.

Pipe the result into the same Outlook reminder pattern from `docs/02` to nudge each owner.

### 3c. Review-aging check

Review-aging (risks not reviewed within `ReviewFrequencyMonths`) is handled by the same script as the overdue chaser above — see [`Get-OverdueRiskActions.ps1`](../scripts/powershell/Get-OverdueRiskActions.ps1), which reports both in one pass.

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
- Run `risk_engine.py` **nightly/weekly** (writes scored CSV + heatmap to `registers`).
- Run overdue/aging checks **weekly**, email owners.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Scoring | Manual formulas | Auto-scored + banded nightly |
| Heatmap | Hand-built | Auto-generated PNG/dashboard |
| Treatment | Manual follow-up | Auto overdue detection + owner nudges |
| Linkage | None | Risk↔control join for impact analysis |

**Next:** `docs/04-control-testing.md`
