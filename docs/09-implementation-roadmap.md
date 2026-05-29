# 09 · Implementation Roadmap (90-Day Rollout)

> **Pillar:** Program execution. A toolkit only delivers value if it is actually rolled out. This is a pragmatic 90-day plan to take a Level 0–1 "shared folder" GRC operation to Level 3 automation, plus the operating model to keep it running.

---

## Guiding principles

1. **Stabilize before you automate.** Fix the folder/naming chaos first (pillar 01) — automation on top of chaos just creates fast chaos.
2. **One source of truth per pillar.** Each register CSV/XLSX is authoritative; scripts read and write only it.
3. **Automate the toil, keep the judgment.** Reminders, collection, scoring, reconciliation = automate. Approvals, risk acceptance, deprovisioning = human.
4. **Least privilege & version control for the automation itself.** Run under `svc-grc`; keep scripts in this repo, not editable on the share.
5. **Prove value early.** The reminder engine (week 1) gives a visible win that buys you room for the rest.

---

## Phase 1 — Foundation (Days 1–30)

**Goal: structured, predictable storage + first automation live.**

| Week | Actions | Output |
|---|---|---|
| 1 | Stand up folder taxonomy (`New-GrcFolderTree.ps1`); publish naming convention; drop in CSV templates. | Clean `GRC/` tree, registers seeded |
| 2 | Populate `policy-register`, `control-matrix`, `risk-register` from existing files. | Baseline registers |
| 3 | Deploy the **reminder engine** (`Send-ComplianceReminders.ps1`) in `-WhatIf`, then live; create `svc-grc`. | Automated reminders running |
| 4 | Schedule weekly tasks (`Register-GrcTasks.ps1`); run naming/stale-file drift checks. | Unattended hygiene + reminders |

**Exit criteria:** every GRC file follows the convention; reminders fire weekly with no manual effort.

## Phase 2 — Core automation (Days 31–60)

**Goal: registers become live, data-driven systems.**

| Week | Actions | Output |
|---|---|---|
| 5 | Auto-compute review/test/reassessment dates across all registers. | Self-maintaining schedules |
| 6 | Deploy risk engine (scoring + heatmap) and Power Query dashboards. | Auto risk dashboard |
| 7 | Deploy evidence harvester (`Invoke-EvidenceCollection.ps1`) with hashing + manifest. | Scheduled evidence + chain of custody |
| 8 | Stand up access-review snapshots and per-manager pack generation. | Automated UAR data |

**Exit criteria:** scoring, evidence, and access data refresh on schedule; dashboards regenerate themselves.

## Phase 3 — Integrate & assure (Days 61–90)

**Goal: single, audit-ready picture; continuous monitoring.**

| Week | Actions | Output |
|---|---|---|
| 9  | Build traceability matrix (clause→control→policy→risk→evidence). | One auditor-ready file |
| 10 | Turn on CCM technical tests (firewall, BitLocker, AV, stale AD) writing Pass/Fail + evidence. | Continuous control monitoring |
| 11 | Deploy vendor alerts (cert expiry, reassessment) + completeness checks. | Automated vendor risk |
| 12 | Run a mock audit: assemble binder, reproducible sampling, freshness/gap report. | Proven audit readiness |

**Exit criteria (Level 3):** any framework clause can be traced to evidence in minutes; failures auto-flag; binder assembles by script.

---

## Operating model & RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Folder/naming governance | GRC Analyst | GRC Manager | IT | All staff |
| Policy lifecycle | Policy/ISMS Manager | CISO | Legal | Staff |
| Risk register | Risk Manager | CRO/CISO | Business owners | ExCo |
| Control testing / CCM | GRC Analyst | GRC Manager | Internal Audit | Control owners |
| Evidence collection | GRC Analyst | GRC Manager | IT/sysadmins | Auditors |
| Access reviews | IAM/IT Security | CISO | Line managers | GRC |
| Vendor risk | Vendor Manager | Procurement Lead | GRC | Owners |
| Audit readiness | GRC Manager | CISO | Internal Audit | ExCo |
| Automation maintenance | GRC Analyst (scripts) | GRC Manager | IT | — |

## Schedule-at-a-glance

| Cadence | Jobs |
|---|---|
| Daily / weekly | Reminders, CCM technical tests, drift & stale checks, overdue chasers, access snapshots, vendor alerts |
| Monthly | Traceability matrix, freshness/gap report, high-frequency evidence |
| Quarterly | Evidence harvest, access-review packs, vendor reassessment (by tier) |
| Annual | Policy reviews, full risk reassessment, framework re-mapping |

## Governing the automation (don't skip)

- **Change control:** script changes go through this repo (PR + review), then deploy to the share copy.
- **Secrets:** DPAPI / Credential Manager only; never in scripts or registers.
- **Separation of duties:** script author ≠ sole reviewer of its output; control tester ≠ control library editor.
- **Logging:** scripts write a run log (timestamp, item counts, errors) to `00_Admin/logs` for your own assurance.
- **Backup:** the `GRC/` tree and registers are backed up per your retention schedule.

## Common pitfalls

- Automating on an unstructured share (do pillar 01 first).
- Hard-coding credentials or running as a domain admin.
- Letting automation *act* (delete/deprovision) instead of *report* — keep irreversible actions human-approved.
- No owner for the scripts — they rot. Assign maintenance explicitly (see RACI).

---

**You're done.** Work back through `docs/01`–`08` to implement each pillar, and use the `scripts/` and `templates/` folders as your starting code and data models.
