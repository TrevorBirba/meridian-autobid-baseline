# Mechanisms, strict gate

Strict gate: only fits with max R-hat at most 1.01 and min bulk ESS at least 400; a fit that fails it is nc and, in the baseline tables, left out.

### Arm 1

| row | channel | true avg | true marg | median est avg | median est marg | per-seed est avg | per-seed est marg | sign (4 of 5) | covered avg | covered marg | converged | median wall s | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | meta | 2.95 | 2.88 | 1.21 | 0.54 | 1.29, 1.16, 1.21, 1.18, 1.28 | 0.59, 0.53, 0.55, 0.53, 0.54 | low 5/5 | 5/5 | 2/5 | 5/5 | 23.6 | 1.89 | 0.94 | 1.20 |
| none | pla | 4.31 | 4.15 | 1.30 | 0.55 | 1.33, 1.28, 1.35, 1.18, 1.30 | 0.55, 0.54, 0.57, 0.49, 0.55 | low 5/5 | 5/5 | 0/5 | 5/5 | 23.6 | 1.93 | 0.97 | 1.30 |
| none | tv | 1.66 | 1.68 | 1.20 | 0.55 | 1.23, 1.21, 1.20, 1.17, 1.13 | 0.55, 0.56, 0.56, 0.54, 0.51 | low 5/5 | 5/5 | 5/5 | 5/5 | 23.6 | 1.92 | 0.95 | 1.19 |
| budget_feedback | meta | 2.95 | 2.88 | 1.18 | 0.54 | 1.24, 1.17, 1.18, nc, nc | 0.55, 0.52, 0.54, nc, nc | indeterminate 3/3 | 3/3 | 0/3 | 3/5 | 41.5 | 1.82 | 0.90 | 1.18 |
| budget_feedback | pla | 4.31 | 4.15 | 1.30 | 0.54 | 1.21, 1.30, 1.32, nc, nc | 0.49, 0.54, 0.55, nc, nc | indeterminate 3/3 | 3/3 | 0/3 | 3/5 | 41.5 | 1.85 | 0.93 | 1.29 |
| budget_feedback | tv | 1.66 | 1.68 | 1.18 | 0.56 | 1.24, 1.18, 1.17, nc, nc | 0.55, 0.56, 0.56, nc, nc | indeterminate 3/3 | 3/3 | 3/3 | 3/5 | 41.5 | 1.93 | 0.95 | 1.18 |
| anticipatory_spend | meta | 2.90 | 2.80 | 1.20 | 0.50 | nc, 1.20, 1.17, nc, 81.15 | nc, 0.50, 0.47, nc, 51.58 | indeterminate 2/3 | 2/3 | 0/3 | 3/5 | 69.4 | 1.99 | 0.89 | 1.17 |
| anticipatory_spend | pla | 4.21 | 4.00 | 47.18 | 28.50 | nc, 47.18, 50.50, nc, 1.15 | nc, 28.50, 31.84, nc, 0.47 | indeterminate 2/3 | 1/3 | 0/3 | 3/5 | 69.4 | 46.99 | 29.03 | 46.41 |
| anticipatory_spend | tv | 1.66 | 1.68 | 1.19 | 0.55 | nc, 1.19, 1.19, nc, 1.17 | nc, 0.54, 0.55, nc, 0.55 | indeterminate 3/3 | 3/3 | 3/3 | 3/5 | 69.4 | 1.87 | 0.93 | 1.19 |
| tv_bursts | meta | 2.95 | 2.88 | 1.25 | 0.54 | nc, nc, nc, 1.20, 1.29 | nc, nc, nc, 0.52, 0.56 | indeterminate 2/2 | 2/2 | 0/2 | 2/5 | 43.6 | 1.95 | 0.97 | 1.24 |
| tv_bursts | pla | 4.31 | 4.15 | 1.18 | 0.49 | nc, nc, nc, 1.16, 1.20 | nc, nc, nc, 0.46, 0.52 | indeterminate 2/2 | 1/2 | 0/2 | 2/5 | 43.6 | 1.71 | 0.85 | 1.17 |
| tv_bursts | tv | 1.56 | 1.67 | 1.68 | 0.43 | nc, nc, nc, 1.68, 1.67 | nc, nc, nc, 0.43, 0.43 | indeterminate 2/2 | 2/2 | 2/2 | 2/5 | 43.6 | 3.15 | 0.88 | 1.38 |
| performance_chasing | meta | 2.95 | 2.88 | 1.21 | 0.56 | 1.29, 1.19, 1.21, 1.18, 1.22 | 0.59, 0.52, 0.56, 0.53, 0.56 | low 5/5 | 5/5 | 1/5 | 5/5 | 64.5 | 2.01 | 0.99 | 1.20 |
| performance_chasing | pla | 4.29 | 4.15 | 37.50 | 22.66 | 34.27, 38.71, 37.50, 26.43, 41.16 | 20.61, 22.95, 22.66, 16.32, 24.96 | high 5/5 | 1/5 | 1/5 | 5/5 | 64.5 | 37.10 | 22.98 | 36.86 |
| performance_chasing | tv | 1.66 | 1.68 | 1.19 | 0.55 | 1.19, 1.18, 1.21, 1.22, 1.17 | 0.55, 0.52, 0.55, 0.53, 0.55 | low 5/5 | 5/5 | 5/5 | 5/5 | 64.5 | 1.91 | 0.95 | 1.18 |
| all_four | meta | 2.90 | 2.80 | 1.35 | 0.57 | 1.35, 1.21, 1.37, 1.34, 1.41 | 0.57, 0.51, 0.57, 0.57, 0.58 | low 5/5 | 5/5 | 4/5 | 5/5 | 63.0 | 2.38 | 1.11 | 1.33 |
| all_four | pla | 4.21 | 4.01 | 39.29 | 24.92 | 34.01, 39.79, 37.62, 39.29, 41.85 | 21.93, 24.92, 24.41, 25.29, 26.90 | high 5/5 | 0/5 | 0/5 | 5/5 | 63.0 | 38.95 | 25.35 | 38.49 |
| all_four | tv | 1.56 | 1.67 | 1.28 | 0.29 | 1.24, 1.32, 1.28, 1.28, 1.31 | 0.26, 0.30, 0.29, 0.29, 0.29 | low 5/5 | 5/5 | 0/5 | 5/5 | 63.0 | 1.80 | 0.46 | 1.06 |

