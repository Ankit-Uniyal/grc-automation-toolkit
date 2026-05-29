"""
sod_check.py - Segregation-of-Duties (SoD) conflict detection.

Compares each user's role/group memberships against a list of conflicting role pairs and reports violations.

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B4).

Governance rule: this only DETECTS and REPORTS conflicts. Removing a conflicting
role is a human decision made after review - never automate the change.

Inputs:
  sod-rules.csv                 RoleA, RoleB, Conflict
  group_membership_<date>.csv   Group, Member  (from docs/06 AD export)

Usage: python sod_check.py group_membership_2026-06-01.csv
Outputs: sod-violations.csv
Requires: pandas, grclib
"""
import os
import sys
import pandas as pd
from grclib import load_register, require_columns

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Folder that holds sod-rules.csv. Replace the token (keep quotes).
# Leave as "." if you run this from inside your registers folder.
# ----------------------------------------------------------------------------

REGISTER_DIR = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\registers>>"   # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================


def main(membership_csv):
    rules_path = "sod-rules.csv"
    if REGISTER_DIR and REGISTER_DIR != "." and "CHANGE_ME" not in REGISTER_DIR:
        rules_path = os.path.join(REGISTER_DIR, "sod-rules.csv")
    rules = load_register(rules_path)
    require_columns(rules, ["RoleA", "RoleB", "Conflict"], "SoD rules")
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
