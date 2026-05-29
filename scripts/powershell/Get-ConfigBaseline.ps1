<#
.SYNOPSIS
    Captures a read-only security configuration baseline of a Windows host as JSON.

.DESCRIPTION
    Snapshots key security settings (firewall, automatic services, local administrators,
    password policy, RDP, SMB1) into a machine-readable baseline.json. Run this once on an
    approved/hardened host to record the standard, then use Compare-ConfigDrift.ps1 on a
    schedule to detect drift away from this baseline.

.GOVERNANCE
    Read-only. This script only reads and records settings. It does not change firewall
    rules, services, accounts, or any configuration.

.NOTES
    Part of grc-automation-toolkit. Convention: ../../CONVENTIONS.md. Walkthrough: ../../DIY-GUIDE.md.
    Edit the CHANGE ME block below before first run (Ctrl+F -> CHANGE_ME).
    Run in an elevated PowerShell session so all settings are readable.
#>

[CmdletBinding()]
param(
    [string]$OutFile
)

# vvv CHANGE ME vvv ---------------------------------------------------------
# Where to write the baseline snapshot. Keep one file per host.
if (-not $OutFile) {
    $OutFile = "<<CHANGE_ME: \\fileserver\GRC\04_Evidence\config\baseline-$env:COMPUTERNAME.json>>"  # CHANGE ME
}
# ^^^ CHANGE ME ^^^ ---------------------------------------------------------

$baseline = [ordered]@{
    Host       = $env:COMPUTERNAME
    CapturedAt = (Get-Date -Format s)
    FirewallProfiles   = (Get-NetFirewallProfile | Select-Object Name, Enabled)
    Services_Automatic = (Get-Service | Where-Object StartType -eq "Automatic" |
                            Select-Object Name, Status)
    LocalAdmins  = (Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue |
                        Select-Object Name)
    PasswordPolicy = (net accounts)
    RDPEnabled = (Get-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" -ErrorAction SilentlyContinue).fDenyTSConnections
    SMB1 = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue).State
}

# Ensure the output folder exists, then write hashed, dated evidence.
$dir = Split-Path -Parent $OutFile
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

$baseline | ConvertTo-Json -Depth 5 | Out-File $OutFile -Encoding UTF8
Write-Host "Baseline written to $OutFile"

# Record a SHA-256 alongside the snapshot so tampering is detectable.
try {
    $hash = (Get-FileHash -Path $OutFile -Algorithm SHA256).Hash
    "$hash  $(Split-Path -Leaf $OutFile)" | Out-File "$OutFile.sha256" -Encoding ASCII
    Write-Host "SHA-256: $hash"
} catch {
    Write-Warning "Could not hash baseline: $($_.Exception.Message)"
}