### Arm 2a

| row | channel | true avg | true marg | median est avg | median est marg | per-seed est avg | per-seed est marg | sign (4 of 5) | covered avg | covered marg | converged | median wall s | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | meta | 2.95 | 2.88 | 1.39 | 0.60 | 1.51, 1.24, 1.62, 1.39, 1.11 | 0.73, 0.55, 0.77, 0.60, 0.47 | low 5/5 | 5/5 | 3/5 | 5/5 | 260.9 | 2.22 | 1.11 | 1.38 |
| none | pla | 4.31 | 4.15 | 1.50 | 0.66 | 1.64, 1.90, 1.50, 1.27, 1.20 | 0.76, 0.84, 0.66, 0.57, 0.53 | low 5/5 | 5/5 | 1/5 | 5/5 | 260.9 | 2.30 | 1.16 | 1.48 |
| none | tv | 1.66 | 1.68 | 1.19 | 0.52 | 1.21, 1.16, 1.18, 1.19, 1.19 | 0.52, 0.52, 0.52, 0.52, 0.52 | low 5/5 | 5/5 | 5/5 | 5/5 | 260.9 | 1.95 | 0.98 | 1.18 |
| budget_feedback | meta | 2.95 | 2.88 | 1.39 | 0.64 | 1.59, 1.34, nc, 1.43, 1.19 | 0.75, 0.60, nc, 0.67, 0.52 | indeterminate 4/4 | 4/4 | 3/4 | 4/5 | 256.5 | 2.22 | 1.11 | 1.38 |
| budget_feedback | pla | 4.31 | 4.15 | 1.54 | 0.69 | 1.72, 2.06, nc, 1.33, 1.35 | 0.77, 0.99, nc, 0.57, 0.60 | indeterminate 4/4 | 4/4 | 1/4 | 4/5 | 256.5 | 2.40 | 1.22 | 1.53 |
| budget_feedback | tv | 1.66 | 1.68 | 1.21 | 0.54 | 1.19, 1.28, nc, 1.19, 1.23 | 0.53, 0.56, nc, 0.52, 0.56 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 256.5 | 1.99 | 0.99 | 1.20 |
| anticipatory_spend | meta | 2.90 | 2.80 | 1.56 | 0.68 | 1.72, 1.56, 1.39, 1.57, nc | 0.75, 0.69, 0.61, 0.68, nc | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 304.1 | 2.62 | 1.23 | 1.53 |
| anticipatory_spend | pla | 4.21 | 4.00 | 2.00 | 0.84 | 2.00, 5.91, 1.67, 2.00, nc | 0.86, 3.08, 0.72, 0.82, nc | indeterminate 3/4 | 4/4 | 2/4 | 4/5 | 304.1 | 2.77 | 1.33 | 1.96 |
| anticipatory_spend | tv | 1.66 | 1.68 | 1.24 | 0.54 | 1.24, 1.25, 1.28, 1.20, nc | 0.52, 0.54, 0.56, 0.53, nc | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 304.1 | 1.93 | 0.96 | 1.23 |
| tv_bursts | meta | 2.95 | 2.88 | 1.17 | 0.53 | nc, 1.16, nc, 1.32, 1.17 | nc, 0.53, nc, 0.60, 0.51 | indeterminate 3/3 | 3/3 | 1/3 | 3/5 | 232.9 | 1.79 | 0.88 | 1.16 |
| tv_bursts | pla | 4.31 | 4.15 | 1.34 | 0.56 | nc, 1.82, nc, 1.34, 1.21 | nc, 0.82, nc, 0.56, 0.50 | indeterminate 3/3 | 3/3 | 1/3 | 3/5 | 232.9 | 1.93 | 0.96 | 1.33 |
| tv_bursts | tv | 1.56 | 1.67 | 1.79 | 0.47 | nc, 2.01, nc, 1.79, 1.62 | nc, 0.56, nc, 0.47, 0.40 | indeterminate 3/3 | 3/3 | 3/3 | 3/5 | 232.9 | 2.70 | 0.77 | 1.47 |
| performance_chasing | meta | 2.95 | 2.88 | 1.30 | 0.59 | nc, 1.21, 1.53, 1.38, 1.15 | nc, 0.56, 0.71, 0.62, 0.51 | indeterminate 4/4 | 4/4 | 2/4 | 4/5 | 276.4 | 2.04 | 1.01 | 1.29 |
| performance_chasing | pla | 4.29 | 4.15 | 1.49 | 0.63 | nc, 1.83, 1.44, 1.53, 1.33 | nc, 0.77, 0.60, 0.66, 0.56 | indeterminate 4/4 | 4/4 | 0/4 | 4/5 | 276.4 | 2.15 | 1.04 | 1.47 |
| performance_chasing | tv | 1.66 | 1.68 | 1.21 | 0.53 | nc, 1.22, 1.22, 1.15, 1.20 | nc, 0.52, 0.55, 0.48, 0.53 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 276.4 | 1.96 | 0.98 | 1.20 |
| all_four | meta | 2.90 | 2.80 | 1.69 | 0.73 | 1.72, 1.80, 1.67, nc, 1.34 | 0.76, 0.78, 0.71, nc, 0.57 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 316.5 | 2.71 | 1.30 | 1.66 |
| all_four | pla | 4.21 | 4.01 | 1.66 | 0.74 | 1.82, 2.38, 1.51, nc, 1.25 | 0.84, 1.15, 0.65, nc, 0.53 | indeterminate 4/4 | 4/4 | 0/4 | 4/5 | 316.5 | 2.09 | 1.02 | 1.62 |
| all_four | tv | 1.56 | 1.67 | 1.41 | 0.34 | 1.68, 1.28, 1.27, nc, 1.53 | 0.42, 0.32, 0.29, nc, 0.37 | indeterminate 3/4 | 4/4 | 2/4 | 4/5 | 316.5 | 2.16 | 0.57 | 1.17 |

