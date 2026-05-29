"""
risk_engine.py - Score the risk register and generate a 5x5 residual heatmap.

Reads risk-register.csv, computes inherent and residual scores, assigns risk
bands, writes risk-register-scored.csv, and saves risk-heatmap.png for reports.

Usage:
    python risk_engine.py [path-to-risk-register.csv]

Requires: pandas, matplotlib, numpy   (pip install pandas matplotlib numpy)
Designed for non-cloud use: reads/writes plain files on a shared drive.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed on a server/workstation
import matplotlib.pyplot as plt


def band(score: int) -> str:
    if score >= 15:
        return "Critical"
    if score >= 8:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def main(path: str = "risk-register.csv") -> None:
    df = pd.read_csv(path)
    df["InherentScore"] = df.Likelihood * df.Impact
    df["ResidualScore"] = df.ResidualLikelihood * df.ResidualImpact
    df["ResidualBand"] = df.ResidualScore.apply(band)

    out_csv = "risk-register-scored.csv"
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
    plt.savefig("risk-heatmap.png", dpi=120)

    print("Wrote", out_csv, "and risk-heatmap.png")
    print(df.ResidualBand.value_counts())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "risk-register.csv")
