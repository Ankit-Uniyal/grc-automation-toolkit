"""
build_uar_packs.py - Generate per-manager User Access Review (UAR) packs and
reconcile the current access snapshot against the previous one.

>>> HOW TO RUN: this script takes its inputs as command-line ARGUMENTS, so the
values you change are on the command line (not inside the file). See the Usage
line below and DIY-GUIDE.md (task B4). The only in-file value you may change is
the OUTPUT_DIR in the CHANGE ME block.

Governance rule: this only PREPARES review packs and lists changes. It never
grants or revokes access - managers decide and IT applies the change manually.

Inputs (export from Active Directory; see the inline AD-export example in docs/06-access-reviews.md):
  users_<date>.csv               SamAccountName, Name, Department, Title, Manager, LastLogonDate
  group_membership_<date>.csv    Group, Member
Outputs:
  <OUTPUT_DIR>/UAR_<manager>_<period>.xlsx   one review spreadsheet per manager
  uar_added.csv / uar_removed.csv            access changes since the previous review

Usage:
  python build_uar_packs.py users_2026-06-01.csv group_membership_2026-06-01.csv \\
         --prev group_membership_2026-03-01.csv --period 2026Q2
Requires: pandas, openpyxl
"""
import argparse
import os
import pandas as pd

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Folder where the per-manager review packs are written. Replace the token
# (keep quotes), or leave as "packs" to create a packs\ folder in the cwd.
# ----------------------------------------------------------------------------

OUTPUT_DIR = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\reports\uar-packs>>"   # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

_OUT = "packs" if (not OUTPUT_DIR or "CHANGE_ME" in OUTPUT_DIR) else OUTPUT_DIR


def build_packs(users_csv, groups_csv, period):
    users = pd.read_csv(users_csv)
    groups = pd.read_csv(groups_csv)
    access = groups.merge(users, left_on="Member", right_on="SamAccountName", how="left")
    os.makedirs(_OUT, exist_ok=True)
    cols = ["Member", "Name", "Department", "Title", "Group", "LastLogonDate"]
    cols = [c for c in cols if c in access.columns]
    count = 0
    for mgr, grp in access.groupby(access.get("Manager", "UNASSIGNED")):
        out = grp[cols].copy()
        out["Decision (Keep/Revoke)"] = ""
        out["Comment"] = ""
        safe = str(mgr).replace("\\", "_").replace("/", "_") or "UNASSIGNED"
        out.to_excel(os.path.join(_OUT, f"UAR_{safe}_{period}.xlsx"), index=False)
        count += 1
    print(f"Generated {count} manager packs in {_OUT}")


def reconcile(curr_csv, prev_csv):
    curr = pd.read_csv(curr_csv)
    prev = pd.read_csv(prev_csv)
    curr_set = set(map(tuple, curr[["Group", "Member"]].values))
    prev_set = set(map(tuple, prev[["Group", "Member"]].values))
    added = sorted(curr_set - prev_set)
    removed = sorted(prev_set - curr_set)
    pd.DataFrame(added, columns=["Group", "Member"]).to_csv("uar_added.csv", index=False)
    pd.DataFrame(removed, columns=["Group", "Member"]).to_csv("uar_removed.csv", index=False)
    print(f"{len(added)} new grants, {len(removed)} removals since last review")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("users_csv")
    p.add_argument("groups_csv")
    p.add_argument("--prev", help="previous group_membership csv for reconciliation")
    p.add_argument("--period", default="current")
    a = p.parse_args()
    build_packs(a.users_csv, a.groups_csv, a.period)
    if a.prev:
        reconcile(a.groups_csv, a.prev)


if __name__ == "__main__":
    main()
