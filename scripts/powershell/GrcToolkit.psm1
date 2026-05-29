<#
    GrcToolkit.psm1 - Shared helper module for the GRC Automation Toolkit.

    Import in any script with:
        Import-Module "\\fileserver\GRC\toolkit\scripts\powershell\GrcToolkit.psm1" -Force

    Provides one consistent foundation for every PowerShell automation:
      * Register I/O (CSV in/out, safe load)
      * Run logging
      * SHA-256 hashing / evidence manifests
      * Date helpers (next-due calculation, days-left, overdue test)
      * Notifications (Outlook COM, with graceful preview fallback)

    Collection/report only. Never deletes, disables, or changes permissions.
#>

function Get-GrcRegister {
    [CmdletBinding()] param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path $Path)) { throw "Register not found: $Path" }
    Import-Csv -Path $Path
}

function Save-GrcRegister {
    [CmdletBinding()] param([Parameter(Mandatory)]$Data, [Parameter(Mandatory)][string]$Path)
    $Data | Export-Csv -Path $Path -NoTypeInformation -Encoding UTF8
}

function Write-GrcLog {
    [CmdletBinding()] param([Parameter(Mandatory)][string]$Message, [string]$LogDir = (Join-Path $env:TEMP "grc-logs"))
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    $line = "{0}  {1}" -f (Get-Date -Format s), $Message
    $file = Join-Path $LogDir ("grc_{0}.log" -f (Get-Date -Format yyyy-MM-dd))
    $line | Tee-Object -FilePath $file -Append
}

function Get-GrcFileHash {
    [CmdletBinding()] param([Parameter(Mandatory)][string]$Path)
    (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

function Get-GrcNextDueDate {
    [CmdletBinding()] param([datetime]$From, [int]$FrequencyMonths)
    $From.AddMonths($FrequencyMonths).ToString("yyyy-MM-dd")
}

function Get-GrcDaysLeft {
    [CmdletBinding()] param([datetime]$DueDate, [datetime]$AsOf = (Get-Date))
    ($DueDate - $AsOf).Days
}

function Test-GrcOverdue {
    [CmdletBinding()] param([datetime]$DueDate, [datetime]$AsOf = (Get-Date))
    $DueDate -lt $AsOf
}

function Send-GrcNotification {
    <# Sends via Outlook COM if available; otherwise logs a preview (safe for testing). #>
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string]$To, [Parameter(Mandatory)][string]$Subject, [string]$Body = "")
    if ($PSCmdlet.ShouldProcess($To, $Subject)) {
        try {
            $ol = New-Object -ComObject Outlook.Application
            $mail = $ol.CreateItem(0)
            $mail.To = $To; $mail.Subject = $Subject; $mail.Body = $Body
            $mail.Send()
            Write-GrcLog "SENT -> $To : $Subject"
        } catch {
            Write-GrcLog "PREVIEW (no Outlook) -> $To : $Subject"
        }
    } else {
        Write-GrcLog "WHATIF -> would send to $To : $Subject"
    }
}

function New-GrcEvidence {
    <# Saves collector output to the quarter/control folder, hashes it, returns a manifest row. #>
    [CmdletBinding()]
    param([string]$EvidenceRoot, [string]$ControlID, [string]$Name, [scriptblock]$Collector)
    $quarter = "{0}\Q{1}" -f (Get-Date).Year, [math]::Ceiling((Get-Date).Month/3)
    $dir = Join-Path $EvidenceRoot "$quarter\$ControlID"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
    $file = Join-Path $dir "EVD_${ControlID}_${Name}_$stamp.txt"
    try { & $Collector 2>&1 | Out-String | Out-File $file -Encoding UTF8 }
    catch { "COLLECTION ERROR: $_" | Out-File $file -Encoding UTF8 }
    [pscustomobject]@{
        ControlID = $ControlID; Name = $Name; File = $file
        SHA256 = (Get-GrcFileHash $file); CollectedBy = $env:USERNAME
        CollectedFrom = $env:COMPUTERNAME; When = $stamp
    }
}

Export-ModuleMember -Function Get-GrcRegister, Save-GrcRegister, Write-GrcLog, `
    Get-GrcFileHash, Get-GrcNextDueDate, Get-GrcDaysLeft, Test-GrcOverdue, `
    Send-GrcNotification, New-GrcEvidence
