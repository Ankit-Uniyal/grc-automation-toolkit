"""
build_traceability.py - Build a framework traceability matrix.

Joins the control matrix, policy register, and risk register into a single
auditor-friendly matrix: framework clause -> control -> policies -> risks ->
last test result -> evidence link. Also reports failing controls.

Usage:
    python build_traceability.py

Expects these CSVs in the working directory (copy the toolkit templates and
point them at your live registers):
    control-matrix.csv, policy-register.csv, risk-register.csv

Requires: pandas, openpyxl   (pip install pandas openpyxl)
"""
import pandas as pd


def split_refs(value: str):
    return [r.strip() for r in str(value).split(";") if r and r.strip()]


def main() -> None:
    controls = pd.read_csv("control-matrix.csv")
    policies = pd.read_csv("policy-register.csv")
    risks = pd.read_csv("risk-register.csv")

    rows = []
    for _, c in controls.iterrows():
        for clause in split_refs(c.get("FrameworkRefs", "")):
            pol = policies[policies.FrameworkRefs.fillna("").str.contains(clause, regex=False)]
            rsk = risks[risks.ControlIDs.fillna("").str.contains(str(c.ControlID), regex=False)]
            rows.append({
                "Clause": clause,
                "ControlID": c.ControlID,
                "ControlTitle": c.get("Title", ""),
                "Policies": ";".join(pol.PolicyID.tolist()),
                "Risks": ";".join(rsk.RiskID.tolist()),
                "LastResult": c.get("LastResult", ""),
                "Evidence": c.get("EvidenceLink", ""),
            })

    matrix = pd.DataFrame(rows).sort_values(["Clause", "ControlID"])
    matrix.to_excel("traceability-matrix.xlsx", index=False)
    matrix.to_csv("traceability-matrix.csv", index=False)

    failing = (matrix.LastResult == "Fail").sum()
    print("Rows:", len(matrix))
    print("Distinct clauses covered:", matrix.Clause.nunique())
    print("Controls failing:", failing)


if __name__ == "__main__":
    main()
