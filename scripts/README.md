# Scripts Index

Runnable automation for the toolkit. Copy the CSV templates from `../templates` into your GRC share first, then point each script at your live registers (most Python scripts expect the CSVs in the current working directory).

## Shared engineering layer

| File | Purpose |
|---|---|
| `powershell/GrcToolkit.psm1` | Reusable PowerShell module: register I/O, logging, SHA-256, date helpers, Outlook notifications, evidence capture. `Import-Module ./GrcToolkit.psm1`. |
| `python/grclib.py` | Python helpers: load/save registers, date math (next-due/days-left/overdue), ref splitting, hashing, logging, banding. `from grclib import ...`. |
| `powershell/Invoke-GrcDailyRun.ps1` | Master orchestrator — runs the recurring PowerShell + Python jobs in one scheduled pass. |

## PowerShell (`powershell/`)

| Script | Purpose | Doc |
|---|---|---|
| `Send-ComplianceReminders.ps1` | Email testers about due/overdue control tests (`-WhatIf` supported). | 04 |
| `Invoke-EvidenceCollection.ps1` | Harvest technical evidence (AD, BitLocker, AV, firewall, patches), hash + manifest. | 05 |
| `Register-GrcTasks.ps1` | Register recurring jobs in Windows Task Scheduler under `svc-grc`. | 04 |
| `Invoke-GrcDailyRun.ps1` | Orchestrate the full daily/weekly run. | — |

Inline examples in the docs also cover folder scaffolding/drift (01), config baseline & drift (18), workpaper checks (16), and patch compliance (17).

## Python (`python/`)

| Script | Purpose | Doc |
|---|---|---|
| `risk_engine.py` | Score risk register + render heatmap PNG. | 03 |
| `build_traceability.py` | Clause→control→policy→risk→evidence matrix. | 08 |
| `build_uar_packs.py` | Per-manager access review packs + reconciliation. | 06 |
| `grc_metrics.py` | Aggregate KRIs/KPIs from all pillars into a RAG dashboard + history. | 21 |
| `issue_tracker.py` | Issue/CAPA aging + exception expiry monitor. | 15 |
| `incident_monitor.py` | Incident SLA timers + regulatory breach-clock. | 12 |
| `vuln_sla.py` | Vulnerability SLA breach + aging report. | 17 |
| `sod_check.py` | Segregation-of-duties conflict detection. | 20 |

Additional Python snippets in the docs (ready to lift into scripts): obligation coverage & compliance calendar (10), framework crosswalk (11), BCM monitor (13), change governance (14), audit plan & sampling (16), vuln ingest (17), DSAR monitor & DPIA gap (19), training compliance & phishing ingest (20), management-review pack (21).

## Power Automate Desktop (`power-automate/`)

No-code build recipes (PAD flows are binary objects, so we document the step list):

| Recipe | Purpose |
|---|---|
| `policy-review-reminder.flow.md` | Email policy owners when reviews are due. |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pandas numpy matplotlib openpyxl
# put grclib.py on PYTHONPATH or run scripts from scripts/python
```

## Safety rules for all scripts

- Run under a **dedicated least-privilege service account**; never a personal admin.
- **No secrets in code** — Windows Credential Manager / DPAPI / gMSA only.
- Scripts **report, collect, and notify**; they do not delete, disable, deprovision, or change permissions. Keep irreversible actions human-approved.
- Keep this folder version-controlled; deploy a copy to the share — don't edit the running copy directly.
