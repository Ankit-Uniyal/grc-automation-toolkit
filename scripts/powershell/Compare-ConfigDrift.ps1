<#
.SYNOPSIS
    Detects configuration drift by comparing a host's current state to its approved baseline.

.DESCRIPTION
    Reads a baseline.json produced by Get-ConfigBaseline.ps1, re-reads the same settings on
    the current host, and reports differences (firewall profile changes, local administrator
    additions/removals, RDP/SMB1 state changes). Output is a read-only drift report. Drift with
    no matching approved ChangeID (docs/14) is a potential unauthorized change - escalate to an
    issue (docs/15).

.GOVERNANCE
    Read-only. This script only compares and reports. It does not remediate drift, change any
    setting, or remove any account. Remediation stays a human-approved change-management action.

.NOTES
    Part of grc-automation-toolkit. Convention: ../../CONVENTIONS.md. Walkthrough: ../../DIY-GUIDE.md.
    Edit the CHANGE ME block below before first run (Ctrl+F -> CHANGE_ME).
    Run elevated so all settings are readable.
#>

[CmdletBinding()]
param(
    [string]$BaselinePath,
    [string]$ReportPath
)

# vvv CHANGE ME vvv ---------------------------------------------------------
if (-not $BaselinePath) {
    $BaselinePath = "<<CHANGE_ME: \\fileserver\GRC\04_Evidence\config\baseline-$env:COMPUTERNAME.json>>"  # CHANGE ME
}
if (-not $ReportPath) {
    $ReportPath   = "<<CHANGE_ME: \\fileserver\GRC\00_Admin\reports\config-drift-$env:COMPUTERNAME.txt>>"     # CHANGE ME
}
# ^^^ CHANGE ME ^^^ ---------------------------------------------------------

if (-not (Test-Path $BaselinePath)) {
    throw "Baseline not found at $BaselinePath. Run Get-ConfigBaseline.ps1 first."
}

$base = Get-Content $BaselinePath -Raw | ConvertFrom-Json
$driftReport = New-Object System.Collections.Generic.List[string]
$driftReport.Add("Config drift report for $env:COMPUTERNAME at $(Get-Date -Format s)")
$driftReport.Add("Baseline captured: $($base.CapturedAt)")
$driftReport.Add("")

# --- Firewall profiles must stay enabled -----------------------------------
foreach ($p in (Get-NetFirewallProfile)) {
    $b = $base.FirewallProfiles | Where-Object Name -eq $p.Name
    if ($b -and $b.Enabled -ne $p.Enabled) {
        $driftReport.Add("FIREWALL DRIFT: $($p.Name) was $($b.Enabled) now $($p.Enabled)")
    }
}

# --- Local administrators group membership changed --------------------------
$currentAdmins = (Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue).Name
$baseAdmins    = $base.LocalAdmins.Name
$added   = $currentAdmins | Where-Object { $_ -notin $baseAdmins }
$removed = $baseAdmins    | Where-Object { $_ -notin $currentAdmins }
if ($added)   { $driftReport.Add("ADMIN ADDED: "   + ($added   -join ", ")) }
if ($removed) { $driftReport.Add("ADMIN REMOVED: " + ($removed -join ", ")) }

# --- RDP / SMB1 state ------------------------------------------------------
$rdpNow = (Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" -ErrorAction SilentlyContinue).fDenyTSConnections
if ($base.RDPEnabled -ne $null -and $base.RDPEnabled -ne $rdpNow) {
    $driftReport.Add("RDP DRIFT: fDenyTSConnections was $($base.RDPEnabled) now $rdpNow")
}
$smbNow = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue).State
if ($base.SMB1 -and $base.SMB1 -ne $smbNow) {
    $driftReport.Add("SMB1 DRIFT: was $($base.SMB1) now $smbNow")
}

# --- Output ----------------------------------------------------------------
if ($driftReport.Count -le 3) {
    $driftReport.Add("No drift detected against baseline.")
}
$dir = Split-Path -Parent $ReportPath
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
$driftReport | Tee-Object -FilePath $ReportPath
Write-Host "Drift report written to $ReportPath"
