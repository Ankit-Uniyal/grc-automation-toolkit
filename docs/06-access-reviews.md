# 06 · Access Reviews & Joiner-Mover-Leaver Automation

> **Pillar:** Identity & access governance. User Access Reviews (UARs) are mandatory under almost every framework and are pure drudgery by hand. With on-prem Active Directory you can automate the entire data gathering, distribution, and reconciliation — leaving managers to do only the part that needs a human: deciding whether access is still appropriate.

---

## 1. What to automate

- **Access extraction** — pull current membership for every system/group from AD.
- **Review packs** — generate a per-manager spreadsheet of their reports' access.
- **Distribution & chase** — send packs, track sign-off, chase non-responders.
- **Reconciliation** — diff this review vs. last review; flag what changed.
- **JML detection** — joiners without onboarding, leavers still enabled, movers with accumulated access.
- **Orphan/stale detection** — accounts with no owner or no recent logon.

## 2. The automation

### 2a. Extract access from Active Directory (PowerShell)

```powershell
# scripts/powershell/Export-AccessSnapshot.ps1
param([string]$OutDir = "\\fileserver\GRC\04_Evidence\AccessReviews")
$stamp = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

Get-ADUser -Filter {Enabled -eq $true} -Properties Department,Manager,Title,LastLogonDate,whenCreated |
  Select SamAccountName,Name,Department,Title,
    @{n='Manager';e={(Get-ADUser $_.Manager).SamAccountName}},
    LastLogonDate,whenCreated |
  Export-Csv "$OutDir\users_$stamp.csv" -NoTypeInformation

$rows = foreach ($g in Get-ADGroup -Filter *) {
  Get-ADGroupMember $g.Name -ErrorAction SilentlyContinue |
    ForEach-Object { [pscustomobject]@{ Group=$g.Name; Member=$_.SamAccountName } }
}
$rows | Export-Csv "$OutDir\group_membership_$stamp.csv" -NoTypeInformation
```

### 2b. Build per-manager review packs (Python)

Use `scripts/python/build_uar_packs.py` — it merges users + group membership and writes one `UAR_<manager>_<period>.xlsx` per manager with empty Keep/Revoke columns, then (with `--prev`) reconciles against the previous snapshot.

```bash
python build_uar_packs.py users_2026-06-01.csv group_membership_2026-06-01.csv \
    --prev group_membership_2026-03-01.csv --period 2026Q2
```

"New grants since last review" (`uar_added.csv`) is exactly what auditors ask for — now one command.

### 2c. JML & hygiene detections (PowerShell)

```powershell
# Leavers still enabled (HR-terminated list vs AD-enabled)
$termed = Import-Csv "\\fileserver\GRC\hr\leavers.csv"
foreach ($t in $termed) {
  $u = Get-ADUser -Filter "SamAccountName -eq '$($t.SamAccountName)'" -Properties Enabled
  if ($u.Enabled) { "LEAVER STILL ENABLED: $($u.SamAccountName)" }
}

# Stale / never-logged-on accounts
Get-ADUser -Filter {Enabled -eq $true} -Properties LastLogonDate |
  Where-Object { $_.LastLogonDate -lt (Get-Date).AddDays(-90) -or -not $_.LastLogonDate } |
  Select SamAccountName, LastLogonDate
```

Feed the snapshot into `sod_check.py` (docs/20) to detect toxic role combinations at the same time.

> **Important:** these scripts **report** access for human decision. Actually disabling/removing accounts is an IT operations action that should go through your change process — automate the *detection and review*, not the irreversible *deprovisioning*.

## 3. Scheduling & ownership

- **Owner:** IAM / IT Security; **Reviewers:** line managers; **Oversight:** GRC.
- Snapshot + leaver/stale checks **weekly**; full manager review cycle **quarterly**.

## 4. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Extraction | Manual AD exports | Scheduled snapshots |
| Review packs | One big spreadsheet | Auto per-manager packs |
| Reconciliation | None | Auto diff vs. prior review |
| JML | Manual checks | Automated leaver/stale detection |

**Next:** `docs/07-vendor-risk.md`
