# DIY Guide - Do It Yourself, Step by Step

> [!IMPORTANT]
> This is the **hand-holding guide**. It assumes **no prior scripting experience**.
> Follow the numbered steps in order and you will get the outcome for each GRC task.
> Before editing any script, read the 60-second **[CONVENTIONS.md](CONVENTIONS.md)** so you know
> exactly which values to change (look for the orange **`CHANGE_ME`** tokens).

## How to use this guide

Every task below uses the **same 6-part recipe** so it always feels familiar:

1. **Outcome** - what you will have when you finish.
2. **You need** - files/access to have ready first.
3. **Do this** - the granular, click-by-click / command-by-command steps.
4. **Values to change** - the exact `CHANGE_ME` tokens for this task.
5. **Verify** - how to confirm it worked.
6. **Schedule (optional)** - make it run by itself.

> [!TIP]
> Read **[Part A - One-Time Setup](#part-a--one-time-setup)** once. Then jump straight to whichever
> task you need in **[Part B - Task Recipes](#part-b--task-recipes)**.

---

## Table of contents

- [Part A - One-Time Setup](#part-a--one-time-setup)
  - [A1. Install the tools](#a1-install-the-tools)
  - [A2. Download this toolkit to your PC](#a2-download-this-toolkit-to-your-pc)
  - [A3. Pick your folder layout (system of record)](#a3-pick-your-folder-layout-system-of-record)
  - [A4. Set up the service account & email](#a4-set-up-the-service-account--email)
  - [A5. Store secrets safely (no passwords in scripts)](#a5-store-secrets-safely-no-passwords-in-scripts)
  - [A6. Allow PowerShell scripts to run](#a6-allow-powershell-scripts-to-run)
  - [A7. Test Python](#a7-test-python)
- [Part B - Task Recipes](#part-b--task-recipes)
  - [B1. Send policy review reminders](#b1-send-policy-review-reminders)
  - [B2. Calculate & refresh the risk register](#b2-calculate--refresh-the-risk-register)
  - [B3. Collect evidence automatically](#b3-collect-evidence-automatically)
  - [B4. Run an access (user) review campaign](#b4-run-an-access-user-review-campaign)
  - [B5. Track control testing](#b5-track-control-testing)
  - [B6. Monitor vendor risk & certificate expiry](#b6-monitor-vendor-risk--certificate-expiry)
  - [B7. Track incidents & SLAs](#b7-track-incidents--slas)
  - [B8. Track vulnerabilities against SLAs](#b8-track-vulnerabilities-against-slas)
  - [B9. Track issues / CAPA](#b9-track-issues--capa)
  - [B10. Build the framework crosswalk / obligations coverage](#b10-build-the-framework-crosswalk--obligations-coverage)
  - [B11. Produce the metrics / management-review pack](#b11-produce-the-metrics--management-review-pack)
  - [B12. Run everything daily (the orchestrator)](#b12-run-everything-daily-the-orchestrator)
- [Part C - Build the Excel dashboard](#part-c--build-the-excel-dashboard)
- [Part D - Troubleshooting](#part-d--troubleshooting)

---

# Part A - One-Time Setup

> [!NOTE]
> You only do Part A once per machine (the PC or server that will run the automation).

## A1. Install the tools

Everything here is free and runs on a normal Windows PC. Nothing here uses the cloud.

1. **PowerShell** - already on Windows. Check the version: open **Start menu → type `PowerShell` → Enter**, then run:
   ```powershell
   $PSVersionTable.PSVersion
   ```
   You need **5.1 or higher** (any modern Windows has this). PowerShell 7 is nicer but optional.
2. **Python** - go to <https://www.python.org/downloads/> → click **Download Python 3.11+** → run the installer.
   > [!IMPORTANT]
   > On the first installer screen, **tick the box** that says **"Add python.exe to PATH"**, then click *Install Now*.
3. **Python libraries** - open PowerShell and run:
   ```powershell
   pip install pandas openpyxl
   ```
4. **Excel** - you already have it (part of Microsoft Office). Power Query is built in.
5. **Power Automate Desktop** (optional, for screen automation) - free from Microsoft Store; install only if you need the PAD flows.
6. **VS Code** (optional but recommended for editing scripts with coloured `CHANGE_ME` tokens) - <https://code.visualstudio.com/>.

## A2. Download this toolkit to your PC

1. Go to the repository home page.
2. Click the green **`< > Code`** button → **Download ZIP**.
3. Right-click the downloaded ZIP → **Extract All** → choose a folder, e.g. `C:\GRC\toolkit`.
4. (Recommended) Open that folder in **VS Code**: *File → Open Folder*. The included `.vscode/settings.json`
   turns on coloured highlighting for every `CHANGE_ME` value.

## A3. Pick your folder layout (system of record)

This toolkit treats your **shared drive / OneDrive / SharePoint-synced folder** as the database.
Create this structure once (change the root to match your environment):

```text
<<PATH: \\fileserver\GRC>>\          <-- CHANGE ME (your shared-drive root)
  00_Admin\         (program admin + this toolkit; also holds \registers and \reports)
    registers\      (working copies of the CSVs from templates\ - your live data)
    reports\        (generated dashboards & packs)
    toolkit\        (a copy of this toolkit, incl. its scripts\ folder)
  01_Policies\      (policy-register.csv, approved policies)
  02_Risk\          (risk-register.csv, assessments)
  03_Controls\      (control-matrix.csv, test results)
  04_Evidence\      (collected evidence, write-once, hashed)
  05_Assets\  06_Vendors\  07_Audits\  08_Incidents\  99_Archive\
  logs\             (script run logs)
```

> [!NOTE]
> This is the same numbered taxonomy defined in `docs/01-folder-governance.md`. Registers that have a natural home live there (risk -> `02_Risk\`, controls -> `03_Controls\`); registers without a dedicated folder (policy, vendor, incident, vuln, issues, KRI) live together in `00_Admin\registers\`, which is what the scripts default to. The script `CHANGE_ME` defaults already point at these paths.

1. Create the folders above on your shared drive.
2. Copy each CSV from the toolkit's **`templates\`** folder into its matching folder (e.g. `risk-register.csv` -> `02_Risk\`, `control-matrix.csv` -> `03_Controls\`, the rest -> `00_Admin\registers\`).
3. These copied CSVs are now your **live registers** - you will maintain these, not the templates.

> [!TIP]
> Keep your register folders backed up / versioned. It is your real GRC data.

## A4. Set up the service account & email

> [!WARNING]
> Ask your IT team to create a **dedicated low-privilege account** (e.g. `svc-grc`) to run the
> scheduled scripts. Do **not** run automation under a personal admin account.

1. Decide which mailbox sends reminders, e.g. `<<EMAIL: grc-bot@yourcompany.local>>`.
2. Get your internal **SMTP server name** from IT, e.g. `<<SERVER: smtp.yourcompany.local>>`.
3. You will paste these two values into the scripts' `CHANGE_ME` slots later.

## A5. Store secrets safely (no passwords in scripts)

> [!IMPORTANT]
> Never type a password directly into a script. This toolkit reads credentials from the
> **Windows Credential Manager** so secrets never sit in a file.

If a script needs SMTP authentication, store the credential once (run as the service account):

```powershell
# Run once. You will be prompted for the password in a secure box.
cmdkey /generic:GRC-SMTP /user:<<CHANGE_ME: grc-bot@yourcompany.local>>   # CHANGE ME
# (Enter the password when Windows prompts you.)
```

## A6. Allow PowerShell scripts to run

By default Windows blocks scripts. Allow signed/local scripts **for your user only** (safe):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## A7. Test Python

```powershell
python --version
python -c "import pandas; print('pandas OK', pandas.__version__)"
```
If both print without errors, you are ready.

---

# Part B - Task Recipes

> Each recipe is self-contained. The scripts live in `scripts\`. Edit the `CHANGE_ME` values at the
> top of each script (search `Ctrl+F` for `CHANGE_ME`) **before** running.

## B1. Send policy review reminders

**1. Outcome:** Owners of policies due for review automatically get an email reminder; nothing is changed for them - they just get nudged.

**2. You need:** `00_Admin\registers\policy-register.csv` filled in (Policy, Owner, OwnerEmail, NextReviewDate).

**3. Do this:**
1. Open `scripts\powershell\Send-ComplianceReminders.ps1` in VS Code.
2. Find the `CHANGE ME` banner near the top (press `Ctrl+F`, type `CHANGE_ME`).
3. Set the SMTP server, From address, and the path to `policy-register.csv`.
4. Save the file.
5. Run it from PowerShell:
   ```powershell
   cd <<PATH: C:\GRC\toolkit\scripts\powershell>>   # CHANGE ME
   .\Send-ComplianceReminders.ps1
   ```

**4. Values to change:** `$SmtpServer`, `$FromAddress`, `$PolicyRegisterPath`, `$ReminderDaysBefore`.

**5. Verify:** Check the mailbox sent items and the log in `logs\`. Run with `-WhatIf` first to preview without sending.

**6. Schedule:** see [B12](#b12-run-everything-daily-the-orchestrator) or register a daily task:
```powershell
.\Register-GrcTasks.ps1
```

## B2. Calculate & refresh the risk register

**1. Outcome:** Inherent/residual scores, risk levels, and a treatment-due flag are recalculated for every risk and written back to the register.

**2. You need:** `02_Risk\risk-register.csv` (Likelihood, Impact, ControlEffectiveness columns filled).

**3. Do this:**
1. Open `scripts\python\risk_engine.py`.
2. Set the input/output paths at the top (`CHANGE_ME`).
3. Run:
   ```powershell
   python risk_engine.py
   ```

**4. Values to change:** `RISK_REGISTER_PATH`, `OUTPUT_PATH`, and (optional) the scoring thresholds.

**5. Verify:** Open the output CSV - the `ResidualScore` and `RiskLevel` columns are now populated.

**6. Schedule:** add to the daily orchestrator (B12).

## B3. Collect evidence automatically

**1. Outcome:** Files referenced in your control matrix are copied into a dated, write-once evidence folder and hashed (SHA-256) so they cannot be silently altered.

**2. You need:** `03_Controls\control-matrix.csv` with an `EvidenceSourcePath` column.

**3. Do this:**
1. Open `scripts\powershell\Invoke-EvidenceCollection.ps1`.
2. Set the control-matrix path and the evidence root.
3. Run:
   ```powershell
   .\Invoke-EvidenceCollection.ps1
   ```

**4. Values to change:** `$ControlMatrixPath`, `$EvidenceRoot`.

**5. Verify:** A new dated folder appears under `04_Evidence\` with copied files and a `hashes.csv` manifest.

> [!WARNING]
> This script only **copies and hashes**. It never deletes or moves your source files.

## B4. Run an access (user) review campaign

**1. Outcome:** A per-manager review pack (who has access to what) is generated so managers can certify or flag access. The script never changes access itself.

**2. You need:** an export of users/entitlements as a CSV in `00_Admin\registers\`.

**3. Do this:**
1. Open `scripts\python\build_uar_packs.py`.
2. Set the access-export path and the output folder.
3. Run:
   ```powershell
   python build_uar_packs.py
   ```

**4. Values to change:** `ACCESS_EXPORT_PATH`, `OUTPUT_DIR`, `MANAGER_COLUMN`.

**5. Verify:** One review file per manager appears in the output folder.

> [!WARNING]
> Managers' decisions are applied **manually** by IT after approval. Automation only prepares and tracks.

## B5. Track control testing

**1. Outcome:** A traceability view linking requirements → controls → tests → evidence, highlighting gaps.

**2. You need:** `control-matrix.csv` and `crosswalk.csv`.

**3. Do this:** run `python build_traceability.py` after setting its paths.

**4. Values to change:** input paths and output path at the top.

**5. Verify:** open the generated traceability CSV; rows with no test/evidence are flagged.

## B6. Monitor vendor risk & certificate expiry

**1. Outcome:** Vendors with expiring certifications (e.g. SOC 2, ISO) or overdue reassessments are listed and owners notified.

**2. You need:** `00_Admin\registers\vendor-register.csv` (CertExpiryDate, NextReviewDate, Owner, OwnerEmail).

**3. Do this:** set paths in the vendor monitoring script, then run it.

**4. Values to change:** register path, SMTP settings, warning window (days before expiry).

**5. Verify:** review the generated alert list / sent reminders.

## B7. Track incidents & SLAs

**1. Outcome:** Open incidents are checked against response/resolution SLAs; breaches are flagged and summarised.

**2. You need:** `00_Admin\registers\incident-register.csv`.

**3. Do this:** run `python incident_monitor.py` after setting its paths.

**4. Values to change:** register path, SLA hours per severity.

**5. Verify:** open the output - breached/at-risk incidents are flagged.

> [!WARNING]
> The script flags SLA breaches. It never sends external/breach notifications - that decision stays with a human.

## B8. Track vulnerabilities against SLAs

**1. Outcome:** Vulnerabilities past their remediation SLA (by severity) are flagged and counted.

**2. You need:** `00_Admin\registers\vuln-register.csv`.

**3. Do this:** run `python vuln_sla.py` after setting paths and SLA days per severity.

**4. Values to change:** register path, SLA days (Critical/High/Medium/Low).

**5. Verify:** output lists overdue vulnerabilities and SLA-attainment %.

## B9. Track issues / CAPA

**1. Outcome:** Open corrective/preventive actions are aged, overdue ones flagged, owners reminded.

**2. You need:** `00_Admin\registers\issue-register.csv`.

**3. Do this:** run `python issue_tracker.py` after setting paths.

**4. Values to change:** register path, overdue threshold.

**5. Verify:** overdue issues appear in the output summary.

## B10. Build the framework crosswalk / obligations coverage

**1. Outcome:** A map of which controls satisfy which framework requirements (ISO 27001, NIST, etc.) and where coverage is missing.

**2. You need:** `crosswalk.csv` and `obligations-register.csv`.

**3. Do this:** run the crosswalk build script after setting paths.

**4. Values to change:** input/output paths, framework column names.

**5. Verify:** uncovered requirements are listed so you can assign controls.

## B11. Produce the metrics / management-review pack

**1. Outcome:** A single metrics snapshot (KRIs, SLA attainment, overdue counts) appended to history and ready for the management review.

**2. You need:** the registers above populated.

**3. Do this:** run `python grc_metrics.py` after setting paths.

**4. Values to change:** register folder path, history-file path.

**5. Verify:** a new dated row appears in `grc-metrics-history.csv`.

**6. Schedule:** run monthly before your governance meeting.

## B12. Run everything daily (the orchestrator)

**1. Outcome:** One command runs all the daily checks and writes one consolidated log.

**2. Do this:**
1. Open `scripts\powershell\Invoke-GrcDailyRun.ps1` and set the toolkit root path.
2. Test it once manually:
   ```powershell
   .\Invoke-GrcDailyRun.ps1
   ```
3. Register it to run automatically every morning:
   ```powershell
   .\Register-GrcTasks.ps1
   ```

**3. Values to change:** `$ToolkitRoot`, run time, the service account.

**4. Verify:** open **Task Scheduler** → confirm the **GRC Daily Run** task exists and the last run = *Success*.

---

# Part C - Build the Excel dashboard

**Outcome:** A self-refreshing Excel dashboard that reads the generated metrics CSV - no manual charting.

1. Open a new Excel workbook.
2. **Data → Get Data → From Text/CSV** → choose `reports\grc-metrics-history.csv`.
3. Click **Transform Data** to clean columns if needed, then **Close & Load**.
4. Insert **PivotCharts** for the metrics you care about (overdue counts, SLA %, risk levels).
5. **Data → Queries & Connections → Properties →** tick **"Refresh data when opening the file"**.
6. Save as `GRC-Dashboard.xlsx` in `reports\`.

> [!TIP]
> Now every time someone opens the dashboard, it pulls the latest numbers automatically.

See [`templates/dashboards/README.md`](templates/dashboards/README.md) for the detailed walk-through.

---

# Part D - Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `running scripts is disabled on this system` | Execution policy | Re-run step **A6**. |
| `python is not recognized` | PATH not set | Reinstall Python and tick **Add to PATH** (step A1). |
| `No module named pandas` | Library missing | Run `pip install pandas openpyxl`. |
| Email not sent | Wrong SMTP / auth | Re-check `$SmtpServer`, `$FromAddress`, and the stored credential (A5). |
| `Could not find file ...` | Wrong path in a `CHANGE_ME` slot | Open the script, fix the path token, save. |
| Script changed data I didn't expect | - | Stop. These scripts only report/collect/notify. Re-check you ran the right file. |

> [!TIP]
> Still stuck? Open the matching pillar guide in **[docs/](docs/)** - each one explains the concept
> behind its script in plain language.