### Step 1

| row | channel | true avg | true marg | median est avg | median est marg | per-seed est avg | per-seed est marg | sign (4 of 5) | covered avg | covered marg | converged | median wall s | median plug-in avg | median plug-in marg | median Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | meta | 2.95 | 2.88 | 1.16 | 0.87 | nc, 1.13, 1.17, 1.14, 1.32 | nc, 0.90, 0.85, 0.81, 1.09 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 53.0 | 2.62 | 2.56 | 1.14 |
| none | pla | 4.31 | 4.15 | 1.22 | 0.84 | nc, 1.24, 1.72, 1.08, 1.20 | nc, 0.87, 1.51, 0.62, 0.82 | indeterminate 4/4 | 4/4 | 3/4 | 4/5 | 53.0 | 2.86 | 2.82 | 1.21 |
| none | tv | 1.66 | 1.68 | 1.15 | 0.94 | nc, 1.19, 1.14, 1.16, 1.15 | nc, 0.95, 1.01, 0.92, 0.94 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 53.0 | 2.83 | 2.81 | 1.14 |
| budget_feedback | meta | 2.95 | 2.88 | 1.19 | 0.89 | 1.20, nc, 1.18, 1.08, 1.30 | 0.93, nc, 0.84, 0.75, 1.00 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 53.3 | 2.52 | 2.43 | 1.18 |
| budget_feedback | pla | 4.31 | 4.15 | 1.18 | 0.73 | 1.21, nc, 1.31, 1.06, 1.14 | 0.76, nc, 1.03, 0.61, 0.69 | indeterminate 4/4 | 4/4 | 3/4 | 4/5 | 53.3 | 2.12 | 1.98 | 1.16 |
| budget_feedback | tv | 1.66 | 1.68 | 1.18 | 0.90 | 1.18, nc, 1.20, 1.16, 1.18 | 0.91, nc, 0.89, 0.92, 0.89 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 53.3 | 2.71 | 2.62 | 1.17 |
| anticipatory_spend | meta | 2.90 | 2.80 | 1.15 | 0.68 | 10.18, 1.15, 1.12, nc, nc | 41.07, 0.67, 0.68, nc, nc | indeterminate 2/3 | 3/3 | 3/3 | 3/5 | 108.6 | 2.19 | 1.60 | 1.12 |
| anticipatory_spend | pla | 4.21 | 4.00 | 9.01 | 31.44 | 1.36, 9.68, 9.01, nc, nc | 0.77, 32.69, 31.44, nc, nc | indeterminate 2/3 | 1/3 | 1/3 | 3/5 | 108.6 | 10.78 | 37.39 | 9.45 |
| anticipatory_spend | tv | 1.66 | 1.68 | 1.17 | 0.94 | 1.30, 1.17, 1.10, nc, nc | 1.00, 0.94, 0.88, nc, nc | indeterminate 3/3 | 3/3 | 3/3 | 3/5 | 108.6 | 2.78 | 2.73 | 1.16 |
| tv_bursts | meta | 2.95 | 2.88 | 1.22 | 0.95 | nc, 1.18, 1.25, 1.14, 1.42 | nc, 0.89, 1.00, 0.81, 1.16 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 65.2 | 2.73 | 2.68 | 1.21 |
| tv_bursts | pla | 4.31 | 4.15 | 1.26 | 0.88 | nc, 1.27, 1.66, 1.08, 1.25 | nc, 0.90, 1.54, 0.69, 0.86 | indeterminate 4/4 | 4/4 | 3/4 | 4/5 | 65.2 | 2.47 | 2.45 | 1.25 |
| tv_bursts | tv | 1.56 | 1.67 | 2.56 | 0.66 | nc, 1.96, 2.19, 2.92, 3.28 | nc, 0.47, 0.52, 0.79, 1.16 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 65.2 | 4.42 | 1.39 | 1.80 |
| performance_chasing | meta | 2.95 | 2.88 | 1.26 | 0.99 | 1.38, 1.16, 1.19, nc, 1.33 | 1.17, 0.92, 0.92, nc, 1.06 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 80.1 | 3.69 | 3.80 | 1.25 |
| performance_chasing | pla | 4.29 | 4.15 | 8.27 | 19.88 | 6.84, 13.35, 7.79, nc, 8.76 | 16.26, 25.12, 18.68, nc, 21.09 | indeterminate 4/4 | 3/4 | 0/4 | 4/5 | 80.1 | 9.14 | 23.23 | 8.71 |
| performance_chasing | tv | 1.66 | 1.68 | 1.17 | 0.93 | 1.18, 1.22, 1.16, nc, 1.16 | 0.91, 0.94, 0.90, nc, 0.96 | indeterminate 4/4 | 4/4 | 4/4 | 4/5 | 80.1 | 2.77 | 2.71 | 1.16 |
| all_four | meta | 2.90 | 2.80 | 1.87 | 1.56 | 2.22, 1.34, 1.52, nc, 4.07 | 1.98, 0.82, 1.14, nc, 6.69 | indeterminate 3/4 | 4/4 | 4/4 | 4/5 | 94.6 | 5.08 | 6.14 | 1.81 |
| all_four | pla | 4.21 | 4.01 | 5.90 | 20.23 | 4.89, 6.89, 5.95, nc, 5.85 | 17.51, 24.92, 20.02, nc, 20.43 | indeterminate 4/4 | 4/4 | 1/4 | 4/5 | 94.6 | 7.09 | 23.29 | 7.14 |
| all_four | tv | 1.56 | 1.67 | 1.38 | 0.22 | 1.25, 1.42, 1.35, nc, 1.42 | 0.17, 0.22, 0.22, nc, 0.25 | indeterminate 4/4 | 4/4 | 1/4 | 4/5 | 94.6 | 2.03 | 0.37 | 1.00 |

