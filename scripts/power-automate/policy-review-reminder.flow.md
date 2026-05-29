# Power Automate Desktop Flow: Policy Review Reminder (no-code)

> A build-it-yourself recipe for teams who prefer **Power Automate Desktop (PAD)** — free with Windows 10/11 — over scripting. This flow emails policy owners when a policy is due for review, reading the same `policy-register` source of truth.

PAD flows are stored as binary/cloud objects, so this repo documents the **exact step list** to recreate the flow in minutes rather than shipping an opaque file.

---

## Prerequisites

- Power Automate Desktop installed (Start → "Power Automate").
- Outlook desktop installed and signed in.
- `policy-register.xlsx` (or .csv) on the shared drive.

## Flow steps

1. **Set variable** `WarnDays` = 30.
2. **Get current date and time** → store in `Today`.
3. **Launch Excel** → open `\\fileserver\GRC\01_Policies\policy-register.xlsx`, visible = false.
4. **Read from Excel worksheet** → read all cells as a DataTable `Policies` (first row contains column names = On).
5. **For each** `Row` in `Policies`:
   1. **If** `Row['Status']` = "Approved" **and** `Row['NextReviewDate']` is not empty:
      1. **Convert text to datetime** `Row['NextReviewDate']` → `NextReview`.
      2. **Subtract dates** `NextReview` − `Today` (in days) → `DaysLeft`.
      3. **If** `DaysLeft` <= `WarnDays`:
         1. **Set variable** `State` = If `DaysLeft` < 0 then "OVERDUE" else "DUE SOON".
         2. **Send email message through Outlook**:
            - Account: your GRC mailbox
            - To: `Row['Owner']` (or look up the owner's email)
            - Subject: `[GRC] Policy review ${State}: ${Row['Title']}`
            - Body: include PolicyID, Version, NextReviewDate, and the StorageLink.
6. **Close Excel** (do not save).
7. (Optional) **Write text to file** → append a run-log line to `00_Admin\logs`.

## Scheduling

- In PAD, create a **scheduled trigger** (Power Automate → "+ New flow" cloud trigger is not required for desktop) **or** simpler: register a **Windows Task Scheduler** task that runs:
  ```
  "C:\Program Files (x86)\Power Automate Desktop\PAD.Console.Host.exe" -flow "Policy Review Reminder"
  ```
  Weekly, Monday 08:00, under the `svc-grc` account.

## Notes

- Keep the logic identical to `scripts/powershell/Get-PolicyReviewsDue.ps1` so the two approaches stay consistent.
- This flow **only notifies** — approvals and edits remain human actions.
- For attestation campaigns, clone this flow but loop the **staff distribution list** and link to the published policy.

---

### Related no-code flows to build the same way

- `evidence-screenshot.flow.md` — open a legacy app, capture a screenshot, save as `EVD_...` evidence.
- `vendor-cert-expiry.flow.md` — read `vendor-register`, email owners before certificate expiry.
- `control-test-reminder.flow.md` — the control-matrix equivalent of this policy flow.
