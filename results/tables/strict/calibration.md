# Calibration, strict gate

Strict gate: only fits with max R-hat at most 1.01 and min bulk ESS at least 400; a fit that fails it is nc and, in the baseline tables, left out.

PLA's ROI prior set from the go-dark experiment on the same instance (experiment.py); Meta and TV at Meridian's default. Uncalibrated rows are the arm 1 and arm 2a fits of the mechanisms set.

### The experiments and the priors they set

| row | seed | level | effect (SE) | true effect | iROAS [95%] | prior mean (sd) | prior loc, scale | experiment's true iROAS |
|---|---|---|---|---|---|---|---|---|
| none | 20260908 | weak | -802 (91) | -990 | 3.49 [2.66, 4.32] | 3.49 (sd 0.42) | 1.243, 0.121 | 4.31 |
| none | 20260909 | weak | -1,248 (228) | -1,093 | 4.90 [3.02, 6.78] | 4.90 (sd 0.96) | 1.571, 0.194 | 4.29 |
| none | 20260910 | weak | -675 (156) | -1,044 | 2.78 [1.43, 4.13] | 2.78 (sd 0.69) | 0.993, 0.244 | 4.30 |
| none | 20260911 | weak | -1,330 (171) | -1,094 | 5.22 [3.81, 6.64] | 5.22 (sd 0.72) | 1.644, 0.137 | 4.30 |
| none | 20260912 | weak | -944 (135) | -1,038 | 3.91 [2.73, 5.08] | 3.91 (sd 0.60) | 1.351, 0.152 | 4.30 |
| performance_chasing | 20260908 | weak | -698 (91) | -886 | 3.41 [2.48, 4.34] | 3.41 (sd 0.47) | 1.217, 0.138 | 4.33 |
| performance_chasing | 20260909 | weak | -1,242 (228) | -1,087 | 4.90 [3.02, 6.79] | 4.90 (sd 0.96) | 1.571, 0.195 | 4.29 |
| performance_chasing | 20260910 | weak | -618 (156) | -987 | 2.70 [1.27, 4.13] | 2.70 (sd 0.73) | 0.957, 0.266 | 4.31 |
| performance_chasing | 20260911 | weak | -1,223 (171) | -987 | 5.35 [3.78, 6.92] | 5.35 (sd 0.80) | 1.666, 0.149 | 4.31 |
| performance_chasing | 20260912 | weak | -792 (135) | -886 | 3.86 [2.48, 5.25] | 3.86 (sd 0.71) | 1.335, 0.181 | 4.32 |
| none | 20260908 | strong | -3,864 (181) | -4,051 | 4.11 [3.70, 4.51] | 4.11 (sd 0.21) | 1.411, 0.050 | 4.30 |
| none | 20260909 | strong | -3,838 (455) | -4,169 | 3.96 [2.97, 4.95] | 3.96 (sd 0.50) | 1.368, 0.127 | 4.30 |
| none | 20260910 | strong | -4,036 (312) | -4,164 | 4.17 [3.49, 4.85] | 4.17 (sd 0.35) | 1.425, 0.083 | 4.30 |
| none | 20260911 | strong | -5,265 (342) | -4,188 | 5.41 [4.67, 6.14] | 5.41 (sd 0.38) | 1.685, 0.070 | 4.30 |
| none | 20260912 | strong | -3,321 (270) | -4,082 | 3.50 [2.90, 4.10] | 3.50 (sd 0.31) | 1.249, 0.087 | 4.30 |
| performance_chasing | 20260908 | strong | -4,511 (181) | -4,698 | 4.07 [3.73, 4.42] | 4.07 (sd 0.18) | 1.403, 0.043 | 4.24 |
| performance_chasing | 20260909 | strong | -4,350 (455) | -4,680 | 3.94 [3.08, 4.81] | 3.94 (sd 0.44) | 1.366, 0.112 | 4.24 |
| performance_chasing | 20260910 | strong | -4,780 (312) | -4,907 | 4.11 [3.55, 4.68] | 4.11 (sd 0.29) | 1.412, 0.070 | 4.22 |
| performance_chasing | 20260911 | strong | -5,852 (342) | -4,775 | 5.20 [4.56, 5.84] | 5.20 (sd 0.33) | 1.647, 0.063 | 4.24 |
| performance_chasing | 20260912 | strong | -3,801 (270) | -4,561 | 3.54 [3.01, 4.07] | 3.54 (sd 0.27) | 1.261, 0.076 | 4.25 |

