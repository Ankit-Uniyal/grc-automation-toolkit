# 04 · Control Testing & Continuous Control Monitoring

> **Pillar:** Compliance operations. This is where most GRC time disappears: scheduling tests, reminding owners, collecting results, and chasing failures. Automate the cadence and the bookkeeping; reserve human effort for judgment-based testing.

---

## 1. What to automate

- **Test scheduling** — derive each control's next test date from its frequency.
- **Reminders & escalation** — notify owners/testers before and after due dates.
- **Result capture** — standard intake so every test produces a comparable record.
- **Automated tests (CCM)** — for technical controls that can be checked by script.
- **Exception tracking** — log failures, link to risks, track remediation.

## 2. Data model — `control-matrix.csv`

| Column | Notes |
|---|---|
| ControlID | CTRL-AC-001 |
| Title | Domain admins reviewed quarterly |
| FrameworkRefs | ISO27001:A.8.2; NISTCSF:PR.AC-4 |
| Owner | IT Manager |
| Tester | Internal Audit |
| TestType | Automated / Manual / Hybrid |
| Frequency | Monthly / Quarterly / Annual |
| LastTested | 2026-03-15 |
| NextTestDate | auto |
| LastResult | Pass / Fail / Partial |
| EvidenceLink | \\fileserver\GRC\04_Evidence\... |
| ExceptionID | EXC-007 (if failed) |

## 3. The automation

### 3a. The reminder engine — `Send-ComplianceReminders.ps1`

This is the toolkit's flagship script (referenced in the README quick start).

> [!TIP]
> **Script:** [`scripts/powershell/Send-ComplianceReminders.ps1`](../scripts/powershell/Send-ComplianceReminders.ps1) — reads the control matrix, finds controls whose `NextTestDate` is due/overdue, and emails the assigned tester (supports `-WhatIf` for a safe preview). Edit its `CHANGE ME` block, then run it.

Run with `-WhatIf` first to preview who would be emailed.

### 3b. Auto-compute next test dates

```powershell
$map = @{ Monthly=1; Quarterly=3; 'Semi-Annual'=6; Annual=12 }
Import-Csv $RegisterPath | ForEach-Object {
  $m = $map[$_.Frequency]; if ($m) {
    $_.NextTestDate = ([datetime]$_.LastTested).AddMonths($m).ToString('yyyy-MM-dd')
  }; $_
} | Export-Csv $RegisterPath -NoTypeInformation
```

### 3c. Continuous Control Monitoring — automated technical tests

Many technical controls can be **tested by script** instead of by interview. Examples that need no cloud:

```powershell
# CTRL: Local admin password policy enforced
$pol = net accounts
# CTRL: BitLocker enabled on workstations
Get-BitLockerVolume | Select MountPoint, ProtectionStatus
# CTRL: Windows Firewall on for all profiles
Get-NetFirewallProfile | Select Name, Enabled
# CTRL: Antivirus definitions current
Get-MpComputerStatus | Select AntivirusSignatureLastUpdated, RealTimeProtectionEnabled
# CTRL: Audit logging enabled
auditpol /get /category:* 
# CTRL: Stale AD accounts (not logged in 90d)
Get-ADUser -Filter {Enabled -eq $true} -Properties LastLogonDate |
  Where-Object { $_.LastLogonDate -lt (Get-Date).AddDays(-90) } |
  Select SamAccountName, LastLogonDate
```

Wrap each check so it writes a **Pass/Fail row** back to a results CSV and saves raw output as evidence:

```powershell
function Write-ControlResult($id,$result,$detail,$evidenceDir){
  $stamp = Get-Date -Format 'yyyy-MM-dd'
  $detail | Out-File "$evidenceDir\EVD_$($id)_$stamp.txt"
  [pscustomobject]@{ ControlID=$id; Date=$stamp; Result=$result } |
    Export-Csv "$evidenceDir\..\ccm-results.csv" -Append -NoTypeInformation
}
```

### 3d. Exception register

When a test fails, append to `exceptions.csv` (ExceptionID, ControlID, Detected, Severity, Owner, RemediationDue, Status) and (optionally) auto-create a row in the risk register. Track remediation with the same overdue-chaser pattern.

## 4. Scheduling unattended runs (Windows Task Scheduler)

> [!TIP]
> **Script:** [`scripts/powershell/Register-GrcTasks.ps1`](../scripts/powershell/Register-GrcTasks.ps1) — registers the recurring jobs in Windows Task Scheduler under a least-privilege service account. Run once, as administrator, after editing its `CHANGE ME` block.

> Run scripts under a **dedicated least-privilege service account** (`svc-grc`). Store its credential with DPAPI / Credential Manager — never in the script.

## 5. Scheduling & ownership

- **Owner:** GRC/Compliance Manager; **Tester:** Internal Audit.
- Reminders **weekly**; CCM technical tests **daily or weekly** depending on control; exception chase **weekly**.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Scheduling | Manual calendar | Auto next-test dates |
| Reminders | Manual emails | Scheduled engine + escalation |
| Technical tests | Manual interviews | Scripted CCM with auto evidence |
| Exceptions | Ad hoc notes | Register + risk linkage + remediation chase |

**Next:** `docs/05-evidence-collection.md`
