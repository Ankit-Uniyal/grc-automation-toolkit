# Starter Templates Index (`templates/`)

Ready-to-use, empty (header-only) register CSVs - one per GRC pillar. Copy a
file into your working folder, fill in your rows, and point the matching script
or guide at it. Column headers are pre-set so the scripts in `scripts/` read them
without changes.

> Tip: keep these as your master schema. When a script expects a column and
> errors out, check the header here first.

## Registers

| Template | Use it for | Related guide |
|----------|-----------|---------------|
| `risk-register.csv` | Risks: scoring, treatment, residual ratings | [03](../docs/03-risk-management.md) |
| `control-matrix.csv` | Control library and testing status | [04](../docs/04-control-testing.md) |
| `policy-register.csv` | Policy lifecycle, owners, review dates | [02](../docs/02-policy-management.md) |
| `asset-inventory.csv` | Asset register and ownership | [01](../docs/01-folder-governance.md) |
| `vendor-register.csv` | Third parties, tiers, cert expiry | [07](../docs/07-vendor-risk.md) |
| `obligations-register.csv` | Legal/regulatory obligations & calendar | [10](../docs/10-compliance-obligations.md) |
| `crosswalk.csv` | Map controls across frameworks | [11](../docs/11-framework-crosswalk.md) |
| `incident-register.csv` | Incidents and breach-clock tracking | [12](../docs/12-incident-management.md) |
| `bia-register.csv` | Business impact analysis (BCM/DR) | [13](../docs/13-business-continuity.md) |
| `change-register.csv` | Change requests, approvals, reviews | [14](../docs/14-change-management.md) |
| `issue-register.csv` | Issues and corrective/preventive actions | [15](../docs/15-issues-capa.md) |
| `audit-universe.csv` | Auditable entities and planning | [16](../docs/16-internal-audit.md) |
| `vuln-register.csv` | Vulnerabilities and SLA tracking | [17](../docs/17-vulnerability-management.md) |
| `exception-register.csv` | Risk/control exceptions and expiry | [04](../docs/04-control-testing.md) |
| `ropa-register.csv` | Records of processing activities (privacy) | [19](../docs/19-data-privacy.md) |
| `dsar-register.csv` | Data subject access requests | [19](../docs/19-data-privacy.md) |
| `sod-rules.csv` | Segregation-of-duties conflict rules | [20](../docs/20-people-awareness-sod.md) |
| `kri-register.csv` | Key risk indicators and thresholds | [21](../docs/21-metrics-management-review.md) |

## Dashboards

See [`dashboards/`](dashboards/README.md) for the reporting/dashboard starters.

---

Back to the [repository overview](../README.md) | [pillar guides](../docs/README.md) | [scripts](../scripts/README.md).
