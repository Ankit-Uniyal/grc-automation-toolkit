<#
.SYNOPSIS
    Sends reminders for GRC control tests that are due or overdue.
.DESCRIPTION
    Reads the control matrix CSV, finds controls whose NextTestDate is within
    -WarnDays (or already overdue), and emails the assigned Tester.
    Supports -WhatIf for a safe preview before sending anything.

    >>> BEFORE YOU RUN: edit the values in the 'CHANGE ME' block below. <<<
    Every value you must set for YOUR environment is tagged with  # CHANGE ME
    and uses a <<CHANGE_ME: ...>> token. Search this file for CHANGE_ME.
    See CONVENTIONS.md and DIY-GUIDE.md (task B1) for step-by-step help.
.NOTES
    Governance rule: this script only NOTIFIES. It never changes access, data, or controls.
    Run under a dedicated least-privilege service account (svc-grc).
    Never hard-code passwords. Use Windows Credential Manager (see DIY-GUIDE A5).
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $RegisterPath,
    [int]    $WarnDays = 14,
    [string] $LogDir
)

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Set these to match YOUR environment. Replace the whole <<CHANGE_ME: ...>>
# token (keep the surrounding quotes). These are used if you do not pass the
# matching -Parameter on the command line.
# ----------------------------------------------------------------------------

# Path to your live control matrix (the source of truth):
if (-not $RegisterPath) {
    $RegisterPath = '<<CHANGE_ME: \\fileserver\GRC\registers\control-matrix.csv>>'   # CHANGE ME
}

# Sender mailbox shown on the reminder emails:
$FromAddress = '<<CHANGE_ME: grc-bot@yourcompany.local>>'                     # CHANGE ME

# Internal SMTP relay (only used if Outlook is not installed on this machine):
$SmtpServer  = '<<CHANGE_ME: smtp.yourcompany.local>>'                        # CHANGE ME
$SmtpPort    = 25                                                            # CHANGE ME (usually 25 or 587)

# How many days BEFORE the due date to start reminding:
if (-not $PSBoundParameters.ContainsKey('WarnDays')) { $WarnDays = 14 }   # CHANGE ME (optional)

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

if (-not (Test-Path $RegisterPath)) { throw "Register not found: $RegisterPath" }
if (-not $LogDir) { $LogDir = Join-Path (Split-Path $RegisterPath) 'logs' }
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$log = Join-Path $LogDir ("reminders_{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))

function Write-Log { param($m) "$(Get-Date -Format s) $m" | Tee-Object -FilePath $log -Append }

$today = Get-Date
$rows  = Import-Csv $RegisterPath
$due = foreach ($r in $rows) {
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
    Write-Log "INFO: Outlook COM not available; will use SMTP relay $SmtpServer instead."
}

foreach ($d in $due) {
    $subject = "[GRC] Control $($d.ControlID) test $($d.State)"
    $body = @"
Control: $($d.Title) ($($d.ControlID))
Tester:  $($d.Tester)
Owner:   $($d.Owner)
Due date: $($d.NextTestDate) ($($d.State))

Please perform the test, record the result in the control matrix, and file evidence
in the current quarter's evidence folder following the naming convention.
(Automated reminder - do not reply to this mailbox.)
"@
    if ($PSCmdlet.ShouldProcess("$($d.Tester) <$($d.ControlID)>", "Send reminder: $subject")) {
        if ($outlook) {
            $mail = $outlook.CreateItem(0)
            $mail.To = $d.Tester
            $mail.Subject = $subject
            $mail.Body = $body
            $mail.Send()
            Write-Log "SENT (Outlook) -> $($d.Tester) [$($d.ControlID)] $($d.State)"
        } else {
            Send-MailMessage -To $d.Tester -From $FromAddress -Subject $subject `
                -Body $body -SmtpServer $SmtpServer -Port $SmtpPort -ErrorAction Stop
            Write-Log "SENT (SMTP) -> $($d.Tester) [$($d.ControlID)] $($d.State)"
        }
    } else {
        Write-Log "WHATIF -> would send to $($d.Tester) [$($d.ControlID)] $subject"
    }
}

Write-Log "Run complete."
