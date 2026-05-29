
> [!IMPORTANT]
> ### New here? Start with these two pages
> - **[DIY-GUIDE.md](DIY-GUIDE.md)** - granular, click-by-click steps for every task (no scripting experience needed).
> - **[CONVENTIONS.md](CONVENTIONS.md)** - the 60-second guide to the **`CHANGE_ME`** convention: how to find and edit every value you must set for your environment.
>
> Every script marks the values **you** must change with a bright **`CHANGE_ME`** token and a `# CHANGE ME` comment - search a script for `CHANGE_ME` to find them all.

# GRC Automation Toolkit (Non-Cloud Edition)

> A practical, end-to-end implementation guide and toolkit for **automating and engineering Governance, Risk & Compliance (GRC)** in organizations that are **not cloud-native** - teams still running GRC on **shared network drives, OneDrive/SharePoint, and Excel**, on **Windows endpoints and on-prem servers**.

This toolkit covers the **whole GRC program** - not just controls and reminders, but compliance obligations, multi-framework crosswalks, incidents and breach clocks, business continuity, change governance, issues/exceptions/CAPA, internal audit, vulnerability management, configuration drift, data privacy, people/awareness/SoD, and management-review metrics - and shows you how to automate each part using tools you already own (Windows, Office, PowerShell, Python).

---

## Who this is for

GRC / InfoSec teams, internal auditors, ISMS/privacy managers, and risk analysts in SMEs and mid-market firms with **low cloud dependency** - where the "GRC system" today is a shared drive, a OneDrive folder, and a stack of Excel/Word files. No SaaS GRC platform and no public-cloud subscription required: only **Microsoft Office** and **free, built-in Windows tooling**.

---

## The automation stack ("automate with what you already own")

| Layer | Tool | Role |
|-------|------|------|
| Scripting/orchestration | **PowerShell 5.1+ / 7** | Files, AD, event logs, scheduling, notifications |
| Data/analytics | **Python 3.11+** (pandas) | Parsing, scoring, registers, reports |
| Self-service reporting | **Excel + Power Query** | Refreshable dashboards, zero code |
| No-code desktop automation | **Power Automate Desktop** | UI automation, emails, file moves |
| Storage / system of record | **Shared drive + OneDrive/SharePoint** | Your registers and evidence |
| Scheduling | **Windows Task Scheduler** | Unattended runs |

The golden rule: **if a human does it more than once a month and it follows rules, script it.** Automation reduces toil; humans keep accountability for judgment and approvals.

---

## Shared engineering layer (don't repeat yourself)

Every script builds on a common foundation:

- **`scripts/powershell/GrcToolkit.psm1`** - reusable PowerShell module: register I/O, logging, SHA-256 hashing, date helpers, Outlook notifications, evidence capture.
- **`scripts/python/grclib.py`** - Python helpers: register load/save, date math, ref splitting, hashing, logging, banding.
- **`scripts/powershell/Invoke-GrcDailyRun.ps1`** - master orchestrator that runs the recurring jobs in one scheduled pass.

---

## The GRC pillars (docs/)

Each `docs/` file follows the same structure: **what to automate → data model → copy-paste code → scheduling/ownership → maturity ladder.**

**Foundations & core**
- `01-folder-governance.md` - taxonomy, naming, versioning, drift detection
- `02-policy-management.md` - policy lifecycle, attestations, coverage
- `03-risk-management.md` - register, scoring, heatmaps, treatment
- `04-control-testing.md` - control library, reminders, continuous control monitoring
- `05-evidence-collection.md` - automated evidence harvesting + hashed manifests
- `06-access-reviews.md` - UARs and joiner/mover/leaver
- `07-vendor-risk.md` - third-party intake, scoring, cert expiry
- `08-audit-readiness.md` - always-on audit binder, traceability, sampling
- `09-implementation-roadmap.md` - 90-day rollout & RACI

**Compliance & governance**
- `10-compliance-obligations.md` - obligations register, compliance calendar
- `11-framework-crosswalk.md` - map once, report against many frameworks
- `21-metrics-management-review.md` - KRIs/KPIs, RAG dashboard, management-review pack

**Operational GRC**
- `12-incident-management.md` - incident register, SLA timers, breach clock
- `13-business-continuity.md` - BIA, RTO/RPO, DR/BCP test scheduling
- `14-change-management.md` - change governance & approval completeness
- `15-issues-capa.md` - issues, exceptions/waivers, corrective actions (the hub)
- `16-internal-audit.md` - audit universe, risk-based plan, sampling, findings

**Technical risk & assurance**
- `17-vulnerability-management.md` - scanner ingest, SLA tracking, patch compliance
- `18-config-baseline.md` - baseline capture & configuration drift detection

**Data, privacy & people**
- `19-data-privacy.md` - RoPA, DPIA, DSAR clocks, retention
- `20-people-awareness-sod.md` - training, phishing ingest, segregation-of-duties

---

## Repository structure

