<#
.SYNOPSIS
    Registers the recurring GRC automation jobs in Windows Task Scheduler.
.DESCRIPTION
    Creates weekly scheduled tasks that run the toolkit PowerShell scripts under
    a dedicated least-privilege service account. Run ONCE, as an administrator.
.PARAMETER ToolkitRoot
    Path to the scripts\powershell folder on the share.
.PARAMETER ServiceAccount
    Domain service account to run the tasks (e.g. DOMAIN\svc-grc).
.EXAMPLE
    # Run elevated. You will be prompted to confirm before tasks are created.
    pwsh ./Register-GrcTasks.ps1 -ServiceAccount "DOMAIN\svc-grc"
.NOTES
    Store the service-account credential via Windows Credential Manager / DPAPI.
    NEVER place passwords in this script. The principal below uses an interactive
    prompt or a gMSA - adjust LogonType to suit your environment.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $ToolkitRoot = "\\fileserver\GRC\toolkit\scripts\powershell",
    [Parameter(Mandatory)] [string] $ServiceAccount
)

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
        Write-Host "Registered task: "$Name
    }
}

# --- Weekly jobs (adjust paths/args to your registers) ---
New-GrcTask -Name 'GRC-Weekly-ControlReminders' -Script 'Send-ComplianceReminders.ps1' `
    -ScriptArgs '-RegisterPath "\\fileserver\GRC\03_Controls\control-matrix.csv"' -DayOfWeek Monday -At '08:00'

New-GrcTask -Name 'GRC-Weekly-EvidenceCollection' -Script 'Invoke-EvidenceCollection.ps1' `
    -ScriptArgs '-EvidenceRoot "\\fileserver\GRC\04_Evidence"' -DayOfWeek Sunday -At '02:00'

Write-Host "Done. Review tasks in Task Scheduler under the root folder."
