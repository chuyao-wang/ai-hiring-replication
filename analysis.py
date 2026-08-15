"""
analysis.py
-----------
Computes every figure input directly from the raw data (conjoints.csv,
respondents.csv), reproducing the manuscript's estimation exactly:

    OLS linear probability model, standard errors clustered by respondent,
    the error rate entered continuously (per +1 pp), decision authority as
    two dummies against "AI decides alone", and each procedural feature as a 0/1
    indicator.

Validated against the paper's tables: all AMCEs (Table C1), marginal means
(Table C3), error-rate moderations / equivalence (Table D1), complementarity
interactions (Table E2), and subgroup conditional AMCEs (Table E1) reproduce to
the third decimal, and the within-respondent preference moments match Appendix H.

`compute_all(...)` returns a namespace whose attribute names match figure_data,
so make_figures.py can use it as a drop-in replacement.
"""
from types import SimpleNamespace
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import figure_data as FD   # for the static task mock-up levels

Z90, Z95 = 1.645, 1.959964
BASE = "accuracy_pct + transparency + opt_out + appeal + bias_audit"


def _fit(df, formula):
    return smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["respondent_id"]})


def _mm(df):
    """Marginal mean and 95% CI of `chosen` on a subset (cluster-robust)."""
    m = _fit(df, "chosen ~ 1")
    est = m.params["Intercept"]; se = m.bse["Intercept"]
    return est, est - Z95 * se, est + Z95 * se


