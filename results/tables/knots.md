# Knots

Arm 1 with the number of time knots fixed; arm 1 itself has one knot and arm 2a selects them automatically. Each cell: median over converged seeds. Baseline figures are weekly means over all 156 weeks, truth in parentheses.

| knots | row | n knots fitted | converged | true avg | median est avg | per-seed est avg | true marg | median est marg | per-seed est marg | covered avg | covered marg | corr(baseline, truth) | baseline mean (truth) | PLA contribution mean (truth) | corr(residual, PLA spend) | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (arm 1) | none | 1 | 5/5 | 4.31 | 1.30 | 1.33, 1.28, 1.35, 1.18, 1.30 | 4.15 | 0.55 | 0.55, 0.54, 0.57, 0.49, 0.55 | 5/5 | 0/5 | 0.28 | 2,534 (2,298) | 113 (260) | 0.03 | 1.93 | 0.97 | 1.30 |
| 1 (arm 1) | performance_chasing | 1 | 5/5 | 4.29 | 37.50 | 34.27, 38.71, 37.50, 26.43, 41.16 | 4.15 | 22.66 | 20.61, 22.95, 22.66, 16.32, 24.96 | 1/5 | 1/5 | 0.28 | 327 (2,298) | 2,228 (261) | 0.44 | 37.10 | 22.98 | 36.86 |
| 4 | none | 4 | 5/5 | 4.31 | 1.30 | 1.30, 1.33, 1.39, 1.18, 1.23 | 4.15 | 0.54 | 0.55, 0.54, 0.58, 0.47, 0.50 | 5/5 | 0/5 | 0.31 | 2,539 (2,298) | 119 (260) | 0.02 | 2.03 | 1.02 | 1.29 |
| 4 | performance_chasing | 4 | 5/5 | 4.29 | 34.88 | 32.12, 35.18, 34.88, 26.85, 38.33 | 4.15 | 21.21 | 19.88, 21.21, 21.73, 16.33, 23.83 | 1/5 | 1/5 | 0.29 | 475 (2,298) | 2,089 (261) | 0.45 | 34.54 | 21.11 | 34.30 |
| 13 | none | 13 | 5/5 | 4.31 | 1.29 | 1.39, 1.26, 1.38, 1.20, 1.29 | 4.15 | 0.54 | 0.60, 0.53, 0.59, 0.50, 0.54 | 5/5 | 0/5 | 0.29 | 2,580 (2,298) | 119 (260) | 0.04 | 2.04 | 1.03 | 1.29 |
| 13 | performance_chasing | 13 | 5/5 | 4.29 | 27.44 | 27.44, 20.43, 29.30, 3.16, 28.55 | 4.15 | 17.33 | 17.33, 12.26, 18.69, 1.58, 18.02 | 3/5 | 3/5 | 0.12 | 1,261 (2,298) | 1,659 (261) | 0.32 | 27.80 | 17.59 | 26.99 |
| 26 | none | 26 | 5/5 | 4.31 | 1.24 | 1.30, 1.24, 1.22, 1.21, 1.24 | 4.15 | 0.55 | 0.56, 0.55, 0.56, 0.51, 0.55 | 5/5 | 0/5 | 0.54 | 2,536 (2,298) | 113 (260) | 0.01 | 1.95 | 0.98 | 1.23 |
| 26 | performance_chasing | 26 | 5/5 | 4.29 | 2.82 | 7.63, 1.76, 2.87, 1.46, 2.82 | 4.15 | 1.39 | 4.49, 0.81, 1.39, 0.68, 1.40 | 5/5 | 5/5 | 0.53 | 2,372 (2,298) | 361 (261) | 0.28 | 6.91 | 3.74 | 2.78 |
| 52 | none | 52 | 5/5 | 4.31 | 1.14 | 1.14, 1.15, 1.20, 1.14, 1.13 | 4.15 | 0.51 | 0.53, 0.51, 0.52, 0.50, 0.48 | 4/5 | 0/5 | 0.73 | 2,558 (2,298) | 101 (260) | 0.02 | 1.74 | 0.86 | 1.14 |
| 52 | performance_chasing | 52 | 5/5 | 4.29 | 1.26 | 1.35, 1.15, 1.27, 1.15, 1.26 | 4.15 | 0.52 | 0.57, 0.51, 0.53, 0.51, 0.52 | 5/5 | 0/5 | 0.72 | 2,554 (2,298) | 113 (261) | 0.11 | 1.98 | 0.95 | 1.24 |
| automatic (arm 2a) | none | 43 to 49 | 5/5 | 4.31 | 1.50 | 1.64, 1.90, 1.50, 1.27, 1.20 | 4.15 | 0.66 | 0.76, 0.84, 0.66, 0.57, 0.53 | 5/5 | 1/5 | 0.94 | 2,464 (2,298) | 131 (260) | -0.04 | 2.30 | 1.16 | 1.48 |
| automatic (arm 2a) | performance_chasing | 43 to 48 | 5/5 | 4.29 | 1.53 | 2.12, 1.83, 1.44, 1.53, 1.33 | 4.15 | 0.66 | 0.98, 0.77, 0.60, 0.66, 0.56 | 5/5 | 0/5 | 0.94 | 2,439 (2,298) | 131 (261) | -0.05 | 2.26 | 1.11 | 1.51 |

