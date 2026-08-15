"""
figure_data.py
--------------
Every quantity plotted in the paper, with an explicit provenance flag so the
author can see exactly which numbers are taken verbatim from the manuscript's
tables and which are reconstructions to be replaced with exact model output.

Provenance legend
-----------------
EXACT        : copied verbatim from a numbered table in the manuscript.
DERIVED      : algebraically implied by reported numbers under the stated,
               design-guaranteed assumption (uniform randomisation => the
               "AI decides alone" process level is 1/3 of profiles and the two
               human-involved levels are 2/3). These reproduce the original
               figures to reading precision.
APPROX-CI    : point estimate is EXACT/DERIVED; the confidence interval is an
               approximation (read from the original render / scaled by the
               1/3 vs 2/3 data split). REPLACE with the exact CIs from your model.
ILLUSTRATIVE : the underlying quantity requires per-respondent raw data not
               present in the manuscript; the values here are simulated to match
               the reported summary moments and are for display only.
"""

# --------------------------------------------------------------------------- #
# Figure 1 & Table C1 -- AMCEs on P(choice).  Provenance: EXACT (Table C1)     #
# --------------------------------------------------------------------------- #
AMCE = [
    # label, estimate, ci_lo, ci_hi, group
    ("AI suggests, human decides",      0.287, 0.273, 0.301, "process"),
    ("AI screens first, human decides", 0.257, 0.244, 0.271, "process"),
    ("Appeal (re-review)",              0.156, 0.145, 0.167, "procedural"),
    ("Opt-out (human from start)",      0.129, 0.118, 0.140, "procedural"),
    ("Explanation",                     0.128, 0.118, 0.139, "procedural"),
    ("Independent bias audit",          0.068, 0.058, 0.079, "procedural"),
    ("Error rate (per −1 pp)",         0.014, 0.014, 0.015, "accuracy"),
]
# Full-range accuracy effect for the de-jargoning annotation (EXACT: -0.014*20).
ACCURACY_FULL_RANGE = -0.285      # over the 10 -> 30 % error range
ACCURACY_20PP_GAIN  = 0.285      # effect of a 20 pp reduction in error

# --------------------------------------------------------------------------- #
# Table C3 -- marginal means (Supp. Fig. S1).  Provenance: EXACT (Table C3)    #
# --------------------------------------------------------------------------- #
MARGINAL_MEANS = [
    # label, mm, lo, hi, group
    ("AI decides alone",               0.320, 0.311, 0.328, "Decision authority"),
    ("AI screens first, human decides",0.575, 0.567, 0.583, "Decision authority"),
    ("AI suggests, human decides",     0.604, 0.596, 0.612, "Decision authority"),
    ("Error rate 30%",                 0.357, 0.349, 0.366, "Error rate"),
    ("Error rate 20%",                 0.499, 0.491, 0.507, "Error rate"),
    ("Error rate 10%",                 0.642, 0.634, 0.651, "Error rate"),
    ("No explanation",                 0.437, 0.431, 0.443, "Explanation"),
    ("Explanation",                    0.564, 0.558, 0.570, "Explanation"),
    ("No opt-out",                     0.435, 0.429, 0.441, "Opt-out"),
    ("Opt-out available",              0.565, 0.559, 0.571, "Opt-out"),
    ("No appeal",                      0.423, 0.417, 0.429, "Appeal"),
    ("Appeal available",               0.579, 0.573, 0.585, "Appeal"),
    ("No bias audit",                  0.466, 0.460, 0.471, "Bias audit"),
    ("Bias audit available",           0.535, 0.529, 0.540, "Bias audit"),
]

# --------------------------------------------------------------------------- #
# Figure 2A & Table D1 -- error-rate moderation, 90% CI.  Provenance: EXACT    #
# SESOI = 0.05.  Human involvement is the sole non-equivalent estimate.           #
# --------------------------------------------------------------------------- #
SESOI = 0.05
MODERATION = [
    # label, moderation over 10-30%, ci90_lo, ci90_hi, equivalent(bool)
    ("Appeal",               0.001, -0.020, 0.022, True),
    ("Opt-out",              0.005, -0.016, 0.026, True),
    ("Explanation",          0.010, -0.011, 0.030, True),
    ("Bias audit",           0.012, -0.009, 0.032, True),
    ("Human involvement",-0.046, -0.067,-0.025, False),
]

# --------------------------------------------------------------------------- #
# Figure 2B -- P(chosen) for human-involved vs AI-alone by error rate.         #
# Provenance: DERIVED.  Contrasts 0.285/0.289/0.239 are EXACT (Sec 4.2);       #
# absolute levels solve  (1/3)A + (2/3)H = errorMM  and  H - A = contrast,      #
# with errorMM = 0.642/0.499/0.357 (Table C3). Matches the original render.    #
# --------------------------------------------------------------------------- #
ERR_RATES      = [10, 20, 30]
P_HUMAN        = [0.737, 0.595, 0.437]   # DERIVED
P_AIALONE      = [0.452, 0.306, 0.198]   # DERIVED
HUMAN_CONTRAST = [0.285, 0.289, 0.239]   # EXACT (reported)