def compute_all(conjoints_path="data/conjoints.csv",
                respondents_path="data/respondents.csv"):
    c = pd.read_csv(conjoints_path)
    r = pd.read_csv(respondents_path)
    c["suggest"] = (c.decision_process_code == "suggest_human_decides").astype(int)
    c["screen"]  = (c.decision_process_code == "screen_human_decides").astype(int)
    c = c.merge(r[["respondent_id", "Q3_ai_exp_binary", "Sex",
                   "Q9_1_legitimacy", "Q9_2_intention_apply"]],
                on="respondent_id", how="left")

    # -- Figure 1 / Table C1: AMCEs (95% CI) --------------------------------- #
    m = _fit(c, f"chosen ~ suggest + screen + {BASE}")
    ci = m.conf_int()
    def amce(v): return m.params[v], ci.loc[v, 0], ci.loc[v, 1]
    def amce_neg(v):  # per -1 pp error: negate estimate and swap/negate the CI
        e, lo, hi = m.params[v], ci.loc[v, 0], ci.loc[v, 1]
        return -e, -hi, -lo
    AMCE = [
        ("AI suggests, human decides",      *amce("suggest"),      "process"),
        ("AI screens first, human decides", *amce("screen"),       "process"),
        ("Appeal (re-review)",              *amce("appeal"),       "procedural"),
        ("Opt-out (human from start)",      *amce("opt_out"),      "procedural"),
        ("Explanation",                     *amce("transparency"), "procedural"),
        ("Independent bias audit",          *amce("bias_audit"),   "procedural"),
        ("Error rate (per \u22121 pp)",     *amce_neg("accuracy_pct"), "accuracy"),
    ]
    # effect of a 20 pp reduction in the error rate (a -20 pp change), positive,
    # for comparison with the discrete component effects
    ACCURACY_20PP_GAIN = round(m.params["accuracy_pct"] * -20, 3)
    ACCURACY_FULL_RANGE = round(m.params["accuracy_pct"] * 20, 3)

    # -- Figure S1 / Table C3: marginal means -------------------------------- #
    MM = []
    for lab, sub, grp in [
        ("AI decides alone",                c.decision_process_code == "AI_alone", "Decision authority"),
        ("AI screens first, human decides", c.decision_process_code == "screen_human_decides", "Decision authority"),
        ("AI suggests, human decides",      c.decision_process_code == "suggest_human_decides", "Decision authority"),
        ("Error rate 30%", c.accuracy_pct == 30, "Error rate"),
        ("Error rate 20%", c.accuracy_pct == 20, "Error rate"),
        ("Error rate 10%", c.accuracy_pct == 10, "Error rate"),
        ("No explanation", c.transparency == 0, "Explanation"),
        ("Explanation",    c.transparency == 1, "Explanation"),
        ("No opt-out",        c.opt_out == 0, "Opt-out"),
        ("Opt-out available", c.opt_out == 1, "Opt-out"),
        ("No appeal",        c.appeal == 0, "Appeal"),
        ("Appeal available", c.appeal == 1, "Appeal"),
        ("No bias audit",        c.bias_audit == 0, "Bias audit"),
        ("Bias audit available", c.bias_audit == 1, "Bias audit"),
    ]:
        est, lo, hi = _mm(c[sub]); MM.append((lab, est, lo, hi, grp))

    # -- Figure 2A / 5 / Table D1: error-rate moderation over 10-30, 90% CI  #
    SESOI = 0.05
    def moderation(term_formula, key):
        mm = _fit(c, term_formula)
        b = mm.params[key] * 20; se = mm.bse[key] * 20
        return b, b - Z90 * se, b + Z90 * se
    MOD = []
    for S, lab in [("appeal", "Appeal"), ("opt_out", "Opt-out"),
                   ("transparency", "Explanation"), ("bias_audit", "Bias audit")]:
        est, lo, hi = moderation(f"chosen ~ suggest + screen + {BASE} + {S}:accuracy_pct",
                                 f"{S}:accuracy_pct")
        MOD.append((lab, est, lo, hi, (lo > -SESOI and hi < SESOI)))
    est, lo, hi = moderation(f"chosen ~ human_involved + {BASE} + human_involved:accuracy_pct",
                             "human_involved:accuracy_pct")
    MOD.append(("Human involvement", est, lo, hi, (lo > -SESOI and hi < SESOI)))
    MODERATION = MOD

    # sensitivity: smallest passed threshold among 0.03/0.05/0.07
    THRESH = [0.03, 0.05, 0.07]
    SENS = []
    for lab, est, lo, hi, equiv in MODERATION:
        passed = next((t for t in THRESH if lo > -t and hi < t), None)
        SENS.append((lab, est, lo, hi, passed, equiv))

    # -- Figure 2B: P(chosen) by human_involved x error rate ----------------- #
    cell = c.groupby(["human_involved", "accuracy_pct"])["chosen"].mean()
    ERR = [10, 20, 30]
    pa_raw = [cell[(0, e)] for e in ERR]
    ph_raw = [cell[(1, e)] for e in ERR]
    P_AIALONE = [round(a, 3) for a in pa_raw]
    P_HUMAN   = [round(h, 3) for h in ph_raw]
    # contrast from UNROUNDED means (rounding the two levels first would give
    # 0.290 at 20% error; the single-rounded contrast is 0.289, matching the text)
    CONTRAST  = [round(h - a, 3) for h, a in zip(ph_raw, pa_raw)]

    # -- Figure 3: feature AMCE with vs without a human ----------------------- #
    # Interaction-model basis (reproduces the paper's reported interactions,
    # e.g. appeal 0.025 [0.004, 0.047]): the conditional AMCE at human=0 is the
    # feature main effect; at human=1 it is main + interaction; delta is the
    # interaction coefficient, so the label equals the plotted difference exactly.
    COMP = []
    for S, lab in [("appeal", "Appeal"), ("transparency", "Explanation"),
                   ("bias_audit", "Bias audit"), ("opt_out", "Opt-out")]:
        mm = _fit(c, f"chosen ~ human_involved + {BASE} + {S}:human_involved")
        b0, bi = mm.params[S], mm.params[f"{S}:human_involved"]
        ci0 = mm.conf_int().loc[S]
        names = [S, f"{S}:human_involved"]
        cov = mm.cov_params().loc[names, names].values
        se1 = float(np.sqrt(np.array([1.0, 1.0]) @ cov @ np.array([1.0, 1.0])))
        e1 = b0 + bi
        COMP.append((lab, b0, ci0[0], ci0[1], e1, e1 - Z95 * se1, e1 + Z95 * se1, bi))
    COMP.sort(key=lambda t: -t[7])   # order by shift so flat opt-out ends

    # -- Figure 4: joint distribution ---------------------------------------- #
    ct = pd.crosstab(r.Q9_1_legitimacy, r.Q9_2_intention_apply).reindex(
        index=[1, 2, 3, 4, 5], columns=[1, 2, 3, 4, 5], fill_value=0)
    JOINT = ct.values.astype(int).tolist()

    # -- Figure S2 / Table E1: conditional AMCE of human involvement --------- #
    def amce_h(df):
        mm = _fit(df, f"chosen ~ human_involved + {BASE}")
        c2 = mm.conf_int()
        return mm.params["human_involved"], c2.loc["human_involved", 0], c2.loc["human_involved", 1]
    POOLED, plo, phi = amce_h(c)
    SUB = [("All respondents", POOLED, plo, phi, "pooled")]
    for lab, sub, grp in [("Prior AI exp: Yes", c.Q3_ai_exp_binary == 1, "experience"),
                          ("Prior AI exp: No or not sure", c.Q3_ai_exp_binary == 0, "experience"),  # CHANGED: binary 0 pools "No" and "Not sure"
                          ("Women", c.Sex == "Female", "gender"),
                          ("Men",   c.Sex == "Male",   "gender")]:
        SUB.append((lab, *amce_h(c[sub]), grp))

    # -- Figures A1 / A6: within-respondent human preference + null ---------- #
    g = c.groupby(["respondent_id", "human_involved"])["chosen"].agg(["mean", "size"]).unstack("human_involved")
    pref = (g["mean"][1] - g["mean"][0]).dropna()
    nH = g["size"][1].loc[pref.index].values.astype(int)
    nA = g["size"][0].loc[pref.index].values.astype(int)
    obs = pref.values
    pH_pop = c.loc[c.human_involved == 1, "chosen"].mean()
    pA_pop = c.loc[c.human_involved == 0, "chosen"].mean()
    rng = np.random.default_rng(20260707)
    null = rng.binomial(nH, pH_pop) / nH - rng.binomial(nA, pA_pop) / nA
    # null SD averaged over replications for a stable annotation
    sds = [ (rng.binomial(nH, pH_pop)/nH - rng.binomial(nA, pA_pop)/nA).std(ddof=0)
            for _ in range(200) ]
    obs_sd = float(np.std(obs, ddof=0)); null_sd = float(np.mean(sds))
    true_sd = float(np.sqrt(max(obs_sd**2 - null_sd**2, 0)))

    return SimpleNamespace(
        AMCE=AMCE, ACCURACY_FULL_RANGE=ACCURACY_FULL_RANGE,
        ACCURACY_20PP_GAIN=ACCURACY_20PP_GAIN,
        MARGINAL_MEANS=MM, SESOI=SESOI, MODERATION=MODERATION,
        SESOI_THRESHOLDS=THRESH, SENSITIVITY=SENS,
        ERR_RATES=ERR, P_HUMAN=P_HUMAN, P_AIALONE=P_AIALONE, HUMAN_CONTRAST=CONTRAST,
        COMPLEMENTARITY=COMP, JOINT_COUNTS=JOINT,
        POOLED_HUMAN_AMCE=round(POOLED, 3), SUBGROUPS=SUB,
        PREF_OBSERVED=obs, PREF_NULL=null,
        PREF_MEAN=round(float(np.mean(obs)), 3),
        PREF_SD_OBSERVED=round(obs_sd, 3), PREF_SD_NULL=round(null_sd, 3),
        PREF_SD_TRUE=round(true_sd, 3),
        PREF_SHARE_POS=round(float((obs > 0).mean()), 3),
        N_RESP=len(obs), N_TASKS=FD.N_TASKS, TASK_ROWS=FD.TASK_ROWS,
    )


if __name__ == "__main__":
    d = compute_all()
    print("Computed from raw data:")
    print("  AMCE suggest =", round(d.AMCE[0][1], 3), "| error rate/pp full-range =", d.ACCURACY_FULL_RANGE)
    print("  human moderation =", round(d.MODERATION[-1][1], 3))
    print("  pref mean/SDobs/SDnull/SDtrue/pos =",
          d.PREF_MEAN, d.PREF_SD_OBSERVED, d.PREF_SD_NULL, d.PREF_SD_TRUE, d.PREF_SHARE_POS)
    print("  joint sum =", sum(sum(row) for row in d.JOINT_COUNTS))
