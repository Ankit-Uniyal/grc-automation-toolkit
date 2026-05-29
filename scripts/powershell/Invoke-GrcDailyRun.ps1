<#
.SYNOPSIS
    Master orchestrator - runs the recurring GRC automations in one pass.
.DESCRIPTION
    A single entry point you can schedule daily/weekly. It runs the PowerShell
    reminders/collection and the Python monitors (metrics, issues, incidents,
    vulns), writing all outputs to the registers area and logging the run.
    All steps are report/collect/notify only - nothing is deleted or changed.

    >>> BEFORE YOU RUN: edit the values in the 'CHANGE ME' block below. <<<
    Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B12).
.NOTES
    Run under svc-grc. Python steps require python on PATH and grclib importable
    (this script runs them from the registers folder so relative CSV paths resolve).
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $GrcRoot,
    [string] $ToolkitRoot
)

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Replace each <<CHANGE_ME: ...>> token (keep the quotes). Used only if you do
# not pass the matching -Parameter on the command line.
# ----------------------------------------------------------------------------

# Root of your GRC share (the 'registers', 'evidence', 'logs' folders live here):
if (-not $GrcRoot)     { $GrcRoot     = '<<CHANGE_ME: \\fileserver\GRC>>' }          # CHANGE ME

# Root of this toolkit (the 'scripts' folder lives here):
if (-not $ToolkitRoot) { $ToolkitRoot = '<<CHANGE_ME: \\fileserver\GRC\toolkit>>' }  # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

Import-Module (Join-Path $ToolkitRoot "scripts\powershell\GrcToolkit.psm1") -Force
$registers = Join-Path $GrcRoot "registers"
$logs      = Join-Path $GrcRoot "logs"
$evidence  = Join-Path $GrcRoot "evidence"
$py        = Join-Path $ToolkitRoot "scripts\python"

Write-GrcLog "=== GRC daily run start ===" -LogDir $logs

# 1) PowerShell: control test reminders
if ($PSCmdlet.ShouldProcess("control reminders", "send")) {
    & (Join-Path $ToolkitRoot "scripts\powershell\Send-ComplianceReminders.ps1") `
        -RegisterPath (Join-Path $registers "control-matrix.csv")
}

# 2) PowerShell: evidence collection (technical CCM)
if ($PSCmdlet.ShouldProcess("evidence collection", "run")) {
    & (Join-Path $ToolkitRoot "scripts\powershell\Invoke-EvidenceCollection.ps1") `
        -EvidenceRoot $evidence
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
        $scriptFile = Join-Path $py $job
        if ($PSCmdlet.ShouldProcess($job, "python run")) {
            Write-GrcLog "Running $job" -LogDir $logs
            python $scriptFile
        }
    }
} finally { Pop-Location }

Write-GrcLog "=== GRC daily run complete ===" -LogDir $logs
Write-Host "Done. Review outputs in $registers and the alerts CSVs."
