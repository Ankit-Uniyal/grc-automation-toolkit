# 10 · Compliance & Obligations Management

> **Pillar:** Compliance. Most teams track "controls" but never maintain a clean list of the **obligations** those controls exist to satisfy (laws, regulations, contractual clauses, standards). This pillar automates the obligations register, the compliance calendar, and multi-framework crosswalk so you can prove coverage and never miss a filing.

---

## 1. What to automate

- **Obligations register** - every legal/regulatory/contractual requirement that applies to you.
- **Obligation → control mapping** - which controls satisfy each obligation (and gaps).
- **Compliance calendar** - recurring filings, certifications, attestations, renewals.
- **Multi-framework crosswalk** - map your controls once, report against ISO 27001 / NIST CSF / SOC 2 / PCI DSS / GDPR simultaneously.
- **Horizon scanning log** - track regulatory changes and assign impact assessments.

## 2. Data model - `obligations-register.csv`

| Column | Notes |
|---|---|
| ObligationID | OBL-012 |
| Source | GDPR / PCI DSS / Local Data Law / Customer Contract X |
| Reference | Art. 32 / Req 8.3 |
| Requirement | Short description of what is required |
| Type | Regulatory / Contractual / Standard / Internal |
| Owner | DPO / CISO |
| ControlIDs | CTRL-AC-001;CTRL-EP-001 |
| Status | Met / Partial / Gap |
| NextObligationDate | filing/renewal date (if any) |
| FrequencyMonths | for recurring obligations |
| Evidence | link |

## 3. The automation

### 3a. Obligation coverage & gap report (Python, uses grclib)

```python
# scripts/python/obligation_coverage.py
import pandas as pd
from grclib import load_register, split_refs

obs = load_register("obligations-register.csv")
controls = set(load_register("control-matrix.csv").ControlID)

rows = []
for _, o in obs.iterrows():
    mapped = split_refs(o.ControlIDs)
    missing = [c for c in mapped if c not in controls]
    rows.append({
        "ObligationID": o.ObligationID, "Source": o.Source, "Reference": o.Reference,
        "MappedControls": len(mapped), "MissingControls": ";".join(missing),
        "Status": o.Status,
        "Coverage": "GAP" if (o.Status == "Gap" or not mapped) else ("PARTIAL" if missing else "OK"),
    })
report = pd.DataFrame(rows)
report.to_csv("obligation-coverage.csv", index=False)
print(report.Coverage.value_counts())
```

### 3b. Compliance calendar engine (Python)

```python
# scripts/python/compliance_calendar.py
import pandas as pd
from grclib import load_register, days_left, next_due

obs = load_register("obligations-register.csv")
upcoming = []
for _, o in obs.iterrows():
    if pd.notna(o.get("NextObligationDate")) and str(o.NextObligationDate).strip():
        d = days_left(o.NextObligationDate)
        if d <= 60:
            upcoming.append({"ObligationID": o.ObligationID, "Source": o.Source,
                             "Due": o.NextObligationDate, "DaysLeft": d, "Owner": o.Owner})
cal = pd.DataFrame(upcoming).sort_values("DaysLeft")
cal.to_csv("compliance-calendar-upcoming.csv", index=False)
print(cal.to_string(index=False))
```

Feed the output into the PowerShell/Outlook notification helper (`Send-GrcNotification`) to remind owners.

### 3c. Multi-framework crosswalk

See `docs/11-framework-crosswalk.md` and `scripts/python/build_crosswalk.py` - map each control to clauses across frameworks once, then auto-produce a coverage report per framework.

## 4. Horizon scanning (regulatory change)

Maintain `reg-change-log.csv` (ChangeID, Date, Source, Summary, Owner, ImpactAssessmentDue, Status). This is mostly a **tracked manual feed** (regulators publish via web/email); the automation chases overdue impact assessments using the standard reminder pattern. Do **not** wire the toolkit to scrape regulator sites.

## 5. Scheduling & ownership

- **Owner:** Compliance Manager / DPO.
- Coverage + calendar **monthly**; obligation reminders **weekly**; horizon-scan review **monthly**.

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Obligations | Scattered in policies | Central register mapped to controls |
| Calendar | Personal reminders | Auto 60-day filing/renewal alerts |
| Frameworks | One at a time | Map once, report many (crosswalk) |
| Change | Ad hoc | Tracked horizon-scan log + impact SLA |

**Next:** `docs/11-framework-crosswalk.md`
