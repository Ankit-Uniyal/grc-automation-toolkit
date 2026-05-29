<#
.SYNOPSIS
    Collects standard technical control evidence from a Windows/AD environment,
    files it by control & quarter, hashes each artifact (SHA-256), and writes a
    tamper-evident manifest (chain of custody).
.DESCRIPTION
    Designed for non-cloud environments. Each collector is a small scriptblock so
    you can add/remove evidence items easily.

    >>> BEFORE YOU RUN: edit the values in the 'CHANGE ME' block below. <<<
    Every value you must set for YOUR environment is tagged with  # CHANGE ME
    and uses a <<CHANGE_ME: ...>> token. Search this file for CHANGE_ME.
    See CONVENTIONS.md and DIY-GUIDE.md (task B3) for step-by-step help.
.NOTES
    Governance rule: COLLECTION ONLY. This script never changes system state,
    never deletes, and never modifies permissions. Run under svc-grc with
    READ-ONLY rights wherever possible. Some collectors require the AD module.
#>
[CmdletBinding()]
param(
    [string] $EvidenceRoot
)

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Replace the whole <<CHANGE_ME: ...>> token (keep the quotes). Used only if
# you do not pass -EvidenceRoot on the command line.
# ----------------------------------------------------------------------------

if (-not $EvidenceRoot) {
    $EvidenceRoot = '<<CHANGE_ME: \\fileserver\GRC\04_Evidence>>'   # CHANGE ME
}

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

$quarter = "{0}\Q{1}" -f (Get-Date).Year, [math]::Ceiling((Get-Date).Month/3)

function Save-Evidence {
    param([string]$ControlID, [string]$Name, [scriptblock]$Collector)
    $dir = Join-Path $EvidenceRoot "$quarter\$ControlID"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $stamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
    $file = Join-Path $dir ("EVD_{0}_{1}_{2}.txt" -f $ControlID, $Name, $stamp)
    try { & $Collector 2>&1 | Out-String | Out-File $file -Encoding UTF8 }
    catch { "COLLECTION ERROR: $_" | Out-File $file -Encoding UTF8 }
    $hash = (Get-FileHash $file -Algorithm SHA256).Hash
    [pscustomobject]@{
        ControlID     = $ControlID
        Name          = $Name
        File          = $file
        SHA256        = $hash
        CollectedBy   = $env:USERNAME
        CollectedFrom = $env:COMPUTERNAME
        When          = $stamp
    }
}

# --- Define the evidence collectors (extend as needed) ---
$manifest = @()
$manifest += Save-Evidence 'CTRL-AC-001' 'DomainAdmins' { Get-ADGroupMember 'Domain Admins' | Select-Object Name, SamAccountName }
$manifest += Save-Evidence 'CTRL-AC-002' 'PasswordPolicy' { Get-ADDefaultDomainPasswordPolicy }
$manifest += Save-Evidence 'CTRL-EP-001' 'BitLocker' { Get-BitLockerVolume | Select-Object MountPoint, ProtectionStatus, EncryptionMethod }
$manifest += Save-Evidence 'CTRL-EP-002' 'Antivirus' { Get-MpComputerStatus | Select-Object AMRunningMode, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated }
$manifest += Save-Evidence 'CTRL-NW-001' 'Firewall' { Get-NetFirewallProfile | Select-Object Name, Enabled }
$manifest += Save-Evidence 'CTRL-VM-001' 'Patches' { Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 50 HotFixID, InstalledOn }
$manifest += Save-Evidence 'CTRL-AC-STALE' 'StaleAccounts' {
    Get-ADUser -Filter {Enabled -eq $true} -Properties LastLogonDate |
        Where-Object { $_.LastLogonDate -lt (Get-Date).AddDays(-90) } |
        Select-Object SamAccountName, LastLogonDate
}

# --- Append to the manifest (append-only chain of custody) ---
$manifestPath = Join-Path $EvidenceRoot "$quarter\_manifest.csv"
$manifest | Export-Csv $manifestPath -Append -NoTypeInformation

Write-Host "Collected $($manifest.Count) evidence items for $quarter"
Write-Host "Manifest: $manifestPath"
