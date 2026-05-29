<#
.SYNOPSIS
    Reports overdue risk treatment actions and risks past their review cadence.

.DESCRIPTION
    Reads the risk register CSV and produces two read-only reports:
      1. Treatment actions that are not Closed and whose ActionDueDate is in the past.
      2. Risks whose LastReviewed + ReviewFrequencyMonths is in the past (review overdue).
    Optionally emails each risk owner via Outlook (use -Notify). Nothing is changed in the
    register; this script only reports and notifies. Pipe the overdue list into the same
    reminder pattern documented in docs/02-policy-management.md to nudge owners.

.GOVERNANCE
    Report / collect / track / notify only. This script never edits the register, never
    closes actions, never accepts risk, and never approves anything. Human judgement stays human.

.NOTES
    Part of grc-automation-toolkit. Convention: ../../CONVENTIONS.md. Walkthrough: ../../DIY-GUIDE.md.
    Edit the CHANGE ME block below before first run (Ctrl+F -> CHANGE_ME).
#>

[CmdletBinding()]
param(
    [string]$RegisterPath,
    [string]$OutputCsv,
    [switch]$Notify
)

# vvv CHANGE ME vvv ---------------------------------------------------------
# Replace each <<CHANGE_ME: ...>> token with your real value (keep the quotes).
if (-not $RegisterPath) {
    $RegisterPath = "<<CHANGE_ME: \\fileserver\GRC\registers\risk-register.csv>>"  # CHANGE ME
}
if (-not $OutputCsv) {
    $OutputCsv    = "<<CHANGE_ME: \\fileserver\GRC\reports\overdue-risk-actions.csv>>" # CHANGE ME
}
# Mailbox / sender used only when -Notify is supplied:
$FromMailbox     = "<<CHANGE_ME: grc@yourcompany.com>>"   # CHANGE ME (-Notify only)
# ^^^ CHANGE ME ^^^ ---------------------------------------------------------

if (-not (Test-Path $RegisterPath)) {
    throw "Risk register not found at $RegisterPath. Edit the CHANGE ME block."
}

$today = Get-Date
$rows  = Import-Csv $RegisterPath

# --- 1. Overdue treatment actions ------------------------------------------
$overdue = $rows |
    Where-Object {
        $_.Status -ne 'Closed' -and
        $_.ActionDueDate -and
        [datetime]$_.ActionDueDate -lt $today
    } |
    Select-Object RiskID, Title, Owner, Treatment, ActionDueDate,
        @{ N = 'DaysOverdue'; E = { ($today - [datetime]$_.ActionDueDate).Days } } |
    Sort-Object ActionDueDate

# --- 2. Review-aging check -------------------------------------------------
$reviewOverdue = $rows |
    Where-Object { $_.LastReviewed -and $_.ReviewFrequencyMonths } |
    ForEach-Object {
        $due = ([datetime]$_.LastReviewed).AddMonths([int]$_.ReviewFrequencyMonths)
        if ($due -lt $today) {
            [pscustomobject]@{
                RiskID      = $_.RiskID
                Title       = $_.Title
                Owner       = $_.Owner
                LastReviewed= $_.LastReviewed
                ReviewDue   = $due.ToString('yyyy-MM-dd')
            }
        }
    }

# --- Output ----------------------------------------------------------------
Write-Host ("Overdue treatment actions : {0}" -f @($overdue).Count)
Write-Host ("Risks overdue for review  : {0}" -f @($reviewOverdue).Count)

if (@($overdue).Count -gt 0) {
    $overdue | Format-Table -AutoSize
    $overdue | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8
    Write-Host "Overdue report written to $OutputCsv"
}
if (@($reviewOverdue).Count -gt 0) {
    $reviewOverdue | Format-Table -AutoSize
}

# --- Optional owner notification (read-only nudge) -------------------------
if ($Notify -and @($overdue).Count -gt 0) {
    try {
        $outlook = New-Object -ComObject Outlook.Application
        foreach ($g in ($overdue | Group-Object Owner)) {
            $mail = $outlook.CreateItem(0)
            $mail.To      = $g.Name
            $mail.Subject = "Overdue risk treatment actions ($($g.Count))"
            $lines = $g.Group | ForEach-Object { "- $($_.RiskID) $($_.Title) - due $($_.ActionDueDate)" }
            $mail.Body = "The following risk treatment actions are past their due date:`n`n" + ($lines -join "`n") + "`n`nThis is an automated reminder. Please update the register."
            $mail.Save()   # saved to Drafts for human review; remove .Save and use .Send to auto-send
        }
        Write-Host "Reminder drafts created in Outlook for $FromMailbox."
    } catch {
        Write-Warning "Outlook notification skipped: $($_.Exception.Message)"
    }
}
