# Scripts Index

Runnable automation for the toolkit. Point each script at your live registers (copy the CSV templates from `../templates` into your GRC share first).

## PowerShell (`powershell/`)

| Script | Purpose | Doc |
|---|---|---|
| `Send-ComplianceReminders.ps1` | Email testers about due/overdue control tests. Supports `-WhatIf`. | docs/04 |
| `Invoke-EvidenceCollection.ps1` | Harvest technical evidence (AD, BitLocker, AV, firewall, patches, stale accounts), hash + manifest. | docs/05 |
| `Register-GrcTasks.ps1` | Register the recurring jobs in Windows Task Scheduler under `svc-grc`. | docs/04 |

### Requirements
- PowerShell 5.1+ or 7 (`pwsh`).
- RSAT / ActiveDirectory module for AD collectors.
- Outlook desktop for email actions.

## Python (`python/`)

| Script | Purpose | Doc |
|---|---|---|
| `risk_engine.py` | Score the risk register and render `risk-heatmap.png`. | docs/03 |
| `build_traceability.py` | Join controls/policies/risks into a traceability matrix. | docs/08 |
| `build_uar_packs.py` | Per-manager access review packs + change reconciliation. | docs/06 |

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pandas numpy matplotlib openpyxl
```

## Power Automate Desktop (`power-automate/`)

No-code build recipes (PAD flows are stored as binary objects, so we document the step list):

| Recipe | Purpose |
|---|---|
| `policy-review-reminder.flow.md` | Email policy owners when reviews are due. |

## Safety rules for all scripts

- Run under a **dedicated least-privilege service account**; never a personal admin.
- **No secrets in code** — use Windows Credential Manager / DPAPI / gMSA.
- Scripts **report and collect**; they do not delete, disable, or change permissions. Keep irreversible actions human-approved.
- Keep this folder under version control; deploy a copy to the share — don't let people edit the running copy directly.
