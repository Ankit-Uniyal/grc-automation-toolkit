# 02 · Policy Management Automation

> **Pillar:** Governance. Policies are the backbone of GRC. The pain is never writing them once - it is the **lifecycle**: reviews falling overdue, staff not attesting, and no one able to prove who-read-what.

---

## 1. What to automate

- **Review-cycle tracking** - flag policies due/overdue for review.
- **Approval workflow** - route drafts for sign-off and record the decision.
- **Attestation campaigns** - send "read & acknowledge" requests and chase non-responders.
- **Coverage mapping** - link each policy to the framework clauses it satisfies (ISO 27001, NIST CSF, SOC 2).
- **Publication** - push approved policies to the read-only staff library.

## 2. Data model - `policy-register.csv`

| Column | Example |
|---|---|
| PolicyID | POL-ISMS-001 |
| Title | Access Control Policy |
| Owner | CISO |
| Version | 2.1 |
| Status | Approved / Draft / Retired |
| ApprovedDate | 2026-03-01 |
| ReviewFrequencyMonths | 12 |
| NextReviewDate | 2027-03-01 |
| FrameworkRefs | ISO27001:A.5.15; NISTCSF:PR.AC |
| AttestationRequired | Yes |
| StorageLink | \\fileserver\GRC\01_Policies\... |

This single CSV (kept as an Excel `.xlsx` master) drives every automation below.

## 3. The automation

### 3a. Review-due engine (PowerShell)

```powershell
# Inline example (copy into your own .ps1; not a committed script) - policy reviews due
param([string]$RegisterPath = "\\fileserver\GRC\01_Policies\policy-register.csv",[int]$WarnDays = 30)
$today = Get-Date
Import-Csv $RegisterPath | ForEach-Object {
  $next = [datetime]$_.NextReviewDate
  $days = ($next - $today).Days
  if ($days -le $WarnDays) {
    [pscustomobject]@{ PolicyID=$_.PolicyID; Title=$_.Title; Owner=$_.Owner;
      NextReview=$_.NextReviewDate; DaysLeft=$days;
      State = if($days -lt 0){'OVERDUE'}else{'DUE SOON'} }
  }
} | Sort-Object DaysLeft | Format-Table -Auto
```

### 3b. Compute next review date automatically

When a policy is approved, recompute the review date instead of typing it:

```powershell
# Adds ReviewFrequencyMonths to ApprovedDate
Import-Csv $RegisterPath | ForEach-Object {
  $_.NextReviewDate = ([datetime]$_.ApprovedDate).AddMonths([int]$_.ReviewFrequencyMonths).ToString('yyyy-MM-dd')
  $_
} | Export-Csv $RegisterPath -NoTypeInformation
```

### 3c. Attestation campaign (PowerShell + Outlook)

```powershell
# Inline example (copy into your own .ps1; not a committed script) - policy attestation via Outlook COM, on-prem friendly
param([string]$PolicyTitle,[string]$Link,[string[]]$Recipients)
$ol = New-Object -ComObject Outlook.Application
foreach ($r in $Recipients) {
  $mail = $ol.CreateItem(0)
  $mail.To = $r
  $mail.Subject = "Action required: acknowledge '$PolicyTitle'"
  $mail.Body = "Please review the policy at $Link and reply 'ACKNOWLEDGED'. Your response is logged for audit."
  $mail.Send()
}
```

Track responses by reading the GRC mailbox folder and writing acknowledgements to an `attestations.csv` (one row per employee per policy version). Chase anyone missing after N days with the same script filtered to non-responders.

### 3d. No-code alternative - Power Automate Desktop

If scripting Outlook is off-limits, build a PAD flow:
1. **Read from Excel** → loop the policy register.
2. **Condition:** NextReviewDate within 30 days.
3. **Send Outlook email** to Owner.
4. **Run weekly** via PAD scheduled trigger or Task Scheduler.

See `scripts/power-automate/policy-review-reminder.flow.md` for the step list.

## 4. Approval workflow without a workflow tool

- Keep drafts in `01_Policies/drafts`. Name them `...-DRAFT`.
- Use a simple **approval log** (`approvals.csv`: PolicyID, Version, Approver, Decision, Date, Comment).
- A PAD/PowerShell step moves an **Approved** file from `/drafts` to the published folder, stamps the version, and appends to `approvals.csv`. The human approval (the email reply / signature) is the control; automation just records and files it.

## 5. Framework coverage mapping

Because `FrameworkRefs` is structured, you can auto-build a coverage matrix:

```python
# Inline example (copy into your own .py; not a committed script) - policy coverage matrix
import pandas as pd
df = pd.read_csv("policy-register.csv")
rows = []
for _, r in df.iterrows():
    for ref in str(r.FrameworkRefs).split(';'):
        ref = ref.strip()
        if ref:
            rows.append({"PolicyID": r.PolicyID, "Clause": ref})
cov = pd.DataFrame(rows)
cov.to_csv("policy-coverage.csv", index=False)
print(cov.groupby("Clause").size())  # clauses with no policy => gap
```

## 6. Scheduling & ownership

- **Owner:** Policy/ISMS Manager.
- Run 3a **weekly**, email overdue list to owners; run attestation chase **weekly during a campaign**.

## 7. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Reviews | Manual calendar | Auto-computed dates + weekly due engine |
| Attestation | Email blast | Tracked campaign with auto-chase + audit log |
| Coverage | Ad hoc | Auto coverage matrix highlighting gaps |

**Next:** `docs/03-risk-management.md`
