# GRC Automation Toolkit (Non-Cloud Edition)

> A practical, end-to-end implementation guide and toolkit for **automating and engineering Governance, Risk & Compliance (GRC)** in organizations that are **not cloud-native** — teams still running GRC on **shared network drives, OneDrive/SharePoint, and Excel**, on **Windows endpoints and on-prem servers**.

If you are a GRC professional, internal auditor, ISMS manager, or risk analyst who currently lives in folders full of spreadsheets and Word documents, this toolkit shows you **exactly how to automate as much of that work as realistically possible** — without buying a SaaS GRC platform and without depending on a public cloud.

---

## Who this is for

- GRC / InfoSec teams in SMEs and mid-market firms with **low cloud dependency**.
- Organizations whose "GRC system" is currently: `\\fileserver\GRC\`, a OneDrive folder, and a stack of Excel/Word files.
- Auditors and consultants who need a **repeatable, scriptable** way to collect evidence and test controls on-prem.
- Anyone who wants to move from **manual, calendar-driven GRC** to **automated, data-driven GRC** using tools they already own (Windows, Office, PowerShell, Python).

## What you are NOT required to have

- No SaaS GRC platform (ServiceNow IRM, Archer, OneTrust, etc.).
- No Azure / AWS / GCP subscription.
- No paid licenses beyond **Microsoft Office** and the **free, built-in Windows tooling**.

---

## Design philosophy: "Automate with what you already own"

The automation stack here is deliberately boring and durable:

| Layer | Tool | Why |
|-------|------|-----|
| Orchestration / scripting | **PowerShell 5.1+ / 7** | Ships with Windows; great for files, AD, event logs, scheduled tasks. |
| Data wrangling & analytics | **Python 3.11+** (pandas, openpyxl) | Best for parsing, transforming, and generating reports/registers. |
| Self-service reporting | **Excel + Power Query (Get & Transform)** | Already on every analyst's desk; refreshable dashboards with zero code. |
| No-code desktop automation | **Power Automate Desktop (PAD)** | Free with Windows 10/11; automates UI, emails, file moves, approvals. |
| Storage & "database" | **Shared drive + OneDrive/SharePoint document libraries** | Your existing system of record — we add structure and versioning. |
| Scheduling | **Windows Task Scheduler** | Runs your scripts unattended on a workstation or server. |
| Notifications | **Outlook / SMTP via PowerShell** | Reminders, escalations, attestation requests. |

The golden rule: **if a human does it more than once a month and it follows rules, script it.**

---

## The GRC automation maturity model

Use this to honestly place yourself and pick your next move. Most "shared folder" teams start at Level 0–1.

| Level | Name | Characteristics | Typical tooling |
|-------|------|-----------------|-----------------|
| **0** | Manual | Ad-hoc files, no naming standard, evidence emailed around, deadlines missed. | Email + random folders |
| **1** | Structured | Standard folder taxonomy, file-naming convention, master registers in Excel. | Shared drive + templates |
| **2** | Assisted | Scripts generate registers, reminders auto-sent, evidence auto-collected from endpoints. | + PowerShell/PAD/Task Scheduler |
| **3** | Integrated | Single source of truth, controls auto-tested, dashboards refresh themselves, exceptions flagged. | + Python + Power Query dashboards |
| **4** | Continuous | Near-real-time control monitoring, drift detection, audit evidence always-ready. | + scheduled continuous control monitoring (CCM) |

This toolkit gets a Level 0–1 team reliably to **Level 3**, with a clear on-ramp to Level 4.

---

## Repository structure

```
grc-automation-toolkit/
├─ README.md                  ← you are here (master implementation guide)
├─ docs/
│  ├─ 01-folder-governance.md      Standard taxonomy, naming, versioning on shared drives/OneDrive
│  ├─ 02-policy-management.md      Policy lifecycle automation & attestations
│  ├─ 03-risk-management.md        Risk register, scoring, heatmaps, treatment tracking
│  ├─ 04-control-testing.md        Control library, automated/assisted testing, CCM
│  ├─ 05-evidence-collection.md    Automated evidence harvesting from Windows/AD/endpoints
│  ├─ 06-access-reviews.md         User access reviews & joiner/mover/leaver automation
│  ├─ 07-vendor-risk.md            Third-party/vendor risk intake & monitoring
│  ├─ 08-audit-readiness.md        Always-on audit binder, traceability, sampling
│  └─ 09-implementation-roadmap.md 90-day rollout plan & RACI
├─ scripts/
│  ├─ powershell/             Evidence collection, reminders, AD access exports, scheduling
│  ├─ python/                 Register generators, scoring, report/dashboard builders
│  └─ power-automate/         Power Automate Desktop flow descriptions (build instructions)
└─ templates/
   ├─ risk-register.csv
   ├─ control-matrix.csv
   ├─ policy-register.csv
   ├─ asset-inventory.csv
   └─ vendor-register.csv
```

---

## Quick start (30 minutes to first automation)

1. **Clone / download** this repo to your GRC shared drive, e.g. `\\fileserver\GRC\toolkit\`.
2. Read **`docs/01-folder-governance.md`** and stand up the standard folder taxonomy. This single step removes most of the chaos.
3. Drop the CSV templates from `/templates` into your registers folder; open them in Excel and save as `.xlsx` master workbooks.
4. Run your **first script** — the deadline reminder engine:
   ```powershell
   pwsh ./scripts/powershell/Send-ComplianceReminders.ps1 -RegisterPath "\\fileserver\GRC\registers\control-matrix.csv" -WhatIf
   ```
   Remove `-WhatIf` once the preview looks right.
5. Schedule it with Task Scheduler (instructions in `docs/04-control-testing.md`).

You now have automated compliance reminders running with zero ongoing effort. Everything else builds on this pattern.

---

## How to read the rest of this toolkit

Each `docs/` file follows the same structure so you can implement pillar by pillar:

1. **What to automate** — the specific repetitive work in that pillar.
2. **Data model** — the register/columns that act as the source of truth.
3. **The automation** — concrete scripts/flows with copy-paste-ready code.
4. **Scheduling & ownership** — who owns it and how it runs unattended.
5. **Maturity ladder** — minimum viable vs. advanced.

Work through them in numeric order for a greenfield rollout, or jump to the pillar that hurts most.

---

## Security & governance notes for the automation itself

Automation introduces its own risk — govern it:

- **Least privilege:** run collection scripts under a dedicated service account with read-only rights wherever possible.
- **Integrity:** keep scripts in this repo (version-controlled); never let people edit the "production" copy on the share directly.
- **Evidence integrity:** write evidence to a **write-once** location and hash it (the evidence scripts generate SHA-256 manifests).
- **Segregation of duties:** the person who runs control tests should not be the person who can edit the control library.
- **No secrets in scripts:** use Windows Credential Manager / DPAPI, never hard-code passwords.

> **Important:** This toolkit automates *collection, tracking, reporting, and reminders*. A human GRC professional must still **review, judge, and sign off**. Automation reduces toil; it does not replace accountability.

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, adapt it for your organization.

## Contributing

Issues and PRs welcome: new scripts, additional framework mappings (ISO 27001, NIST CSF, SOC 2, PCI DSS), and connectors for on-prem systems.