PLA median average return on performance_chasing at 1, 4, 13, 26, 52 knots: 37.50, 34.88, 27.44, 2.82, 1.26; strictly falling: True.

### PLA against the default ROI prior

PLA's ROI prior at every uncalibrated configuration (Meridian 2.0.0's default, read from the fitted model specification): LogNormal(0.2, 0.9), median 1.22, mean 1.83, 90 percent interval (5th to 95th percentile) [0.28, 5.37], width 5.09. Beside it, per uncalibrated cell: PLA's per-draw average return and Meridian's ROI (the quantity the prior is placed on), median [5th, 95th percentile] over the fit's saved draws, as medians over converged seeds; each ratio is the median over converged seeds of the per-fit ratio (median over the prior's median; interval width over the prior's interval width).

| config | row | converged | ROI prior median [90%] | per-draw avg [90%] | median / prior median | width / prior width | Meridian ROI [90%] | ROI median / prior median | ROI width / prior width | true avg |
|---|---|---|---|---|---|---|---|---|---|---|
| arm1 | none | 5 | 1.22 [0.28, 5.37] | 1.30 [0.28, 5.66] | 1.07 | 1.05 | 1.30 [0.28, 5.65] | 1.06 | 1.05 | 4.31 |
| arm1 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 37.50 [22.63, 54.93] | 30.70 | 6.56 | 36.86 [22.25, 54.05] | 30.18 | 6.43 | 4.29 |
| knots4 | none | 5 | 1.22 [0.28, 5.37] | 1.30 [0.25, 5.56] | 1.06 | 1.04 | 1.29 [0.25, 5.53] | 1.06 | 1.04 | 4.31 |
| knots4 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 34.88 [21.70, 48.28] | 28.56 | 5.57 | 34.30 [21.35, 47.48] | 28.09 | 5.47 | 4.29 |
| knots13 | none | 5 | 1.22 [0.28, 5.37] | 1.29 [0.29, 5.89] | 1.06 | 1.10 | 1.29 [0.29, 5.79] | 1.05 | 1.08 | 4.31 |
| knots13 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 27.44 [2.45, 38.43] | 22.46 | 5.09 | 26.99 [2.42, 37.93] | 22.10 | 5.01 | 4.29 |
| knots26 | none | 5 | 1.22 [0.28, 5.37] | 1.24 [0.29, 5.25] | 1.02 | 0.97 | 1.23 [0.29, 5.24] | 1.01 | 0.97 | 4.31 |
| knots26 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 2.82 [0.34, 21.14] | 2.31 | 4.09 | 2.78 [0.34, 20.80] | 2.28 | 4.02 | 4.29 |
| knots52 | none | 5 | 1.22 [0.28, 5.37] | 1.14 [0.26, 4.46] | 0.94 | 0.83 | 1.14 [0.26, 4.44] | 0.93 | 0.82 | 4.31 |
| knots52 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 1.26 [0.28, 5.37] | 1.03 | 1.00 | 1.24 [0.28, 5.28] | 1.02 | 0.98 | 4.29 |
| arm2a | none | 5 | 1.22 [0.28, 5.37] | 1.50 [0.31, 6.77] | 1.23 | 1.27 | 1.48 [0.31, 6.75] | 1.22 | 1.27 | 4.31 |
| arm2a | performance_chasing | 5 | 1.22 [0.28, 5.37] | 1.53 [0.31, 6.19] | 1.25 | 1.14 | 1.51 [0.31, 6.11] | 1.24 | 1.13 | 4.29 |
