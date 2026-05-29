"""
build_uar_packs.py - Generate per-manager User Access Review (UAR) packs and
reconcile the current access snapshot against the previous one.

Inputs (export from Active Directory with Export-AccessSnapshot.ps1):
    users_<date>.csv             columns: SamAccountName, Name, Department, Title, Manager, LastLogonDate
    group_membership_<date>.csv  columns: Group, Member

Outputs:
    packs/UAR_<manager>_<period>.xlsx   one review spreadsheet per manager
    uar_added.csv / uar_removed.csv     access changes since the previous review

Usage:
    python build_uar_packs.py users_2026-06-01.csv group_membership_2026-06-01.csv \
        --prev group_membership_2026-03-01.csv --period 2026Q2

Requires: pandas, openpyxl
"""
import argparse
import os
import pandas as pd


def build_packs(users_csv, groups_csv, period):
    users = pd.read_csv(users_csv)
    groups = pd.read_csv(groups_csv)
    access = groups.merge(users, left_on="Member", right_on="SamAccountName", how="left")
    os.makedirs("packs", exist_ok=True)
    cols = ["Member", "Name", "Department", "Title", "Group", "LastLogonDate"]
    cols = [c for c in cols if c in access.columns]
    count = 0
    for mgr, grp in access.groupby(access.get("Manager", "UNASSIGNED")):
        out = grp[cols].copy()
        out["Decision (Keep/Revoke)"] = ""
        out["Comment"] = ""
        safe = str(mgr).replace("\\", "_").replace("/", "_") or "UNASSIGNED"
        out.to_excel(f"packs/UAR_{safe}_{period}.xlsx", index=False)
        count += 1
    print(f"Generated {count} manager packs in ./packs")


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
