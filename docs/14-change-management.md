# 14 · Change Management Governance

> **Pillar:** Operational control. Auditors routinely test that significant changes were assessed, approved, and reviewed. This pillar automates the change register, approval-completeness checks, and emergency-change reconciliation — without a ticketing platform.

---

## 1. What to automate

- **Change register** — record of changes with risk, approval, and outcome.
- **Approval-completeness checks** — flag changes missing required approvals.
- **Emergency change reconciliation** — ensure post-hoc reviews happened.
- **Unauthorized change detection** — reconcile a change log against system/config drift evidence.
- **Metrics** — change success rate, emergency-change ratio, failed-change trend.

## 2. Data model — `change-register.csv`

| Column | Notes |
|---|---|
| ChangeID | CHG-2026-088 |
| Title | Firewall ruleset update |
| Type | Standard / Normal / Emergency |
| RiskLevel | Low / Medium / High |
| Requestor | Network Eng |
| ApprovedBy | Change Manager |
| ApprovalDate | 2026-05-10 |
| ImplementedAt | 2026-05-12 |
| Outcome | Success / Failed / Rolled back |
| PostReviewDone | Yes / No (emergency) |
| LinkedAssets | AST-004 |
| LinkedIncidentID | INC-... (if it caused one) |

## 3. The automation

### 3a. Approval & review completeness (Python, uses grclib)

```python
# scripts/python/change_governance.py
import pandas as pd
from grclib import load_register

chg = load_register("change-register.csv")
issues = []
for _, c in chg.iterrows():
    # Normal/High-risk changes must have an approver before implementation
    if c.Type in ("Normal",) and (pd.isna(c.get("ApprovedBy")) or not str(c.ApprovedBy).strip()):
        issues.append((c.ChangeID, "MISSING APPROVAL"))
    if str(c.RiskLevel) == "High" and (pd.isna(c.get("ApprovalDate")) or not str(c.ApprovalDate).strip()):
        issues.append((c.ChangeID, "HIGH-RISK: no approval date"))
    # Emergency changes must have a post-implementation review
    if c.Type == "Emergency" and str(c.get("PostReviewDone")) != "Yes":
        issues.append((c.ChangeID, "EMERGENCY: post-review outstanding"))
    # Approval must pre-date implementation
    if pd.notna(c.get("ApprovalDate")) and pd.notna(c.get("ImplementedAt")):
        if pd.to_datetime(c.ApprovalDate) > pd.to_datetime(c.ImplementedAt):
            issues.append((c.ChangeID, "APPROVAL AFTER IMPLEMENTATION"))

pd.DataFrame(issues, columns=["ChangeID", "Issue"]).to_csv("change-governance-issues.csv", index=False)
for i in issues:
    print(i)
```

### 3b. Change metrics

```python
chg = load_register("change-register.csv")
total = len(chg)
print("Success rate:", round((chg.Outcome == "Success").mean()*100, 1), "%")
print("Emergency ratio:", round((chg.Type == "Emergency").mean()*100, 1), "%")
print("Failed/rolled back:", int(chg.Outcome.isin(["Failed", "Rolled back"]).sum()))
```

### 3c. Unauthorized change detection

Cross-reference implemented changes against your configuration-drift evidence (`docs/18`). Drift with **no matching ChangeID** is a potential unauthorized change — surface it for investigation.

## 4. Scheduling & ownership

- **Owner:** Change Manager.
- Governance completeness + metrics **weekly**; unauthorized-change reconciliation **weekly** (after drift collection).

## 5. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Register | Email approvals | Structured change register |
| Approvals | Manual check | Auto completeness + sequence checks |
| Emergency | Often unreviewed | Auto post-review chase |
| Integrity | Trust-based | Drift-vs-change reconciliation |

**Next:** `docs/15-issues-capa.md`
