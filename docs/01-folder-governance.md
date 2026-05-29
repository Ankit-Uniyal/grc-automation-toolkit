# 01 · Folder Governance & File Discipline

> **Pillar:** Foundation. Everything else in this toolkit assumes a clean, predictable storage layout. Do this first.

In a non-cloud shop, your shared drive / OneDrive / SharePoint library **is** your GRC system of record. If it is chaotic, no automation can run reliably (scripts can't find files, evidence can't be tied to controls, auditors waste days). This pillar turns the share into a structured, scriptable "database."

---

## 1. What to automate

- Enforcing a **standard folder taxonomy** across the GRC area.
- Enforcing a **file-naming convention** so scripts can parse metadata from names.
- **Versioning & retention** (keep history, archive the old, purge nothing without approval).
- **Detecting drift** — rogue folders, misnamed files, stale documents, duplicates.
- **Permissions hygiene** — who can read/write each area.

## 2. The standard taxonomy

Stand this up at `\\fileserver\GRC\` (or `OneDrive\GRC\`). Keep it shallow and predictable:

```
GRC/
├─ 00_Admin/                 Program charter, RACI, calendar, this toolkit
├─ 01_Policies/              Approved policies + /drafts + /archive
├─ 02_Risk/                  risk-register.xlsx, assessments, treatment plans
├─ 03_Controls/              control-matrix.xlsx, test plans, test results
├─ 04_Evidence/             Year/quarter folders, write-once, hashed
│  └─ 2026/Q1/CTRL-AC-001/
├─ 05_Assets/                asset-inventory.xlsx, data flow maps
├─ 06_Vendors/               vendor-register.xlsx, due-diligence packs
├─ 07_Audits/                Internal & external audit binders by year
├─ 08_Incidents/             Incident log + post-incident reviews
└─ 99_Archive/               Retired documents (never deleted ad-hoc)
```

## 3. File-naming convention

```
<DOMAIN>_<ID>_<ShortTitle>_v<Major.Minor>_<YYYY-MM-DD>.<ext>
```

Examples:

- `POL_ISMS-001_AccessControlPolicy_v2.1_2026-03-01.docx`
- `EVD_CTRL-AC-001_DomainAdminsExport_v1.0_2026-04-15.csv`
- `RA_RISK-014_RansomwareAssessment_v1.3_2026-02-10.xlsx`

Because metadata lives **in the name**, PowerShell/Python can index everything without opening a single file.

## 4. The automation

### 4a. Scaffold the taxonomy (PowerShell)

```powershell
# scripts/powershell/New-GrcFolderTree.ps1
param([string]$Root = "\\fileserver\GRC")
$tree = @(
  "00_Admin","01_Policies\drafts","01_Policies\archive","02_Risk",
  "03_Controls","04_Evidence","05_Assets","06_Vendors","07_Audits",
  "08_Incidents","99_Archive"
)
foreach ($d in $tree) {
  $p = Join-Path $Root $d
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null; "Created $p" }
}
```

### 4b. Detect naming / structure drift (PowerShell)

```powershell
# scripts/powershell/Test-FileNaming.ps1  — flags files that break the convention
param([string]$Root = "\\fileserver\GRC")
$pattern = '^(POL|RA|EVD|CTRL|VEN|AUD)_[A-Za-z0-9\-]+_.+_v\d+\.\d+_\d{4}-\d{2}-\d{2}\.[A-Za-z0-9]+$'
Get-ChildItem $Root -Recurse -File |
  Where-Object { $_.Name -notmatch $pattern } |
  Select-Object FullName, @{n='LastWrite';e={$_.LastWriteTime}} |
  Export-Csv "$Root\00_Admin\naming-violations.csv" -NoTypeInformation
```

### 4c. Find stale documents (review-overdue)

```powershell
# Flags anything not updated in > 365 days for review
Get-ChildItem "\\fileserver\GRC\01_Policies" -Recurse -File |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-365) } |
  Sort-Object LastWriteTime |
  Select-Object Name, LastWriteTime, Directory
```

### 4d. Duplicate / integrity detection (hash)

```powershell
Get-ChildItem "\\fileserver\GRC\04_Evidence" -Recurse -File |
  Get-FileHash -Algorithm SHA256 |
  Group-Object Hash | Where-Object Count -gt 1 |
  ForEach-Object { $_.Group.Path }
```

## 5. Versioning & retention

- **OneDrive/SharePoint:** turn on **version history** in library settings — it is free and gives you rollback + audit trail. Set major+minor versioning for the `01_Policies` library.
- **Plain file server:** keep `/drafts` and `/archive` subfolders; the naming convention's version token preserves lineage. Move superseded files to `99_Archive` (never delete) — automate the move but **require human approval** before purges.
- Document a **retention schedule** in `00_Admin` (e.g. evidence retained 7 years, drafts 1 year).

## 6. Permissions hygiene

- `04_Evidence` should be **write-once**: contributors can add, only the GRC lead can modify/delete. On a Windows file server use NTFS permissions; on SharePoint use library permission levels.
- Export current ACLs for review (read-only):
  ```powershell
  (Get-Acl "\\fileserver\GRC\04_Evidence").Access |
    Select IdentityReference, FileSystemRights, AccessControlType
  ```
- **Note:** *changing* permissions is a governance decision — make the change yourself through your IT process; scripts here only **report** on permissions.

## 7. Scheduling & ownership

- **Owner:** GRC Analyst.
- Run `Test-FileNaming.ps1` and the stale-doc check **weekly** via Task Scheduler; email the violation CSV to the owner (see `docs/04-control-testing.md` for the scheduling recipe).

## 8. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Structure | Manual folder tree + naming guide | Auto-scaffolded, drift-detected weekly |
| Versioning | Manual archive | Library versioning + automated archive-on-supersede |
| Integrity | None | SHA-256 manifests + duplicate detection |

**Next:** `docs/02-policy-management.md`
