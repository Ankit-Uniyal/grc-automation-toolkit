# 08 · Audit Readiness (Always-On Audit Binder)

> **Pillar:** Assurance & traceability. Audits become painful only when evidence and traceability are assembled reactively. If the previous pillars run on schedule, the audit binder is **already built** — this pillar is about wiring them together so you are perpetually audit-ready.

---

## 1. What to automate

- **Traceability matrix** — framework clause → control → policy → evidence, generated automatically.
- **Audit binder assembly** — collate current-period evidence per control into one structured pack.
- **Sampling** — pick random, reproducible samples for the auditor.
- **Gap & freshness reporting** — what is missing or stale before the auditor arrives.
- **PBC (Provided-By-Client) list tracking** — manage auditor requests and responses.

## 2. The master traceability matrix (Python)

This is the keystone report. It joins the registers from the other pillars into one auditor-friendly matrix.

```python
# scripts/python/build_traceability.py
import pandas as pd

controls = pd.read_csv("control-matrix.csv")     # ControlID, FrameworkRefs, EvidenceLink, LastResult...
policies = pd.read_csv("policy-register.csv")     # PolicyID, FrameworkRefs
risks    = pd.read_csv("risk-register.csv")        # RiskID, ControlIDs

# explode control framework refs to one row per clause
rows = []
for _, c in controls.iterrows():
    for ref in str(c.FrameworkRefs).split(";"):
        ref = ref.strip()
        if not ref: continue
        pol = policies[policies.FrameworkRefs.str.contains(ref, na=False)].PolicyID.tolist()
        rsk = risks[risks.ControlIDs.str.contains(c.ControlID, na=False)].RiskID.tolist()
        rows.append({
            "Clause": ref, "ControlID": c.ControlID, "ControlTitle": c.Title,
            "Policies": ";".join(pol), "Risks": ";".join(rsk),
            "LastResult": c.get("LastResult",""), "Evidence": c.get("EvidenceLink","")
        })
matrix = pd.DataFrame(rows).sort_values("Clause")
matrix.to_excel("traceability-matrix.xlsx", index=False)

# clauses with no mapped control = coverage gaps
print("Rows:", len(matrix), "| Controls failing:", (matrix.LastResult=="Fail").sum())
```

Hand the auditor `traceability-matrix.xlsx` and you have answered "show me how clause X is satisfied" for the whole framework in one file.

## 3. Audit binder assembly (PowerShell)

```powershell
# scripts/powershell/Build-AuditBinder.ps1
param(
  [string]$EvidenceRoot = "\\fileserver\GRC\04_Evidence\2026\Q2",
  [string]$BinderRoot   = "\\fileserver\GRC\07_Audits\2026_ExternalAudit"
)
$controls = Import-Csv "\\fileserver\GRC\03_Controls\control-matrix.csv"
foreach ($c in $controls) {
  $src = Join-Path $EvidenceRoot $c.ControlID
  $dst = Join-Path $BinderRoot   $c.ControlID
  if (Test-Path $src) {
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
    Copy-Item "$src\*" $dst -Recurse -Force
  } else {
    "BINDER GAP: no evidence for $($c.ControlID)"
  }
}
```

> Copy into the binder (read-only). Never move originals out of the write-once evidence store.

## 4. Reproducible sampling

Auditors love a defensible, random sample. Make it reproducible with a fixed seed so you can prove it was not cherry-picked:

```python
import pandas as pd
pop = pd.read_csv("users_2026-06-01.csv")     # e.g. sample 25 users for access testing
sample = pop.sample(n=25, random_state=42)     # fixed seed = reproducible
sample.to_csv("audit-sample-users.csv", index=False)
```

## 5. Freshness & gap dashboard

Before any audit, run one consolidated check:

```powershell
# Controls whose evidence is older than the period or missing
$controls = Import-Csv "\\fileserver\GRC\03_Controls\control-matrix.csv"
foreach ($c in $controls) {
  if ($c.LastResult -eq 'Fail') { "OPEN FAIL: $($c.ControlID)" }
  if ([datetime]$c.LastTested -lt (Get-Date).AddMonths(-6)) { "STALE TEST: $($c.ControlID) ($($c.LastTested))" }
}
```

## 6. PBC (auditor request) tracker

Maintain `pbc-list.csv` (RequestID, Description, Owner, DueDate, Status, ResponseLink). Reuse the overdue-chaser pattern from `docs/02` to keep responses on time during fieldwork — turning the usually-chaotic PBC scramble into a tracked workflow.

## 7. Scheduling & ownership

- **Owner:** GRC/Compliance Manager.
- Rebuild the traceability matrix and freshness report **monthly** (and on demand pre-audit); assemble the binder at audit kickoff.

## 8. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Traceability | Manual mapping doc | Auto matrix joining controls/policies/risks/evidence |
| Binder | Hand-collated | Scripted assembly with gap flags |
| Sampling | Manual pick | Reproducible seeded sampling |
| PBC | Email chain | Tracked list with auto-chase |

**Next:** `docs/09-implementation-roadmap.md`