### PLA

| row | config | level | PLA avg median (per seed) | true avg | PLA marg median (per seed) | true marg | covered avg | covered marg | converged | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | arm 1 | uncalibrated | 1.30 (1.33, 1.28, 1.35, 1.18, 1.30) | 4.31 | 0.55 (0.55, 0.54, 0.57, 0.49, 0.55) | 4.15 | 5/5 | 0/5 | 5/5 | 1.93 | 0.97 | 1.30 |
| none | arm 1 | weak | 4.19 (3.51, 4.88, 2.73, 5.18, nc) | 4.31 | 1.98 (1.67, 2.28, 1.29, 2.36, nc) | 4.15 | 2/4 | 0/4 | 4/5 | 4.39 | 2.21 | 4.17 |
| none | arm 1 | strong | 4.03 (4.12, 3.94, 4.18, nc, 3.49) | 4.31 | 1.96 (2.04, 1.87, 2.06, nc, 1.61) | 4.15 | 3/4 | 0/4 | 4/5 | 4.22 | 2.12 | 4.01 |
| none | arm 2a | uncalibrated | 1.50 (1.64, 1.90, 1.50, 1.27, 1.20) | 4.31 | 0.66 (0.76, 0.84, 0.66, 0.57, 0.53) | 4.15 | 5/5 | 1/5 | 5/5 | 2.30 | 1.16 | 1.48 |
| none | arm 2a | weak | 3.88 (3.52, 5.01, nc, nc, 3.88) | 4.31 | 1.83 (1.83, 2.61, nc, nc, 1.81) | 4.15 | 3/3 | 1/3 | 3/5 | 4.08 | 1.96 | 3.86 |
| none | arm 2a | strong | 4.02 (4.13, 4.02, nc, nc, 3.50) | 4.31 | 2.13 (2.19, 2.13, nc, nc, 1.68) | 4.15 | 2/3 | 0/3 | 3/5 | 4.14 | 2.22 | 4.00 |
| performance_chasing | arm 1 | uncalibrated | 37.50 (34.27, 38.71, 37.50, 26.43, 41.16) | 4.29 | 22.66 (20.61, 22.95, 22.66, 16.32, 24.96) | 4.15 | 1/5 | 1/5 | 5/5 | 37.10 | 22.98 | 36.86 |
| performance_chasing | arm 1 | weak | 4.46 (3.58, 5.34, 2.95, 5.64, nc) | 4.29 | 2.41 (1.91, 2.92, 1.53, 3.11, nc) | 4.15 | 3/4 | 2/4 | 4/5 | 4.64 | 2.61 | 4.40 |
| performance_chasing | arm 1 | strong | 4.16 (4.16, 4.04, 4.23, 5.31, 3.61) | 4.29 | 2.35 (2.35, 2.15, 2.39, 2.98, 1.92) | 4.15 | 3/5 | 0/5 | 5/5 | 4.21 | 2.41 | 4.09 |
| performance_chasing | arm 2a | uncalibrated | 1.49 (nc, 1.83, 1.44, 1.53, 1.33) | 4.29 | 0.63 (nc, 0.77, 0.60, 0.66, 0.56) | 4.15 | 4/4 | 0/4 | 4/5 | 2.15 | 1.04 | 1.47 |
| performance_chasing | arm 2a | weak | 3.83 (3.50, 5.00, 2.72, 5.36, 3.83) | 4.29 | 1.81 (1.81, 2.37, 1.26, 2.59, 1.76) | 4.15 | 4/5 | 0/5 | 5/5 | 4.03 | 1.89 | 3.78 |
| performance_chasing | arm 2a | strong | 4.09 (nc, 4.01, 4.17, 5.27, 3.58) | 4.29 | 1.99 (nc, 1.99, 2.00, 2.59, 1.68) | 4.15 | 2/4 | 0/4 | 4/5 | 4.22 | 2.07 | 4.03 |

### Uncalibrated PLA against the default ROI prior

