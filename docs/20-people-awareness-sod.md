# 20 · People: Awareness, Training & Segregation of Duties

> **Pillar:** Human controls. People are both the biggest risk and a tested control. This pillar automates training/awareness completion tracking, phishing-simulation result ingestion, and segregation-of-duties (SoD) conflict detection.

---

## 1. What to automate

- **Training completion** — who has/has not completed mandatory training.
- **Awareness campaign tracking** — by topic and audience.
- **Phishing simulation ingestion** — normalize results, track repeat clickers.
- **SoD conflict detection** — flag users holding conflicting role combinations.
- **Onboarding/role-change controls** — required training before access.

## 2. Data models

`training-register.csv`

| Column | Notes |
|---|---|
| Course | Security Awareness 2026 |
| Mandatory | Yes |
| DueDate | 2026-06-30 |

`training-completions.csv`

| Column | Notes |
|---|---|
| Employee | jsmith |
| Course | Security Awareness 2026 |
| CompletedDate | 2026-05-01 |
| Score | 92 |

## 3. The automation

### 3a. Training compliance & non-completers (Python, uses grclib)

```python
# scripts/python/training_compliance.py
import pandas as pd
from grclib import load_register

employees = load_register("users_2026-06-01.csv")     # from docs/06 AD export
done = load_register("training-completions.csv")
course = "Security Awareness 2026"

completed = set(done[done.Course == course].Employee)
employees["Completed"] = employees.SamAccountName.isin(completed)
rate = employees.Completed.mean() * 100
print(f"{course} completion: {rate:.1f}%")

non = employees[~employees.Completed][["SamAccountName", "Name", "Department"]]
non.to_csv("training-noncompleters.csv", index=False)
print(f"{len(non)} outstanding")
```

Feed `training-noncompleters.csv` into reminders, and escalate to managers as the due date nears.

### 3b. Phishing simulation ingestion (Python)

```python
# scripts/python/phishing_results.py  -- normalize any tool's CSV export
import pandas as pd
raw = pd.read_csv("phishing_export.csv")
res = pd.DataFrame({
    "Employee": raw.get("User", raw.iloc[:, 0]),
    "Campaign": raw.get("Campaign", "Q2-2026"),
    "Clicked": raw.get("Clicked", False),
    "Reported": raw.get("Reported", False),
})
res.to_csv("phishing-normalized.csv", index=False)
print("Click rate:", round(res.Clicked.mean()*100, 1), "%")
print("Report rate:", round(res.Reported.mean()*100, 1), "%")

# Repeat clickers across campaigns => targeted follow-up training
all_res = pd.read_csv("phishing-history.csv") if False else res
repeat = (all_res[all_res.Clicked].groupby("Employee").size()
          .reset_index(name="Clicks").query("Clicks >= 2"))
print("Repeat clickers:\n", repeat.to_string(index=False))
```

### 3c. Segregation-of-Duties (SoD) conflict detection (Python)

```python
# scripts/python/sod_check.py
import pandas as pd
from grclib import load_register

# sod-rules.csv: RoleA, RoleB, Conflict (e.g. "Create Vendor" vs "Approve Payment")
rules = load_register("sod-rules.csv")
# membership: from docs/06 group_membership export (Group=role, Member=user)
mem = load_register("group_membership_2026-06-01.csv")

user_roles = mem.groupby("Member").Group.apply(set).to_dict()
violations = []
for user, roles in user_roles.items():
    for _, r in rules.iterrows():
        if r.RoleA in roles and r.RoleB in roles:
            violations.append((user, r.RoleA, r.RoleB, r.Conflict))
pd.DataFrame(violations, columns=["User", "RoleA", "RoleB", "Conflict"]).to_csv("sod-violations.csv", index=False)
for v in violations:
    print("SoD VIOLATION:", v)
```

SoD violations should open an **issue** (docs/15) for review — either remediate the access or document a compensating control as an **exception** with expiry.

## 4. Onboarding control

Tie required training to access: a joiner should complete mandatory training before (or shortly after) provisioning. Cross-reference new `whenCreated` accounts (docs/06) against `training-completions` to flag gaps.

## 5. Scheduling & ownership

- **Owner:** Security Awareness Lead (training), IAM (SoD), HR (onboarding).
- Training compliance **weekly** during campaigns; phishing ingestion **per campaign**; SoD check **monthly** (and after role changes).

## 6. Maturity ladder

| | Minimum viable | Advanced |
|---|---|---|
| Training | LMS export reviewed manually | Auto completion + non-completer chase |
| Phishing | Per-campaign PDF | Normalized + repeat-clicker tracking |
| SoD | Never checked | Rule-based conflict detection |
| Onboarding | Trust | Training-before-access reconciliation |

**Next:** `docs/21-metrics-management-review.md`