### PLA, the three configurations side by side

| row | true avg | true marg | arm 1 median avg | arm 1 median marg | arm 1 per-seed avg | arm 1 sign | arm 1 covered | arm 1 converged | arm 1 median plug-in avg | arm 1 median Meridian ROI | arm 1 per-seed Meridian ROI | arm 2a median avg | arm 2a median marg | arm 2a per-seed avg | arm 2a sign | arm 2a covered | arm 2a converged | arm 2a median plug-in avg | arm 2a median Meridian ROI | arm 2a per-seed Meridian ROI | step 1 median avg | step 1 median marg | step 1 per-seed avg | step 1 sign | step 1 covered | step 1 converged | step 1 median plug-in avg | step 1 median Meridian ROI | step 1 per-seed Meridian ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 4.31 | 4.15 | 1.30 | 0.55 | 1.33, 1.28, 1.35, 1.18, 1.30 | low 5/5 | 5/5 | 5/5 | 1.93 | 1.30 | 1.33, 1.27, 1.34, 1.17, 1.30 | 1.50 | 0.66 | 1.64, 1.90, 1.50, 1.27, 1.20 | low 5/5 | 5/5 | 5/5 | 2.30 | 1.48 | 1.63, 1.89, 1.48, 1.27, 1.19 | 1.22 | 0.84 | nc, 1.24, 1.72, 1.08, 1.20 | indeterminate 4/4 | 4/4 | 4/5 | 2.86 | 1.21 | nc, 1.23, 1.71, 1.08, 1.19 |
| budget_feedback | 4.31 | 4.15 | 1.30 | 0.54 | 1.21, 1.30, 1.32, nc, nc | indeterminate 3/3 | 3/3 | 3/5 | 1.85 | 1.29 | 1.20, 1.29, 1.30, nc, nc | 1.54 | 0.69 | 1.72, 2.06, nc, 1.33, 1.35 | indeterminate 4/4 | 4/4 | 4/5 | 2.40 | 1.53 | 1.71, 2.06, nc, 1.32, 1.35 | 1.18 | 0.73 | 1.21, nc, 1.31, 1.06, 1.14 | indeterminate 4/4 | 4/4 | 4/5 | 2.12 | 1.16 | 1.19, nc, 1.30, 1.05, 1.13 |
| anticipatory_spend | 4.21 | 4.00 | 47.18 | 28.50 | nc, 47.18, 50.50, nc, 1.15 | indeterminate 2/3 | 1/3 | 3/5 | 46.99 | 46.41 | nc, 46.41, 49.74, nc, 1.13 | 2.00 | 0.84 | 2.00, 5.91, 1.67, 2.00, nc | indeterminate 3/4 | 4/4 | 4/5 | 2.77 | 1.96 | 1.96, 5.78, 1.64, 1.97, nc | 9.01 | 31.44 | 1.36, 9.68, 9.01, nc, nc | indeterminate 2/3 | 1/3 | 3/5 | 10.78 | 9.45 | 1.32, 10.09, 9.45, nc, nc |
| tv_bursts | 4.31 | 4.15 | 1.18 | 0.49 | nc, nc, nc, 1.16, 1.20 | indeterminate 2/2 | 1/2 | 2/5 | 1.71 | 1.17 | nc, nc, nc, 1.15, 1.20 | 1.34 | 0.56 | nc, 1.82, nc, 1.34, 1.21 | indeterminate 3/3 | 3/3 | 3/5 | 1.93 | 1.33 | nc, 1.81, nc, 1.33, 1.20 | 1.26 | 0.88 | nc, 1.27, 1.66, 1.08, 1.25 | indeterminate 4/4 | 4/4 | 4/5 | 2.47 | 1.25 | nc, 1.27, 1.64, 1.07, 1.24 |
| performance_chasing | 4.29 | 4.15 | 37.50 | 22.66 | 34.27, 38.71, 37.50, 26.43, 41.16 | high 5/5 | 1/5 | 5/5 | 37.10 | 36.86 | 33.65, 38.17, 36.86, 26.05, 40.43 | 1.49 | 0.63 | nc, 1.83, 1.44, 1.53, 1.33 | indeterminate 4/4 | 4/4 | 4/5 | 2.15 | 1.47 | nc, 1.81, 1.43, 1.51, 1.32 | 8.27 | 19.88 | 6.84, 13.35, 7.79, nc, 8.76 | indeterminate 4/4 | 3/4 | 4/5 | 9.14 | 8.71 | 7.22, 13.08, 8.25, nc, 9.18 |
| all_four | 4.21 | 4.01 | 39.29 | 24.92 | 34.01, 39.79, 37.62, 39.29, 41.85 | high 5/5 | 0/5 | 5/5 | 38.95 | 38.49 | 33.29, 39.04, 36.85, 38.49, 40.92 | 1.66 | 0.74 | 1.82, 2.38, 1.51, nc, 1.25 | indeterminate 4/4 | 4/4 | 4/5 | 2.09 | 1.62 | 1.77, 2.32, 1.47, nc, 1.22 | 5.90 | 20.23 | 4.89, 6.89, 5.95, nc, 5.85 | indeterminate 4/4 | 4/4 | 4/5 | 7.09 | 7.14 | 6.04, 8.17, 7.03, nc, 7.24 |

