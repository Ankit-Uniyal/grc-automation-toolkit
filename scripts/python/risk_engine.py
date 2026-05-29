"""
risk_engine.py - Score the risk register and generate a 5x5 residual heatmap.

Reads risk-register.csv, computes inherent and residual scores, assigns risk
bands, writes risk-register-scored.csv, and saves risk-heatmap.png for reports.

>>> BEFORE YOU RUN: edit the values in the CHANGE ME block below. <<<
Every value you must set for YOUR environment is tagged with  # CHANGE ME
and uses a <<CHANGE_ME: ...>> token. Search this file for CHANGE_ME.
See CONVENTIONS.md and DIY-GUIDE.md (task B2) for step-by-step help.

Governance rule: this script only CALCULATES and REPORTS. It never accepts a
risk or approves treatment - those decisions stay human-approved.

Usage:
    python risk_engine.py [optional-path-to-risk-register.csv]
Requires: pandas, matplotlib, numpy  (pip install pandas matplotlib numpy)
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed on a server/workstation
import matplotlib.pyplot as plt
from grclib import load_register, require_columns

# ============================================================================
# vvv                          CHANGE ME                                  vvv
# Set these to match YOUR environment. Replace the whole "<<CHANGE_ME: ...>>"
# value (keep the surrounding quotes).
# ----------------------------------------------------------------------------

# Where your live risk register lives (the source of truth):
RISK_REGISTER_PATH = r"<<CHANGE_ME: \\fileserver\GRC\02_Risk\risk-register.csv>>"   # CHANGE ME

# Where to write the scored output and the heatmap image:
OUTPUT_CSV  = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\reports\risk-register-scored.csv>>"     # CHANGE ME
OUTPUT_PNG  = r"<<CHANGE_ME: \\fileserver\GRC\00_Admin\reports\risk-heatmap.png>>"             # CHANGE ME

# Scoring thresholds (optional - tune to your risk methodology):
THRESHOLD_CRITICAL = 15   # CHANGE ME (optional)
THRESHOLD_HIGH     = 8    # CHANGE ME (optional)
THRESHOLD_MEDIUM   = 4    # CHANGE ME (optional)

# ^^^                          CHANGE ME                                  ^^^
# ============================================================================


def band(score: int) -> str:
    if score >= THRESHOLD_CRITICAL:
        return "Critical"
    if score >= THRESHOLD_HIGH:
        return "High"
    if score >= THRESHOLD_MEDIUM:
        return "Medium"
    return "Low"


def main(path: str = RISK_REGISTER_PATH) -> None:
    df = load_register(path)
    require_columns(df, ["Likelihood", "Impact", "ResidualLikelihood", "ResidualImpact"], "risk register")
    df["InherentScore"] = df.Likelihood * df.Impact
    df["ResidualScore"] = df.ResidualLikelihood * df.ResidualImpact
    df["ResidualBand"] = df.ResidualScore.apply(band)

    # If the OUTPUT_ paths still contain the CHANGE_ME placeholder, fall back to
    # relative filenames so the quickstart works out of the box. Set real paths
    # in the config block above for production runs.
    out_csv = OUTPUT_CSV if "CHANGE_ME" not in OUTPUT_CSV else "risk-register-scored.csv"
    out_png = OUTPUT_PNG if "CHANGE_ME" not in OUTPUT_PNG else "risk-heatmap.png"

    df.to_csv(out_csv, index=False)

    # Build a 5x5 grid of residual risk counts (Impact rows, Likelihood cols)
    grid = np.zeros((5, 5), dtype=int)
    for _, r in df.iterrows():
        i = 5 - int(r.ResidualImpact)
        j = int(r.ResidualLikelihood) - 1
        if 0 <= i < 5 and 0 <= j < 5:
            grid[i, j] += 1

    plt.figure(figsize=(6, 5))
    plt.imshow(grid, cmap="RdYlGn_r")
    plt.colorbar(label="Number of risks")
    plt.xlabel("Likelihood")
    plt.ylabel("Impact")
    plt.xticks(range(5), range(1, 6))
    plt.yticks(range(5), range(5, 0, -1))
    for i in range(5):
        for j in range(5):
            if grid[i, j]:
                plt.text(j, i, grid[i, j], ha="center", va="center")
    plt.title("Residual Risk Heatmap")
    plt.tight_layout()
    plt.savefig(out_png, dpi=120)

    print("Wrote", out_csv, "and", out_png)
    print(df.ResidualBand.value_counts())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RISK_REGISTER_PATH)
