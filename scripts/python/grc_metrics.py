"""
grc_metrics.py - Aggregate headline GRC metrics from every pillar into a single
RAG (red/amber/green) dashboard, and append a snapshot for trend tracking.

Reads whatever registers exist in REGISTER_DIR (missing ones are skipped
gracefully) and the thresholds in kri-register.csv.

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Search this file for CHANGE_ME. See CONVENTIONS.md and DIY-GUIDE.md (task B11).

Governance rule: this only MEASURES and REPORTS. It changes no register data.

Usage: python grc_metrics.py
Outputs: grc-metrics.csv (current), grc-metrics-history.csv (appended)
Requires: pandas, grclib
"""
import os
import pandas as pd
from datetime import date
from grclib import load_register, overdue

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Folder that holds your live register CSVs. Replace the token (keep quotes).
# Leave as "." if you run this from inside your registers folder.
# ----------------------------------------------------------------------------

REGISTER_DIR = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\registers>>"   # CHANGE ME

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================

if REGISTER_DIR and REGISTER_DIR != "." and "CHANGE_ME" not in REGISTER_DIR:
    os.chdir(REGISTER_DIR)


def safe(fn, default=0):
    try:
        return fn()
    except Exception:
        return default


def collect():
    m = {}
    ctl = safe(lambda: load_register("control-matrix.csv"), pd.DataFrame())
    m["overdue_control_tests"] = safe(
        lambda: int(ctl[ctl.NextTestDate.notna()].NextTestDate.apply(overdue).sum()))
    rk = safe(lambda: load_register("risk-register.csv"), pd.DataFrame())
    m["critical_residual_risks"] = safe(
        lambda: int(((rk.ResidualLikelihood * rk.ResidualImpact) >= 15).sum()))
    iss = safe(lambda: load_register("issue-register.csv"), pd.DataFrame())
    m["overdue_capa"] = safe(
        lambda: int(iss[iss.Status != "Closed"].DueDate.apply(overdue).sum()))
    exc = safe(lambda: load_register("exception-register.csv"), pd.DataFrame())
    m["expired_exceptions"] = safe(
        lambda: int(exc[exc.Status == "Active"].ExpiryDate.apply(overdue).sum()))
    vul = safe(lambda: load_register("vuln-register.csv"), pd.DataFrame())
    m["sla_breached_vulns"] = safe(
        lambda: int(vul[(vul.Status == "Open") & (vul.Severity.isin(["Critical", "High"]))]
                    .DueDate.apply(overdue).sum()))
    obl = safe(lambda: load_register("obligations-register.csv"), pd.DataFrame())
    m["overdue_obligations"] = safe(
        lambda: int(obl[obl.NextObligationDate.notna() & (obl.NextObligationDate.astype(str).str.strip() != "")]
                    .NextObligationDate.apply(overdue).sum()))
    return m


def rag(metric, value, thresholds):
    t = thresholds.get(metric)
    if t is None:
        return "n/a"
    green, amber, direction = t
    if direction == "higher_is_better":
        if value >= green: return "GREEN"
        if value >= amber: return "AMBER"
        return "RED"
    if value <= green: return "GREEN"
    if value <= amber: return "AMBER"
    return "RED"


def main():
    kri = safe(lambda: load_register("kri-register.csv"), pd.DataFrame())
    thresholds = {}
    for _, r in kri.iterrows():
        thresholds[r.Metric] = (float(r.GreenMax), float(r.AmberMax), r.Direction)

    metrics = collect()
    rows = []
    for k, v in metrics.items():
        rows.append({"Metric": k, "Value": v, "Status": rag(k, v, thresholds),
                     "AsOf": date.today().isoformat()})
    out = pd.DataFrame(rows)
    out.to_csv("grc-metrics.csv", index=False)
    hist = "grc-metrics-history.csv"
    out.to_csv(hist, mode="a", header=not os.path.exists(hist), index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
