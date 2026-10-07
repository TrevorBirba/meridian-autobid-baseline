# Strength

Performance chasing alone at roi_sensitivity 0 (the none row), 0.2, 0.4 and 0.8 (the published value). The correlation is over all 156 weeks of the generator's frame, per seed in parentheses.

| roi_sensitivity | row | corr(PLA spend, true non-marketing) | true avg | true marg | config | converged | median est avg | per-seed est avg | median est marg | per-seed est marg | covered avg | covered marg | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | none | 0.03 (0.19, -0.01, 0.20, -0.07, 0.03) | 4.31 | 4.15 | arm 1 | 5/5 | 1.30 | 1.33, 1.28, 1.35, 1.18, 1.30 | 0.55 | 0.55, 0.54, 0.57, 0.49, 0.55 | 5/5 | 0/5 | 1.93 | 0.97 | 1.30 |
| 0.0 | none | 0.03 (0.19, -0.01, 0.20, -0.07, 0.03) | 4.31 | 4.15 | arm 2a | 5/5 | 1.50 | 1.64, 1.90, 1.50, 1.27, 1.20 | 0.66 | 0.76, 0.84, 0.66, 0.57, 0.53 | 5/5 | 1/5 | 2.30 | 1.16 | 1.48 |
| 0.2 | performance_chasing_0p2 | 0.31 (0.39, 0.22, 0.39, 0.17, 0.31) | 4.31 | 4.15 | arm 1 | 3/5 | 1.39 | 1.97, nc, nc, 1.28, 1.39 | 0.65 | 0.94, nc, nc, 0.54, 0.65 | 3/3 | 1/3 | 2.39 | 1.21 | 1.38 |
| 0.2 | performance_chasing_0p2 | 0.31 (0.39, 0.22, 0.39, 0.17, 0.31) | 4.31 | 4.15 | arm 2a | 5/5 | 1.40 | 1.63, 1.62, 1.40, 1.24, 1.27 | 0.64 | 0.74, 0.70, 0.64, 0.54, 0.53 | 5/5 | 0/5 | 2.11 | 1.05 | 1.39 |
| 0.4 | performance_chasing_0p4 | 0.41 (0.44, 0.33, 0.44, 0.30, 0.41) | 4.30 | 4.15 | arm 1 | 3/5 | 40.66 | 40.66, nc, 45.33, nc, 39.49 | 24.71 | 24.71, nc, 28.41, nc, 24.64 | 1/3 | 2/3 | 39.30 | 24.34 | 40.38 |
| 0.4 | performance_chasing_0p4 | 0.41 (0.44, 0.33, 0.44, 0.30, 0.41) | 4.30 | 4.15 | arm 2a | 5/5 | 1.39 | 1.50, 1.89, 1.39, 1.27, 1.35 | 0.59 | 0.69, 0.86, 0.59, 0.55, 0.57 | 5/5 | 1/5 | 1.99 | 0.97 | 1.37 |
| 0.8 | performance_chasing | 0.46 (0.46, 0.38, 0.46, 0.38, 0.46) | 4.29 | 4.15 | arm 1 | 5/5 | 37.50 | 34.27, 38.71, 37.50, 26.43, 41.16 | 22.66 | 20.61, 22.95, 22.66, 16.32, 24.96 | 1/5 | 1/5 | 37.10 | 22.98 | 36.86 |
| 0.8 | performance_chasing | 0.46 (0.46, 0.38, 0.46, 0.38, 0.46) | 4.29 | 4.15 | arm 2a | 5/5 | 1.53 | 2.12, 1.83, 1.44, 1.53, 1.33 | 0.66 | 0.98, 0.77, 0.60, 0.66, 0.56 | 5/5 | 0/5 | 2.26 | 1.11 | 1.51 |

Arm 1 median PLA average return over truth at 0, 0.2, 0.4, 0.8: 0.30, 0.32, 9.45, 8.74.

### PLA against the default ROI prior

PLA's ROI prior at every uncalibrated configuration (Meridian 2.0.0's default, read from the fitted model specification): LogNormal(0.2, 0.9), median 1.22, mean 1.83, 90 percent interval (5th to 95th percentile) [0.28, 5.37], width 5.09. Beside it, per uncalibrated cell: PLA's per-draw average return and Meridian's ROI (the quantity the prior is placed on), median [5th, 95th percentile] over the fit's saved draws, as medians over converged seeds; each ratio is the median over converged seeds of the per-fit ratio (median over the prior's median; interval width over the prior's interval width).

| config | row | converged | ROI prior median [90%] | per-draw avg [90%] | median / prior median | width / prior width | Meridian ROI [90%] | ROI median / prior median | ROI width / prior width | true avg |
|---|---|---|---|---|---|---|---|---|---|---|
| arm1 | none | 5 | 1.22 [0.28, 5.37] | 1.30 [0.28, 5.66] | 1.07 | 1.05 | 1.30 [0.28, 5.65] | 1.06 | 1.05 | 4.31 |
| arm1 | performance_chasing_0p2 | 3 | 1.22 [0.28, 5.37] | 1.39 [0.29, 8.09] | 1.14 | 1.53 | 1.38 [0.28, 8.06] | 1.13 | 1.53 | 4.31 |
| arm1 | performance_chasing_0p4 | 3 | 1.22 [0.28, 5.37] | 40.66 [7.76, 68.35] | 33.29 | 11.08 | 40.38 [7.71, 67.88] | 33.06 | 11.00 | 4.30 |
| arm1 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 37.50 [22.63, 54.93] | 30.70 | 6.56 | 36.86 [22.25, 54.05] | 30.18 | 6.43 | 4.29 |
| arm2a | none | 5 | 1.22 [0.28, 5.37] | 1.50 [0.31, 6.77] | 1.23 | 1.27 | 1.48 [0.31, 6.75] | 1.22 | 1.27 | 4.31 |
| arm2a | performance_chasing_0p2 | 5 | 1.22 [0.28, 5.37] | 1.40 [0.29, 6.16] | 1.15 | 1.15 | 1.39 [0.29, 6.14] | 1.14 | 1.15 | 4.31 |
| arm2a | performance_chasing_0p4 | 5 | 1.22 [0.28, 5.37] | 1.39 [0.30, 5.56] | 1.13 | 1.03 | 1.37 [0.30, 5.53] | 1.12 | 1.03 | 4.30 |
| arm2a | performance_chasing | 5 | 1.22 [0.28, 5.37] | 1.53 [0.31, 6.19] | 1.25 | 1.14 | 1.51 [0.31, 6.11] | 1.24 | 1.13 | 4.29 |