PLA's ROI prior at every uncalibrated configuration (Meridian 2.0.0's default, read from the fitted model specification): LogNormal(0.2, 0.9), median 1.22, mean 1.83, 90 percent interval (5th to 95th percentile) [0.28, 5.37], width 5.09. Beside it, per uncalibrated cell: PLA's per-draw average return and Meridian's ROI (the quantity the prior is placed on), median [5th, 95th percentile] over the fit's saved draws, as medians over converged seeds; each ratio is the median over converged seeds of the per-fit ratio (median over the prior's median; interval width over the prior's interval width).

| config | row | converged | ROI prior median [90%] | per-draw avg [90%] | median / prior median | width / prior width | Meridian ROI [90%] | ROI median / prior median | ROI width / prior width | true avg |
|---|---|---|---|---|---|---|---|---|---|---|
| arm1 | none | 5 | 1.22 [0.28, 5.37] | 1.30 [0.28, 5.66] | 1.07 | 1.05 | 1.30 [0.28, 5.65] | 1.06 | 1.05 | 4.31 |
| arm2a | none | 5 | 1.22 [0.28, 5.37] | 1.50 [0.31, 6.77] | 1.23 | 1.27 | 1.48 [0.31, 6.75] | 1.22 | 1.27 | 4.31 |
| arm1 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 37.50 [22.63, 54.93] | 30.70 | 6.56 | 36.86 [22.25, 54.05] | 30.18 | 6.43 | 4.29 |
| arm2a | performance_chasing | 4 | 1.22 [0.28, 5.37] | 1.49 [0.31, 5.84] | 1.22 | 1.08 | 1.47 [0.30, 5.76] | 1.20 | 1.07 | 4.29 |

### Meta and TV average return, median (true)

| row | config | level | Meta | TV |
|---|---|---|---|---|
| none | arm 1 | uncalibrated | 1.21 (2.95) | 1.20 (1.66) |
| none | arm 1 | weak | 1.22 (2.95) | 1.17 (1.66) |
| none | arm 1 | strong | 1.25 (2.95) | 1.19 (1.66) |
| none | arm 2a | uncalibrated | 1.39 (2.95) | 1.19 (1.66) |
| none | arm 2a | weak | 1.23 (2.95) | 1.17 (1.66) |
| none | arm 2a | strong | 1.21 (2.95) | 1.17 (1.66) |
| performance_chasing | arm 1 | uncalibrated | 1.21 (2.95) | 1.19 (1.66) |
| performance_chasing | arm 1 | weak | 1.25 (2.95) | 1.17 (1.66) |
| performance_chasing | arm 1 | strong | 1.25 (2.95) | 1.18 (1.66) |
| performance_chasing | arm 2a | uncalibrated | 1.30 (2.95) | 1.21 (1.66) |
| performance_chasing | arm 2a | weak | 1.35 (2.95) | 1.24 (1.66) |
| performance_chasing | arm 2a | strong | 1.25 (2.95) | 1.18 (1.66) |

### Arm 1 baseline on performance_chasing, all weeks

| level | baseline mean, median (per seed) | truth mean | corr(residual, PLA spend) | residual share of PLA contribution | PLA fitted / true | converged |
|---|---|---|---|---|---|---|
| uncalibrated | 327 (327, 446, 300, 1,100, 298) | 2,298 | 0.44 (0.44, 0.38, 0.46, 0.37, 0.46) | 0.86 (0.87, 0.85, 0.86, 0.79, 0.86) | 8.63 (7.83, 9.01, 8.63, 5.95, 9.47) | 5/5 |
| weak | 2,319 (2,157, 2,477, 2,344, 2,295) | 2,261 | 0.40 (0.43, 0.38, 0.45, 0.37) | -0.17 (-0.26, -0.08, -0.65, 0.01) | 1.04 (0.83, 1.26, 0.72, 1.31) | 4/4 |
| strong | 2,319 (2,126, 2,563, 2,277, 2,319, 2,562) | 2,298 | 0.43 (0.43, 0.38, 0.45, 0.37, 0.45) | -0.21 (-0.10, -0.46, -0.21, -0.06, -0.60) | 0.95 (0.95, 0.94, 0.97, 1.22, 0.84) | 5/5 |