### PLA against the default ROI prior

PLA's ROI prior at every uncalibrated configuration (Meridian 2.0.0's default, read from the fitted model specification): LogNormal(0.2, 0.9), median 1.22, mean 1.83, 90 percent interval (5th to 95th percentile) [0.28, 5.37], width 5.09. Beside it, per uncalibrated cell: PLA's per-draw average return and Meridian's ROI (the quantity the prior is placed on), median [5th, 95th percentile] over the fit's saved draws, as medians over converged seeds; each ratio is the median over converged seeds of the per-fit ratio (median over the prior's median; interval width over the prior's interval width).

| config | row | converged | ROI prior median [90%] | per-draw avg [90%] | median / prior median | width / prior width | Meridian ROI [90%] | ROI median / prior median | ROI width / prior width | true avg |
|---|---|---|---|---|---|---|---|---|---|---|
| arm1 | none | 5 | 1.22 [0.28, 5.37] | 1.30 [0.28, 5.66] | 1.07 | 1.05 | 1.30 [0.28, 5.65] | 1.06 | 1.05 | 4.31 |
| arm1 | budget_feedback | 3 | 1.22 [0.28, 5.37] | 1.30 [0.28, 5.65] | 1.06 | 1.05 | 1.29 [0.28, 5.62] | 1.05 | 1.05 | 4.31 |
| arm1 | anticipatory_spend | 3 | 1.22 [0.28, 5.37] | 47.18 [33.80, 63.42] | 38.63 | 5.47 | 46.41 [33.27, 62.48] | 38.00 | 5.39 | 4.21 |
| arm1 | tv_bursts | 2 | 1.22 [0.28, 5.37] | 1.18 [0.27, 4.76] | 0.97 | 0.88 | 1.17 [0.27, 4.74] | 0.96 | 0.88 | 4.31 |
| arm1 | performance_chasing | 5 | 1.22 [0.28, 5.37] | 37.50 [22.63, 54.93] | 30.70 | 6.56 | 36.86 [22.25, 54.05] | 30.18 | 6.43 | 4.29 |
| arm1 | all_four | 5 | 1.22 [0.28, 5.37] | 39.29 [29.15, 51.53] | 32.17 | 4.40 | 38.49 [28.56, 50.47] | 31.51 | 4.30 | 4.21 |
| arm2a | none | 5 | 1.22 [0.28, 5.37] | 1.50 [0.31, 6.77] | 1.23 | 1.27 | 1.48 [0.31, 6.75] | 1.22 | 1.27 | 4.31 |
| arm2a | budget_feedback | 4 | 1.22 [0.28, 5.37] | 1.54 [0.33, 7.22] | 1.26 | 1.36 | 1.53 [0.33, 7.19] | 1.25 | 1.35 | 4.31 |
| arm2a | anticipatory_spend | 4 | 1.22 [0.28, 5.37] | 2.00 [0.37, 7.73] | 1.64 | 1.45 | 1.96 [0.36, 7.62] | 1.61 | 1.43 | 4.21 |
| arm2a | tv_bursts | 3 | 1.22 [0.28, 5.37] | 1.34 [0.28, 5.53] | 1.10 | 1.03 | 1.33 [0.28, 5.49] | 1.09 | 1.02 | 4.31 |
| arm2a | performance_chasing | 4 | 1.22 [0.28, 5.37] | 1.49 [0.31, 5.84] | 1.22 | 1.08 | 1.47 [0.30, 5.76] | 1.20 | 1.07 | 4.29 |
| arm2a | all_four | 4 | 1.22 [0.28, 5.37] | 1.66 [0.39, 5.28] | 1.36 | 0.96 | 1.62 [0.38, 5.15] | 1.33 | 0.94 | 4.21 |
| step1 | none | 4 | 1.22 [0.28, 5.37] | 1.22 [0.29, 5.55] | 1.00 | 1.03 | 1.21 [0.29, 5.52] | 0.99 | 1.03 | 4.31 |
| step1 | budget_feedback | 4 | 1.22 [0.28, 5.37] | 1.18 [0.27, 4.83] | 0.96 | 0.89 | 1.16 [0.27, 4.80] | 0.95 | 0.89 | 4.31 |
| step1 | anticipatory_spend | 3 | 1.22 [0.28, 5.37] | 9.01 [4.73, 16.30] | 7.37 | 2.27 | 9.45 [5.82, 16.14] | 7.74 | 2.03 | 4.21 |
| step1 | tv_bursts | 4 | 1.22 [0.28, 5.37] | 1.26 [0.29, 5.57] | 1.03 | 1.04 | 1.25 [0.28, 5.51] | 1.03 | 1.03 | 4.31 |
| step1 | performance_chasing | 4 | 1.22 [0.28, 5.37] | 8.27 [2.58, 21.01] | 6.77 | 3.75 | 8.71 [3.81, 20.40] | 7.13 | 3.30 | 4.29 |
| step1 | all_four | 4 | 1.22 [0.28, 5.37] | 5.90 [2.54, 11.30] | 4.83 | 1.62 | 7.14 [3.63, 11.76] | 5.84 | 1.46 | 4.21 |

