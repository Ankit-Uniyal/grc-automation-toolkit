# Excel / Power Query Dashboard Pack

> [!IMPORTANT]
> This builds a **self-refreshing** GRC dashboard in plain Excel - no code, no cloud.
> It reads the CSVs produced by the scripts (e.g. `grc-metrics-history.csv`) and redraws charts
> every time you open the file. New here? See **[../../DIY-GUIDE.md](../../DIY-GUIDE.md)** Part C first.

## What you get

A single `GRC-Dashboard.xlsx` with refreshable views of:
- overdue counts (controls, issues, vulnerabilities, access reviews),
- SLA attainment % (incidents, vulns),
- risk levels (Critical/High/Medium/Low),
- KRI trend over time.

## Before you start - the values to change

> [!TIP]
> Everywhere below, replace the `<<CHANGE_ME: ...>>` path with the real location of your reports folder.

| Value | Replace with |
|-------|--------------|
| Metrics history file | `<<CHANGE_ME: \\fileserver\GRC\reports\grc-metrics-history.csv>>` |
| Risk scored file | `<<CHANGE_ME: \\fileserver\GRC\reports\risk-register-scored.csv>>` |
| Where to save the workbook | `<<CHANGE_ME: \\fileserver\GRC\reports\GRC-Dashboard.xlsx>>` |

## Step-by-step (one time)

1. Open a **new, blank** Excel workbook.
2. Go to **Data -> Get Data -> From File -> From Text/CSV**.
3. Browse to your metrics history file (the `<<CHANGE_ME>>` path above) and click **Import**.
4. In the preview window, click **Transform Data** (this opens Power Query).
5. In Power Query: confirm each column has the right **data type** (dates as Date, counts as Whole Number).
   Right-click a column header -> **Change Type** if needed.
6. Click **Home -> Close & Load To... -> Only Create Connection** *and* tick **Add this data to the Data Model**.
7. Repeat steps 2-6 for the risk scored file (and any other report CSV you want to chart).
8. Build the visuals: **Insert -> PivotChart**, choose the connection, and drag fields:
   - X axis (Axis) = `SnapshotDate` (for trends) or the category (e.g. `RiskLevel`).
   - Values = the metric you want (e.g. `OverdueControls`, `SlaAttainmentPct`).
9. Add as many PivotCharts as you need on one **Dashboard** worksheet.

## Make it refresh automatically

1. Go to **Data -> Queries & Connections**.
2. Right-click each query -> **Properties**.
3. Tick **Refresh data when opening the file** (and optionally **Refresh every N minutes**).
4. Click **OK**.

> [!TIP]
> Now anyone who opens `GRC-Dashboard.xlsx` sees the latest numbers automatically - no manual work.

## Keep it current automatically

Schedule the metrics script (see [../../DIY-GUIDE.md](../../DIY-GUIDE.md) task B11) to append a fresh row to
`grc-metrics-history.csv` on a schedule. The dashboard picks up the new row on next open / refresh.

## Suggested layout

```text
Dashboard (sheet 1)   <- the PivotCharts and slicers your audience sees
Data_Metrics (sheet)  <- the loaded metrics query (can be hidden)
Data_Risk (sheet)     <- the loaded risk query (can be hidden)
```

> [!NOTE]
> Add **Slicers** (PivotChart Analyze -> Insert Slicer) on `Period`, `Department`, or `Framework` so
> reviewers can filter the whole dashboard with one click during the management review.
