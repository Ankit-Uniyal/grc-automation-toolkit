# 18 · Configuration Baseline & Drift Detection

> **Pillar:** Secure configuration assurance. Hardening standards (CIS-style baselines) are only useful if you can prove systems still match them. This pillar captures a baseline snapshot and detects **drift** over time on Windows endpoints/servers — no cloud, no agent platform.

---

## 1. What to automate

- **Baseline capture** — snapshot key security settings as the approved standard.
- **Drift detection** — compare current state to the baseline and flag differences.
- **Change reconciliation** — match drift to approved changes (docs/14).
- **Reporting** — per-host configuration compliance.

## 2. The automation

### 2a. Capture a baseline (PowerShell)

```powershell
# scripts/powershell/Get-ConfigBaseline.ps1  -> writes baseline.json
param([string]$OutFile = "baseline.json")
$baseline = [ordered]@{
  Host                 = $env:COMPUTERNAME
  CapturedAt           = (Get-Date -Format s)
  FirewallProfiles     = (Get-NetFirewallProfile | Select-Object Name, Enabled)
  Services_Automatic   = (Get-Service | Where-Object StartType -eq "Automatic" | Select-Object Name, Status)
  LocalAdmins          = (Get-LocalGroupMember -Group "Administrators" | Select-Object Name)
  PasswordPolicy       = (net accounts)
  RDPEnabled           = (Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server").fDenyTSConnections
  SMB1                 = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue).State
}
$baseline | ConvertTo-Json -Depth 5 | Out-File $OutFile -Encoding UTF8
Write-Host "Baseline written to $OutFile"
```

### 2b. Detect drift (PowerShell)

```powershell
# scripts/powershell/Compare-ConfigDrift.ps1
param([string]$BaselinePath = "baseline.json")
$base = Get-Content $BaselinePath -Raw | ConvertFrom-Json

# Re-capture current values the same way, then compare field by field
$driftReport = @()

# Example: firewall must stay enabled on all profiles
foreach ($p in (Get-NetFirewallProfile)) {
  $b = $base.FirewallProfiles | Where-Object Name -eq $p.Name
  if ($b -and $b.Enabled -ne $p.Enabled) {
    $driftReport += "FIREWALL DRIFT: $($p.Name) was $($b.Enabled) now $($p.Enabled)"
  }
}

# Example: local administrators group membership changed
$currentAdmins = (Get-LocalGroupMember -Group "Administrators").Name
$baseAdmins = $base.LocalAdmins.Name
$added   = $currentAdmins | Where-Object { $_ -notin $baseAdmins }
$removed = $baseAdmins   | Where-Object { $_ -notin $currentAdmins }
if ($added)   { $driftReport += "ADMIN ADDED: "   + ($added   -join ", ") }
if ($removed) { $driftReport += "ADMIN REMOVED: " + ($removed -join ", ") }

$driftReport | Tee-Object -FilePath "config-drift.txt"
```

### 2c. Reconcile drift to approved changes

Cross-reference `config-drift.txt` against the change register (docs/14). Drift with **no matching ChangeID** is a potential unauthorized change — escalate to an issue (docs/15).

## 3. Scheduling & ownership

- **Owner:** Sysadmin / SecOps; **Oversight:** GRC.
- Re-baseline after approved hardening changes; run drift detection **weekly** per host (loop via `Invoke-Command` in a domain) and store results as evidence.

## 4. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Baseline | Word doc of settings | Machine-readable JSON snapshot |
| Drift | Manual spot checks | Automated weekly comparison |
| Integrity | Trust | Drift-vs-change reconciliation |
| Evidence | None | Drift reports filed + hashed |

**Next:** `docs/19-data-privacy.md`