### Fits that did not converge

| configuration | row | seed | max R-hat | min bulk ESS |
|---|---|---|---|---|
| arm 1 | anticipatory_spend | 20260908 | 24.891 | 7 |
| arm 1 | anticipatory_spend | 20260911 | 1.005 | 119 |
| arm 1 | budget_feedback | 20260911 | 1.288 | 39 |
| arm 1 | budget_feedback | 20260912 | 1.014 | 2526 |
| arm 1 | tv_bursts | 20260908 | 1.061 | 299 |
| arm 1 | tv_bursts | 20260909 | 1.014 | 1722 |
| arm 1 | tv_bursts | 20260910 | 1.026 | 1356 |
| arm 2a | all_four | 20260911 | 1.010 | 2591 |
| arm 2a | anticipatory_spend | 20260912 | 1.011 | 1015 |
| arm 2a | budget_feedback | 20260910 | 1.010 | 1392 |
| arm 2a | performance_chasing | 20260908 | 1.010 | 1639 |
| arm 2a | tv_bursts | 20260908 | 1.019 | 978 |
| arm 2a | tv_bursts | 20260910 | 1.018 | 1239 |
| step 1 | all_four | 20260911 | 1.027 | 406 |
| step 1 | anticipatory_spend | 20260911 | 1.027 | 783 |
| step 1 | anticipatory_spend | 20260912 | 1.033 | 424 |
| step 1 | budget_feedback | 20260909 | 1.012 | 1438 |
| step 1 | none | 20260908 | 1.032 | 610 |
| step 1 | performance_chasing | 20260911 | 1.064 | 351 |
| step 1 | tv_bursts | 20260908 | 1.326 | 42 |

### Knots chosen by automatic selection at arm 2a

| row | 20260908 | 20260909 | 20260910 | 20260911 | 20260912 |
|---|---|---|---|---|---|
| none | 46 | 49 | 47 | 43 | 43 |
| budget_feedback | 46 | 47 | 48 | 43 | 43 |
| anticipatory_spend | 44 | 48 | 44 | 48 | 43 |
| tv_bursts | 46 | 50 | 47 | 43 | 41 |
| performance_chasing | 46 | 48 | 45 | 43 | 44 |
| all_four | 45 | 49 | 41 | 48 | 45 |
