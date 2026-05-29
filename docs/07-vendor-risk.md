# 07 · Third-Party / Vendor Risk Automation

> **Pillar:** Supply-chain risk. Vendor risk in a manual shop usually means a folder of half-finished questionnaires and certificates nobody tracks the expiry of. You can automate the intake, scoring, reminders, and expiry monitoring entirely with Excel/CSV + scripts - no GRC SaaS required.

---

## 1. What to automate

- **Intake & tiering** - classify each vendor by criticality/data sensitivity.
- **Due-diligence tracking** - what was requested, received, and reviewed.
- **Certificate/attestation expiry** - flag SOC 2 / ISO 27001 certs before they lapse.
- **Reassessment cadence** - schedule periodic re-reviews by tier.
- **Reminders** - chase vendors and internal owners.

## 2. Data model - `vendor-register.csv`

| Column | Notes |
|---|---|
| VendorID | VEN-021 |
| Name | Acme Payroll Ltd |
| ServiceProvided | Payroll processing |
| DataAccessed | PII, financial |
| Tier | Critical / High / Medium / Low (auto from inputs) |
| Owner | HR Manager |
| LastAssessed | 2026-01-10 |
| ReassessFrequencyMonths | 12 |
| NextAssessment | auto |
| CertType | ISO27001 / SOC2 / None |
| CertExpiry | 2026-09-30 |
| Status | Approved / Conditional / Under Review |
| RiskScore | auto |

## 3. The automation

### 3a. Tiering & scoring (Python)

```python
# scripts/python/vendor_score.py
import pandas as pd
df = pd.read_csv("vendor-register.csv")

DATA_WEIGHT = {"PII, financial":5,"PII":4,"financial":4,"confidential":3,"public":1}
def data_score(v):
    return max([DATA_WEIGHT.get(x.strip(),2) for x in str(v).split(",")] or [2])

def tier(score):
    if score >= 12: return "Critical"
    if score >= 8:  return "High"
    if score >= 4:  return "Medium"
    return "Low"

# crude criticality from data sensitivity x business dependence (1-5, in a column or default 3)
df["RiskScore"] = df["DataAccessed"].apply(data_score) * df.get("BusinessDependence", 3)
df["Tier"] = df.RiskScore.apply(tier)
df.to_csv("vendor-register-scored.csv", index=False)
print(df.groupby("Tier").size())
```

### 3b. Certificate expiry & reassessment monitor (PowerShell)

```powershell
# scripts/powershell/Get-VendorAlerts.ps1
param([string]$RegisterPath = "\\fileserver\GRC\06_Vendors\vendor-register.csv",[int]$WarnDays = 60)
$today = Get-Date
Import-Csv $RegisterPath | ForEach-Object {
  # cert expiry
  if ($_.CertExpiry) {
    $d = ([datetime]$_.CertExpiry - $today).Days
    if ($d -le $WarnDays) { "CERT: $($_.Name) $($_.CertType) expires in $d d ($($_.CertExpiry))" }
  }
  # reassessment due
  $next = ([datetime]$_.LastAssessed).AddMonths([int]$_.ReassessFrequencyMonths)
  if (($next - $today).Days -le $WarnDays) {
    "REASSESS: $($_.Name) due $($next.ToString('yyyy-MM-dd')) [Tier $($_.Tier)]"
  }
}
```

### 3c. Questionnaire intake without a portal

- Keep a master questionnaire (Excel/Word) in `06_Vendors/_templates`.
- For each vendor create `06_Vendors/<VendorID>_<Name>/` containing the sent questionnaire, returned answers, and certificates (named with the `VEN_` convention).
- A PowerShell script verifies each Critical/High vendor folder contains the **required artifacts** and flags incomplete packs:

```powershell
$required = 'questionnaire','cert','dpa'
Get-ChildItem "\\fileserver\GRC\06_Vendors" -Directory | ForEach-Object {
  $files = (Get-ChildItem $_.FullName -File).Name -join ' '
  $missing = $required | Where-Object { $files -notmatch $_ }
  if ($missing) { "INCOMPLETE: $($_.Name) missing -> $($missing -join ', ')" }
}
```

### 3d. Reminders

Feed the output of `Get-VendorAlerts.ps1` into the Outlook reminder pattern (`docs/02`) to nudge the internal vendor owner ahead of expiries and reassessment dates.

## 4. A note on automated external risk feeds

Public breach databases, sanction lists, and security-rating feeds can enrich vendor risk - but most useful ones are cloud/API services. In a strictly non-cloud environment, keep this step **manual or periodic**: download any permitted public list and reconcile against your register with a simple join. Do not wire the toolkit to scrape third-party sites.

## 5. Scheduling & ownership

- **Owner:** Procurement / Vendor Manager; **Oversight:** GRC.
- Cert & reassessment alerts **weekly**; full reassessment cycle by tier (Critical annually or more often).

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Tiering | Manual judgement | Auto-scored from data + dependence |
| Cert tracking | Forgotten until lapse | Auto 60-day expiry alerts |
| Intake | Loose files | Folder completeness checks |
| Reassessment | Ad hoc | Cadence-driven reminders by tier |

**Next:** `docs/08-audit-readiness.md`
