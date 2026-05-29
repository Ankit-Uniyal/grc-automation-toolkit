<#
.SYNOPSIS
    Registers the recurring GRC automation jobs in Windows Task Scheduler.
.DESCRIPTION
    Creates weekly scheduled tasks that run the toolkit PowerShell scripts under
    a dedicated least-privilege service account. Run ONCE, as an administrator.

    >>> BEFORE YOU RUN: edit the values in the 'CHANGE ME' block below. <<<
    Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B1/B12).
.NOTES
    Store the service-account credential via Windows Credential Manager / DPAPI.
    NEVER place passwords in this script. The principal below uses a stored
    credential or a gMSA - adjust LogonType to suit your environment.
.EXAMPLE
    # Run elevated. You will be prompted to confirm before tasks are created.
    pwsh ./Register-GrcTasks.ps1 -ServiceAccount "DOMAIN\svc-grc"
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $ToolkitRoot,
    [string] $ServiceAccount
)

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Replace each <<CHANGE_ME: ...>> token (keep the quotes).
# ----------------------------------------------------------------------------

# Folder that holds the toolkit's PowerShell scripts:
if (-not $ToolkitRoot) {
    $ToolkitRoot = '<<CHANGE_ME: \\fileserver\GRC\toolkit\scripts\powershell>>'   # CHANGE ME
}

# Domain service account that will run the tasks (least privilege):
if (-not $ServiceAccount) {
    $ServiceAccount = '<<CHANGE_ME: DOMAIN\svc-grc>>'                                # CHANGE ME
}

# Path to your live control matrix and evidence root (used as task arguments):
$ControlMatrix = '<<CHANGE_ME: \\fileserver\GRC\registers\control-matrix.csv>>'     # CHANGE ME
$EvidenceRoot  = '<<CHANGE_ME: \\fileserver\GRC\evidence>>'                          # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

function New-GrcTask {
    param([string]$Name, [string]$Script, [string]$ScriptArgs, [string]$DayOfWeek = 'Monday', [string]$At = '08:00')
    $file = Join-Path $ToolkitRoot $Script
    $action = New-ScheduledTaskAction -Execute 'pwsh.exe' -Argument ("-NoProfile -File `"{0}`" {1}" -f $file, $ScriptArgs)
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DayOfWeek -At $At
    # gMSA recommended; for a standard service account use -LogonType Password (credential stored securely)
    $principal = New-ScheduledTaskPrincipal -UserId $ServiceAccount -LogonType Password -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    if ($PSCmdlet.ShouldProcess($Name, "Register scheduled task")) {
        Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
        Write-Host "Registered task: $Name"
    }
}

# --- Weekly jobs ---
New-GrcTask -Name 'GRC-Weekly-ControlReminders' -Script 'Send-ComplianceReminders.ps1' `
    -ScriptArgs ("-RegisterPath `"{0}`"" -f $ControlMatrix) -DayOfWeek Monday -At '08:00'

New-GrcTask -Name 'GRC-Weekly-EvidenceCollection' -Script 'Invoke-EvidenceCollection.ps1' `
    -ScriptArgs ("-EvidenceRoot `"{0}`"" -f $EvidenceRoot) -DayOfWeek Sunday -At '02:00'

Write-Host "Done. Review tasks in Task Scheduler under the root folder."
