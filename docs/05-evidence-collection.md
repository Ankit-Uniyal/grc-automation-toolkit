# 05 · Automated Evidence Collection

> **Pillar:** Audit & assurance. Evidence gathering is the single most automatable part of GRC. In a non-cloud shop, most evidence already lives on Windows endpoints, Active Directory, file servers, and applications you can query locally. Harvest it on a schedule, hash it, and file it — so audits stop being fire drills.

---

## 1. What to automate

- **Scheduled harvesting** of standard evidence (configs, exports, logs, screenshots).
- **Consistent filing** into `04_Evidence/<Year>/<Quarter>/<ControlID>/`.
- **Integrity** — SHA-256 manifest so you can prove evidence wasn't altered.
- **Coverage check** — which controls are missing current-period evidence.
- **Chain of custody** — who collected what, when, from where.

## 2. Evidence that scripts can collect with zero cloud

| Evidence | Source | Command |
|---|---|---|
| Privileged group membership | AD | `Get-ADGroupMember 'Domain Admins'` |
| User access list | AD | `Get-ADUser -Filter * -Properties *` |
| Password policy | AD/local | `Get-ADDefaultDomainPasswordPolicy` |
| Patch status | WSUS/Windows | `Get-HotFix` |
| Disk encryption | endpoint | `Get-BitLockerVolume` |
| Endpoint protection | endpoint | `Get-MpComputerStatus` |
| Firewall config | endpoint | `Get-NetFirewallProfile` |
| Running services | endpoint | `Get-Service` |
| Audit/security logs | Event Log | `Get-WinEvent` |
| Backup job status | backup tool | tool CLI / log parse |
| Installed software | endpoint | registry / `Get-Package` |

## 3. The automation

### 3a. Evidence harvester with hashing (PowerShell)

```powershell
# scripts/powershell/Invoke-EvidenceCollection.ps1
param(
  [string]$EvidenceRoot = "\\fileserver\GRC\04_Evidence",
  [string]$Quarter = ("{0}\Q{1}" -f (Get-Date).Year, [math]::Ceiling((Get-Date).Month/3))
)
function Save-Evidence {
  param($ControlID, $Name, [scriptblock]$Collector)
  $dir = Join-Path $EvidenceRoot "$Quarter\$ControlID"
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  $stamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
  $file = Join-Path $dir "EVD_${ControlID}_${Name}_$stamp.txt"
  try { & $Collector | Out-File $file -Encoding UTF8 }
  catch { "COLLECTION ERROR: $_" | Out-File $file }
  $hash = (Get-FileHash $file -Algorithm SHA256).Hash
  [pscustomobject]@{
    ControlID=$ControlID; File=$file; SHA256=$hash
    CollectedBy=$env:USERNAME; CollectedFrom=$env:COMPUTERNAME; When=$stamp
  }
}

$manifest = @()
$manifest += Save-Evidence 'CTRL-AC-001' 'DomainAdmins' { Get-ADGroupMember 'Domain Admins' | Select Name,SamAccountName }
$manifest += Save-Evidence 'CTRL-AC-002' 'PasswordPolicy' { Get-ADDefaultDomainPasswordPolicy }
$manifest += Save-Evidence 'CTRL-EP-001' 'BitLocker' { Get-BitLockerVolume | Select MountPoint,ProtectionStatus }
$manifest += Save-Evidence 'CTRL-EP-002' 'Antivirus' { Get-MpComputerStatus }
$manifest += Save-Evidence 'CTRL-NW-001' 'Firewall' { Get-NetFirewallProfile | Select Name,Enabled }
$manifest += Save-Evidence 'CTRL-VM-001' 'Patches' { Get-HotFix | Sort InstalledOn -Descending | Select -First 50 }

$manifest | Export-Csv (Join-Path $EvidenceRoot "$Quarter\_manifest.csv") -Append -NoTypeInformation
"Collected $($manifest.Count) evidence items for $Quarter"
```

The manifest gives you a tamper-evident chain of custody: re-hash any file later and compare to prove integrity.

### 3b. UI / app evidence that has no API — Power Automate Desktop

For systems with no command line (legacy desktop apps, on-prem web admin consoles), use PAD to:
1. Open the app and navigate to the relevant screen.
2. **Take a screenshot** / export to file.
3. Save with the standard `EVD_...` name into the quarter folder.
4. Run on the control's cadence.

See `scripts/power-automate/evidence-screenshot.flow.md`.

### 3c. Coverage gap check (PowerShell)

Cross-reference the control matrix against collected evidence to find gaps **before** the auditor does:

```powershell
$controls = Import-Csv "\\fileserver\GRC\03_Controls\control-matrix.csv"
$quarterDir = "\\fileserver\GRC\04_Evidence\2026\Q2"
foreach ($c in $controls) {
  $have = Test-Path (Join-Path $quarterDir $c.ControlID)
  if (-not $have) { "MISSING evidence: $($c.ControlID) - $($c.Title)" }
}
```

## 4. Integrity & retention rules

- Write evidence to a **write-once** share (contributors add only).
- Keep the `_manifest.csv` append-only; never edit historical rows.
- Apply the retention schedule from `docs/01` (e.g., 7 years). Archive, don't delete; any purge needs documented approval.

## 5. Scheduling & ownership

- **Owner:** GRC Analyst (collection), Internal Audit (review).
- Schedule `Invoke-EvidenceCollection.ps1` to run **at the start of each quarter** (and monthly for high-frequency controls) via Task Scheduler under `svc-grc`.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Collection | Manual screenshots | Scheduled multi-source harvester |
| Integrity | None | SHA-256 manifest + chain of custody |
| Coverage | Found out at audit | Automated gap report each period |
| UI evidence | Manual | PAD screenshot flows |

**Next:** `docs/06-access-reviews.md`
