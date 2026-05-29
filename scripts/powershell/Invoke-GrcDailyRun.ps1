<#
.SYNOPSIS
    Master orchestrator - runs the recurring GRC automations in one pass.
.DESCRIPTION
    A single entry point you can schedule daily/weekly. It runs the PowerShell
    reminders/collection and the Python monitors (metrics, issues, incidents,
    vulns, SoD), writing all outputs to the registers area and logging the run.

    All steps are report/collect/notify only - nothing is deleted or changed.
.PARAMETER GrcRoot
    Root of the GRC share (registers live under here).
.PARAMETER ToolkitRoot
    Root of this toolkit (scripts live under here).
.EXAMPLE
    pwsh ./Invoke-GrcDailyRun.ps1 -GrcRoot "\\fileserver\GRC" -WhatIf
.NOTES
    Run under svc-grc. Python steps require python on PATH and grclib importable
    (run them from the registers folder so relative CSV paths resolve).
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $GrcRoot = "\\fileserver\GRC",
    [string] $ToolkitRoot = "\\fileserver\GRC\toolkit"
)

Import-Module (Join-Path $ToolkitRoot "scripts\powershell\GrcToolkit.psm1") -Force
$registers = Join-Path $GrcRoot "registers"
$py = Join-Path $ToolkitRoot "scripts\python"

Write-GrcLog "=== GRC daily run start ===" -LogDir (Join-Path $GrcRoot "00_Admin\logs")

# 1) PowerShell: control test reminders
if ($PSCmdlet.ShouldProcess("control reminders", "send")) {
    & (Join-Path $ToolkitRoot "scripts\powershell\Send-ComplianceReminders.ps1") `
        -RegisterPath (Join-Path $registers "control-matrix.csv")
}

# 2) PowerShell: evidence collection (technical CCM)
if ($PSCmdlet.ShouldProcess("evidence collection", "run")) {
    & (Join-Path $ToolkitRoot "scripts\powershell\Invoke-EvidenceCollection.ps1") `
        -EvidenceRoot (Join-Path $GrcRoot "04_Evidence")
}

# 3) Python monitors - run from the registers folder so CSV paths resolve
$pyJobs = @(
    "grc_metrics.py",
    "issue_tracker.py",
    "incident_monitor.py",
    "vuln_sla.py"
)
Push-Location $registers
try {
    $env:PYTHONPATH = $py
    foreach ($job in $pyJobs) {
        $script = Join-Path $py $job
        if ($PSCmdlet.ShouldProcess($job, "python run")) {
            Write-GrcLog "Running $job" -LogDir (Join-Path $GrcRoot "00_Admin\logs")
            python $script
        }
    }
} finally { Pop-Location }

Write-GrcLog "=== GRC daily run complete ===" -LogDir (Join-Path $GrcRoot "00_Admin\logs")
Write-Host "Done. Review outputs in $registers and the alerts CSVs."
