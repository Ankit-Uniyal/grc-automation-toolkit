"""
sod_check.py - Segregation-of-Duties (SoD) conflict detection.

Compares each user's role/group memberships against a list of conflicting role
pairs and reports violations.

Inputs:
    sod-rules.csv                  RoleA, RoleB, Conflict
    group_membership_<date>.csv    Group, Member  (from docs/06 AD export)

Usage:  python sod_check.py group_membership_2026-06-01.csv
Outputs: sod-violations.csv
Requires: pandas, grclib
"""
import sys
import pandas as pd
from grclib import load_register


def main(membership_csv):
    rules = load_register("sod-rules.csv")
    mem = load_register(membership_csv)
    user_roles = mem.groupby("Member").Group.apply(set).to_dict()
    violations = []
    for user, roles in user_roles.items():
        for _, r in rules.iterrows():
            if r.RoleA in roles and r.RoleB in roles:
                violations.append((user, r.RoleA, r.RoleB, r.Conflict))
    out = pd.DataFrame(violations, columns=["User", "RoleA", "RoleB", "Conflict"])
    out.to_csv("sod-violations.csv", index=False)
    if violations:
        print(f"{len(violations)} SoD violations found:")
        print(out.to_string(index=False))
    else:
        print("No SoD violations found.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sod_check.py <group_membership.csv>")
        sys.exit(1)
    main(sys.argv[1])