```
grc-automation-toolkit/
├─ README.md                  ← master guide (this file)
├─ docs/                      21 pillar guides (01-21)
├─ scripts/
│  ├─ powershell/             GrcToolkit.psm1 + reminders, evidence, scheduling, orchestrator
│  ├─ python/                 grclib.py + risk, traceability, UAR, metrics, issues, incidents, vulns, SoD
│  └─ power-automate/         no-code PAD flow recipes
└─ templates/                 register CSVs for every pillar (risk, control, policy, asset, vendor,
                              obligations, crosswalk, incident, issue, exception, change, BIA,
                              vuln, RoPA, DSAR, KRI, SoD rules, audit universe)
```

---

## Maturity model

| Level | Name | Characteristics |
|-------|------|-----------------|
| 0 | Manual | Ad-hoc files, deadlines missed |
| 1 | Structured | Standard taxonomy, naming, master registers |
| 2 | Assisted | Scripts generate registers, reminders, evidence auto-collected |
| 3 | Integrated | Single source of truth, controls auto-tested, dashboards refresh, exceptions flagged |
| 4 | Continuous | Near-real-time monitoring, drift detection, always-ready evidence |

This toolkit takes a Level 0-1 team to **Level 3**, with a clear on-ramp to Level 4.

---

## Before you start (prerequisites checklist)

Run through this once so you know whether you can use the toolkit on your own or need a hand from IT. Nothing here is exotic; most Windows analyst laptops already have the basics.

**To run the reports yourself (the 2-minute path below):**

- [ ] Windows 10/11 (or any OS that runs Python)
- [ ] Python 3.11+ installed and on your PATH (`python --version`)
- [ ] Ability to install packages with `pip` (see requirements.txt)
- [ ] A copy of this repo on your machine (download ZIP or `git clone`)

**To schedule automation and send notifications (the "roll it out for real" path), you also need:**

- [ ] PowerShell 5.1+ (built into Windows) or PowerShell 7
- [ ] A path you can read/write for the GRC share (e.g. a mapped drive or OneDrive/SharePoint folder)
- [ ] Outlook on the machine, or an SMTP relay host, for email reminders
- [ ] A service account (often called svc-grc) that owns the scheduled tasks - ask IT
- [ ] Read access to Active Directory if you use the access-review scripts - ask IT
- [ ] Permission to create Scheduled Tasks on the host - ask IT

If the second list has gaps, you can still get full value from the Python reports today and bring IT in for the scheduling/credential pieces later. The items marked "ask IT" are the usual reasons a pure-policy analyst needs a technical partner.

---

## Quick start

### Try it in 2 minutes (with the included sample data)

No environment setup needed - the `templates/` folder ships with realistic sample CSVs so you can see real output immediately.

```bash
# 1. Install Python deps (one-time)
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 2. Run the risk engine against the bundled sample register
cd scripts/python
python risk_engine.py ../../templates/risk-register.csv
#   -> writes risk-register-scored.csv + risk-heatmap.png and prints the band counts

# 3. Run the vulnerability SLA report against the bundled sample register
copy ..\..\templates\vuln-register.csv vuln-register.csv   # Windows (cp on macOS/Linux)
python vuln_sla.py
#   -> writes vuln-sla-report.csv and prints open-by-severity + breach count
```

That is a working GRC output (a scored risk heatmap and an SLA breach report) before you touch your real environment.

### Roll it out for real

1. Copy this repo to your GRC share, e.g. `\\fileserver\GRC\00_Admin\toolkit\`.
2. Read `docs/01-folder-governance.md` and stand up the numbered folder taxonomy (`00_Admin`, `01_Policies`, `02_Risk`, ... `99_Archive`).
3. Copy the CSVs from `/templates` into the matching folders (e.g. `risk-register.csv` -> `02_Risk\`, `control-matrix.csv` -> `03_Controls\`).
4. Open each script you plan to use, press `Ctrl+F`, search for `CHANGE_ME`, and replace every `<<CHANGE_ME: ...>>` token with your real value (full walkthrough: `DIY-GUIDE.md`; convention: `CONVENTIONS.md`).
5. Preview the reminder engine safely with `-WhatIf`:
   ```powershell
   pwsh ./scripts/powershell/Send-ComplianceReminders.ps1 -RegisterPath "\\fileserver\GRC\03_Controls\control-matrix.csv" -WhatIf
   ```
6. Schedule the master run with Task Scheduler (`Register-GrcTasks.ps1`).

---

## Security & governance of the automation itself

- **Least privilege:** run under a dedicated service account (`svc-grc`), read-only where possible.
- **No secrets in scripts:** use Windows Credential Manager / DPAPI / gMSA.
- **Integrity:** scripts are version-controlled here; evidence is written write-once and SHA-256 hashed.
- **Separation of duties:** the person running tests is not the one editing the control library.
- **Report, don't act:** automation collects/tracks/notifies. Irreversible actions (deletion, deprovisioning, breach notification, risk acceptance, approvals) stay **human-approved**.

---

## License

MIT - see [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome: new scripts, additional framework mappings, and connectors for on-prem systems.
