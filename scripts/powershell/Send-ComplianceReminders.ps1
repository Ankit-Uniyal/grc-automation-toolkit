<#
.SYNOPSIS
    Sends reminders for GRC control tests that are due or overdue.
.DESCRIPTION
    Reads the control matrix CSV, finds controls whose NextTestDate is within
    -WarnDays (or already overdue), and emails the assigned Tester via Outlook.
    Supports -WhatIf for a safe preview before sending anything.
.PARAMETER RegisterPath
    UNC/local path to control-matrix.csv (the source of truth).
.PARAMETER WarnDays
    Days ahead of the due date to start warning. Default 14.
.PARAMETER LogDir
    Directory for the run log. Default 00_Admin\logs under the register root.
.EXAMPLE
    pwsh ./Send-ComplianceReminders.ps1 -RegisterPath "\\fileserver\GRC\03_Controls\control-matrix.csv" -WhatIf
.NOTES
    Run under a dedicated least-privilege service account (svc-grc).
    Never hard-code credentials. Requires Outlook installed for the COM object.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string] $RegisterPath,
    [int] $WarnDays = 14,
    [string] $LogDir
)

if (-not (Test-Path $RegisterPath)) { throw "Register not found: $RegisterPath" }
if (-not $LogDir) { $LogDir = Join-Path (Split-Path $RegisterPath) 'logs' }
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$log = Join-Path $LogDir ("reminders_{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))

function Write-Log { param($m) "$(Get-Date -Format s)  $m" | Tee-Object -FilePath $log -Append }

$today  = Get-Date
$rows   = Import-Csv $RegisterPath
$due    = foreach ($r in $rows) {
    if (-not $r.NextTestDate) { continue }
    $days = ([datetime]$r.NextTestDate - $today).Days
    if ($days -le $WarnDays) {
        [pscustomobject]@{
            ControlID = $r.ControlID; Title = $r.Title; Tester = $r.Tester
            Owner = $r.Owner; NextTestDate = $r.NextTestDate; DaysLeft = $days
            State = if ($days -lt 0) { "OVERDUE by $([math]::Abs($days))d" } else { "due in $days d" }
        }
    }
}

Write-Log "Found $($due.Count) controls within reminder window (WarnDays=$WarnDays)."
if (-not $due) { Write-Log "Nothing to send. Exiting."; return }

$outlook = $null
try { $outlook = New-Object -ComObject Outlook.Application } catch {
    Write-Log "WARNING: Outlook COM not available. Running in preview-only mode."
}

foreach ($d in $due) {
    $subject = "[GRC] Control $($d.ControlID) test $($d.State)"
    $body    = @"
Control:   $($d.Title) ($($d.ControlID))
Tester:    $($d.Tester)
Owner:     $($d.Owner)
Due date:  $($d.NextTestDate)  ($($d.State))

Please perform the test, record the result in the control matrix, and file evidence
in the current quarter's evidence folder following the naming convention.

(Automated reminder - do not reply to this mailbox.)
"@
    if ($PSCmdlet.ShouldProcess("$($d.Tester) <$($d.ControlID)>", "Send reminder: $subject")) {
        if ($outlook) {
            $mail = $outlook.CreateItem(0)
            $mail.To      = $d.Tester
            $mail.Subject = $subject
            $mail.Body    = $body
            $mail.Send()
            Write-Log "SENT  -> $($d.Tester)  [$($d.ControlID)]  $($d.State)"
        } else {
            Write-Log "PREVIEW (no Outlook) -> $($d.Tester)  [$($d.ControlID)]  $subject"
        }
    } else {
        Write-Log "WHATIF -> would send to $($d.Tester)  [$($d.ControlID)]  $subject"
    }
}

Write-Log "Run complete."