# --------------------------------------------------------------------------- #
# Figure 3 -- each feature's AMCE with vs without a human.                      #
# Point estimates DERIVED from overall AMCE (Table C1) and the complementarity  #
# interactions (Table E2, Panel B: appeal +0.026, explanation +0.027,           #
# bias audit +0.029, opt-out -0.000) via AMCE = (2/3)H + (1/3)A and H - A = int.#
# CIs are APPROX-CI (read from the original render / scaled by the data split). #
# Ordered by the size of the shift so the flat opt-out ends the sequence.       #
# --------------------------------------------------------------------------- #
COMPLEMENTARITY = [
    # label, amce_aialone, ci_a_lo, ci_a_hi, amce_human, ci_h_lo, ci_h_hi, delta
    ("Bias audit",   0.049, 0.031, 0.066, 0.078, 0.065, 0.091, 0.029),
    ("Explanation",  0.110, 0.092, 0.129, 0.137, 0.124, 0.150, 0.027),
    ("Appeal",       0.139, 0.122, 0.156, 0.165, 0.151, 0.178, 0.025),
    ("Opt-out",      0.129, 0.111, 0.147, 0.129, 0.116, 0.142, 0.000),
]

# --------------------------------------------------------------------------- #
# Figure 4 -- joint distribution of legitimacy belief (rows 1..5) x intention  #
# to apply (cols 1..5).  Provenance: EXACT -- read from the embedded figure;    #
# the 25 cells sum to 1919 and reproduce mean intention 3.24, mean legitimacy   #
# 2.85, and the doubt-but-engage share 7.8% (legitimacy<=2 & intention>=4).     #
# COUNTS[i][j] = legitimacy (i+1), intention (j+1).                             #
# --------------------------------------------------------------------------- #
JOINT_COUNTS = [
    [140,  48,  46,  30,   6],   # legitimacy = 1
    [ 31, 151, 166, 106,   8],   # legitimacy = 2
    [  5,  73, 215, 236,  14],   # legitimacy = 3
    [  2,  14,  73, 430,  62],   # legitimacy = 4
    [  0,   1,   2,   7,  53],   # legitimacy = 5
]

# --------------------------------------------------------------------------- #
# Figure 5 -- SESOI sensitivity.  Provenance: EXACT (Table D1 reports the       #
# preregistered ±0.05 test; the ±0.03 / ±0.07 bounds appear in Figure 5).       #
# --------------------------------------------------------------------------- #
SESOI_THRESHOLDS = [0.03, 0.05, 0.07]      # dotted / solid(pre-reg) / dashed
SENSITIVITY = [
    # label, change over 10-30%, ci90_lo, ci90_hi, smallest SESOI passed, equivalent
    ("Appeal",               0.001, -0.020, 0.022, 0.03, True),
    ("Opt-out",              0.005, -0.016, 0.026, 0.03, True),
    ("Explanation",          0.010, -0.011, 0.030, 0.05, True),
    ("Bias audit",           0.012, -0.009, 0.032, 0.05, True),
    ("Human involvement",-0.046, -0.067,-0.025, 0.07, False),
]

# --------------------------------------------------------------------------- #
# Supp. Fig. S2 & Table E1 -- conditional AMCE of human involvement by subgroup.#
# Provenance: EXACT (Table E1).  Pooled reference = 0.272.                       #
# --------------------------------------------------------------------------- #
POOLED_HUMAN_AMCE = 0.272
SUBGROUPS = [
    # label, amce, lo, hi, group
    ("All respondents",     0.272, 0.260, 0.284, "pooled"),
    ("Prior AI exp: Yes",   0.269, 0.255, 0.283, "experience"),
    ("Prior AI exp: No or not sure",    0.282, 0.258, 0.307, "experience"),  # CHANGED: binary 0 pools "No" and "Not sure"
    ("Women",               0.289, 0.273, 0.304, "gender"),
    ("Men",                 0.253, 0.234, 0.271, "gender"),
]

# --------------------------------------------------------------------------- #
# Figure H1 / Supp. Fig. S3 -- within-respondent human-preference distribution. #
# Provenance: ILLUSTRATIVE.  Reported moments used to constrain the simulation: #
#   mean = 0.29 ; observed SD = 0.30 ; null SD = 0.27 ; true between-person     #
#   SD ~= 0.13 ; 77% of respondents on the positive side ; N = 1911 ; 8 tasks.  #
# REPLACE the simulation in make_figures.py with your raw per-respondent stat   #
# to reproduce these two panels exactly.                                        #
# --------------------------------------------------------------------------- #
PREF_MEAN        = 0.29
PREF_SD_OBSERVED = 0.30
PREF_SD_NULL     = 0.27
PREF_SD_TRUE     = 0.13
PREF_SHARE_POS   = 0.77
N_RESP           = 1911
N_TASKS          = 8

# --------------------------------------------------------------------------- #
# Table 2 -- example paired-profile task (UI mock-up).  ILLUSTRATIVE levels;    #
# on-screen wording retained deliberately (see manuscript Sec 3.2 note).        #
# --------------------------------------------------------------------------- #
TASK_ROWS = [
    ("Decision process",                        "AI screens, human decides", "AI decides alone"),
    ("Accuracy (qualified applicants\nwrongly rejected)", "~20%",             "~30%"),
    ("Meaningful explanation",                  "Yes",                       "No"),
    ("Human option from the start",             "No",                        "Yes"),
    ("Human re-review if rejected",             "Yes",                       "No"),
    ("Independent bias audit",                  "Yes",                       "No"),
]
