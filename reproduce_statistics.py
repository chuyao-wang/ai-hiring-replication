#!/usr/bin/env python3
"""
reproduce_statistics.py
-----------------------
Reproduces every numeric claim in the manuscript that is NOT already produced as
a figure input by ``analysis.py``. Running ``analysis.py`` verifies the figure
inputs (AMCEs, marginal means, equivalence tests, complementarity, subgroups,
within-respondent preference moments); running this script verifies the rest:

    * Table B1  -- sample characteristics (age, sex, prior-AI experience, quality checks)
    * Table C2  -- planned contrasts, pooled human involvement vs each feature
    * Sec 4.1   -- personal-recourse-vs-audit contrasts (AMCE and marginal-mean
                   scales; the marginal-mean CIs use a respondent-clustered
                   bootstrap)
    * Sec 4.1   -- the 20 pp error reduction vs human involvement, and the CI for
                   the difference between the two
    * Sec 4.2   -- the exploratory decision-authority sequence x error-rate
                   interaction ("AI suggests" vs "AI screens first")
    * Sec 4.2   -- conditional AMCEs at the 10% error rate (registered H2(a),
                   subsumed under H1a; see Appendix I)
    * Sec 4.5   -- decision-authority nested F (linear vs unordered factor)
    * Table E2  -- error-rate x feature and human x error-rate interactions under a
                   logit link (cluster-robust), plus a 10-20% subset check that is
                   an internal diagnostic and is not reported in the manuscript
    * Sec 4.4   -- attitude items (registered H5, reported descriptively): paired
                   test and the three attitude correlations
    * Sec 4.5   -- secondary acceptability-rating AMCEs and the rank correlation
    * App B/F   -- batch-indicator and left/right profile-position checks
    * App H     -- convergent validity: revealed human-preference vs stated attitudes
    * App H     -- the homogeneous-null SD 95% interval (fixed seed 20260707)

Estimation matches the manuscript: OLS linear probability model with standard
errors clustered by respondent; a logit link for the interaction robustness.

Note on reproducibility: point estimates and 95% CIs reproduce the manuscript to
the third decimal. The p-values of the non-significant interactions are mildly
sensitive to the finite-sample cluster-robust correction and can differ in the
second decimal across library versions; every such interaction remains
non-significant, so no conclusion changes. Pin the versions in requirements.txt
for bitwise agreement.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy.stats import norm, spearmanr

Z95 = 1.959964
BASE = "accuracy_pct + transparency + opt_out + appeal + bias_audit"
NULL_SEED = 20260707
NULL_REPS = 10000          # for the homogeneous-null SD interval
BOOT_REPS = 2000           # for the marginal-mean contrast CIs


def _load():
    c = pd.read_csv("data/conjoints.csv")
    r = pd.read_csv("data/respondents.csv")
    c["suggest"] = (c.decision_process_code == "suggest_human_decides").astype(int)
    c["screen"] = (c.decision_process_code == "screen_human_decides").astype(int)
    c["batch_main"] = c.batch.astype(str).str.lower().str.contains("main").astype(int)
    c = c.merge(r[["respondent_id", "Q9_1_legitimacy", "Q9_2_intention_apply",
                   "Q9_3_intention_withdraw"]], on="respondent_id", how="left")
    return c, r


def _ols(f, d):
    return smf.ols(f, data=d).fit(cov_type="cluster",
                                  cov_kwds={"groups": d["respondent_id"]})


def _logit(f, d):
    try:
        return smf.logit(f, data=d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d["respondent_id"]},
                                        disp=False, maxiter=200)
    except Exception:                                     # noqa: BLE001
        return smf.glm(f, data=d, family=sm.families.Binomial()).fit(
            cov_type="cluster", cov_kwds={"groups": d["respondent_id"]})


def _row(label, got, paper):
    print(f"  {label:44s} got = {got:<24s} paper = {paper}")


def _contrast(params, cov, a, b):
    e = params[a] - params[b]
    se = float(np.sqrt(cov.loc[a, a] + cov.loc[b, b] - 2 * cov.loc[a, b]))
    return e, e - Z95 * se, e + Z95 * se


def main():
    c, r = _load()

    print("=" * 92)
    print("Table B1 -- sample characteristics")
    print("=" * 92)
    _row("N respondents", f"{len(r)}", "1,919")
    _row("age mean / SD", f"{r.Age.mean():.1f} / {r.Age.std(ddof=1):.1f}", "36.6 / 12.1")
    _row("Female", f"{r.Sex.astype(str).str.lower().str.startswith('f').mean()*100:.1f}%", "54.6%")
    vc = r.Q3_ai_experience.value_counts(normalize=True) * 100
    _row("prior-AI yes / no / not sure",
         f"{vc.get('Yes', 0):.1f}% / {vc.get('No', 0):.1f}% / {vc.get('Not sure', 0):.1f}%",
         "74.9% / 12.5% / 12.6%")
    _row("manipulation-check pass", f"{(1 - r.flag_manip_fail.mean()) * 100:.1f}%", "92.4%")
    _row("straight-lining (ratings)", f"{r.flag_straightline_rating.mean() * 100:.1f}%", "4.1%")

    print("=" * 92)
    print("Table C2 -- pooled human involvement minus each feature")
    print("=" * 92)
    m = _ols(f"chosen ~ human_involved + {BASE}", c)
    b, V = m.params, m.cov_params()
    paper = {"appeal": "+0.116 [0.099, 0.133]", "opt_out": "+0.143 [0.127, 0.160]",
             "transparency": "+0.144 [0.128, 0.160]", "bias_audit": "+0.204 [0.188, 0.221]"}
    for s in ["appeal", "opt_out", "transparency", "bias_audit"]:
        e, lo, hi = _contrast(b, V, "human_involved", s)
        _row(f"human - {s}", f"{e:+.3f} [{lo:.3f}, {hi:.3f}]", paper[s])

    print("=" * 92)
    print("Sec 4.1 -- AMCE contrasts vs the collective bias audit")
    print("=" * 92)
    m2 = _ols(f"chosen ~ suggest + screen + {BASE}", c)
    b2, V2 = m2.params, m2.cov_params()
    e, lo, hi = _contrast(b, V, "human_involved", "bias_audit")
    _row("human (pooled) - audit", f"{e:+.3f} [{lo:.3f}, {hi:.3f}]", "+0.204 [0.188, 0.221]")
    e, lo, hi = _contrast(b2, V2, "appeal", "bias_audit")
    _row("appeal - audit", f"{e:+.3f} [{lo:.3f}, {hi:.3f}]", "+0.088 [0.073, 0.103]")
    e, lo, hi = _contrast(b2, V2, "opt_out", "bias_audit")
    _row("opt-out - audit", f"{e:+.3f} [{lo:.3f}, {hi:.3f}]", "+0.061 [0.045, 0.076]")

    # ---- added in this revision: the error-rate benchmark and its difference ----
    print("=" * 92)
    print("Sec 4.1 -- 20 pp error reduction as a benchmark for human involvement")
    print("=" * 92)
    _row("20 pp error reduction", f"{-20 * b['accuracy_pct']:+.3f}", "+0.285")
    _row("human involvement (pooled)", f"{b['human_involved']:+.3f}", "+0.272")
    # difference = (-20 * accuracy_pct) - human_involved
    w = {"accuracy_pct": -20.0, "human_involved": -1.0}
    d = sum(b[k] * wk for k, wk in w.items())
    sd = float(np.sqrt(sum(w[i] * w[j] * V.loc[i, j] for i in w for j in w)))
    _row("difference (20 pp - human)", f"{d:+.3f} [{d - Z95 * sd:.3f}, {d + Z95 * sd:.3f}]",
         "+0.013 [-0.007, 0.033]")

    # ---- added in this revision: exploratory sequence x error-rate interaction ----
    print("=" * 92)
    print("Sec 4.2 -- 'AI suggests' vs 'AI screens first' by error rate (exploratory)")
    print("=" * 92)
    ms = _ols(f"chosen ~ suggest + screen + {BASE} + suggest:accuracy_pct + screen:accuracy_pct", c)
    bs, Vs = ms.params, ms.cov_params()

    def _seq(v):
        """suggest minus screen at error rate v, with a cluster-robust CI."""
        w = {"suggest": 1.0, "screen": -1.0,
             "suggest:accuracy_pct": float(v), "screen:accuracy_pct": -float(v)}
        e = sum(bs[k] * wk for k, wk in w.items())
        se = float(np.sqrt(sum(w[i] * w[j] * Vs.loc[i, j] for i in w for j in w)))
        return e, se

    for v, pv in [(10, "+0.027 [0.008, 0.047]"), (20, "+0.030 [0.017, 0.043]"),
                  (30, "+0.032 [0.011, 0.053]")]:
        e, se = _seq(v)
        _row(f"suggest - screen @ {v}% error",
             f"{e:+.3f} [{e - Z95 * se:.3f}, {e + Z95 * se:.3f}]", pv)
    w = {"suggest:accuracy_pct": 20.0, "screen:accuracy_pct": -20.0}
    ch = sum(bs[k] * wk for k, wk in w.items())
    sch = float(np.sqrt(sum(w[i] * w[j] * Vs.loc[i, j] for i in w for j in w)))
    p = 2 * (1 - norm.cdf(abs(ch / sch)))
    _row("change over 10-30% error",
         f"{ch:+.3f} [{ch - Z95 * sch:.3f}, {ch + Z95 * sch:.3f}] (p = {p:.2f})",
         "+0.005 [-0.026, 0.036] (p = .77)")
    # a return proportional to the number of errors implies tripling the 10% contrast
    _row("proportional benchmark (2 x contrast @ 10%)", f"{2 * _seq(10)[0]:+.3f}", "about +0.055")
    _row("own moderations vs AI-alone (suggest / screen)",
         f"{20 * bs['suggest:accuracy_pct']:+.3f} / {20 * bs['screen:accuracy_pct']:+.3f}",
         "-0.044 / -0.048")

    print("=" * 92)
    print(f"Sec 4.1 -- marginal-mean contrasts vs audit (respondent-clustered bootstrap, "
          f"{BOOT_REPS} reps)")
    print("=" * 92)
    ids = c.respondent_id.unique()
    pos = {rid: k for k, rid in enumerate(ids)}
    S, N = {}, {}
    for nm, mk in {"hum": c.human_involved == 1, "audit": c.bias_audit == 1,
                   "appeal": c.appeal == 1, "opt": c.opt_out == 1}.items():
        a = c[mk].groupby("respondent_id")["chosen"].agg(["sum", "size"])
        s, n = np.zeros(len(ids)), np.zeros(len(ids))
        for rid, rr in a.iterrows():
            s[pos[rid]], n[pos[rid]] = rr["sum"], rr["size"]
        S[nm], N[nm] = s, n
    mm = lambda sel, nm: S[nm][sel].sum() / N[nm][sel].sum()
    full = np.arange(len(ids))
    pts = {"human-involved - audit": mm(full, "hum") - mm(full, "audit"),
           "appeal - audit": mm(full, "appeal") - mm(full, "audit"),
           "opt-out - audit": mm(full, "opt") - mm(full, "audit")}
    rng = np.random.default_rng(NULL_SEED)
    boot = {k: [] for k in pts}
    for _ in range(BOOT_REPS):
        sel = rng.integers(0, len(ids), len(ids))
        a = mm(sel, "audit")
        boot["human-involved - audit"].append(mm(sel, "hum") - a)
        boot["appeal - audit"].append(mm(sel, "appeal") - a)
        boot["opt-out - audit"].append(mm(sel, "opt") - a)
    pmm = {"human-involved - audit": "+0.055 [0.048, 0.063]",
           "appeal - audit": "+0.044 [0.036, 0.052]",
           "opt-out - audit": "+0.031 [0.022, 0.039]"}
    for k in pts:
        lo, hi = np.percentile(boot[k], [2.5, 97.5])
        _row(k, f"{pts[k]:+.3f} [{lo:.3f}, {hi:.3f}]", pmm[k])

    print("=" * 92)
    print("Sec 4.2 -- conditional AMCEs at the 10% error rate (registered H2(a); subsumed under H1a)")
    print("=" * 92)
    c10 = c[c.accuracy_pct == 10]
    m10h = _ols(f"chosen ~ human_involved + {BASE}", c10)
    _row("human @ 10%", f"{m10h.params['human_involved']:+.3f}", "+0.286")
    m10 = _ols(f"chosen ~ suggest + screen + {BASE}", c10)
    for s, pv in [("appeal", "+0.150"), ("opt_out", "+0.122"),
                  ("transparency", "+0.120"), ("bias_audit", "+0.066")]:
        _row(f"{s} @ 10%", f"{m10.params[s]:+.3f}", pv)

    print("=" * 92)
    print("Sec 4.5 -- decision-authority nested F (linear vs unordered factor)")
    print("=" * 92)
    fullf = smf.ols(f"chosen ~ C(decision_process_code) + {BASE}", data=c).fit()
    for nm, mp in [("AI-alone < screen < suggest",
                    {"AI_alone": 0, "screen_human_decides": 1, "suggest_human_decides": 2}),
                   ("AI-alone < suggest < screen",
                    {"AI_alone": 0, "suggest_human_decides": 1, "screen_human_decides": 2})]:
        c["_lin"] = c.decision_process_code.map(mp)
        red = smf.ols(f"chosen ~ _lin + {BASE}", data=c).fit()
        F = ((red.ssr - fullf.ssr) / (fullf.df_model - red.df_model)) / (fullf.ssr / fullf.df_resid)
        _row(f"nested F ({nm})", f"{F:.0f}", "838 or 432")

    print("=" * 92)
    print("Table E2 -- interaction p-values under LPM and logit (cluster-robust)")
    print("=" * 92)
    for s, pl, pg in [("appeal", ".94", ".87"), ("opt_out", ".69", ".82"),
                      ("transparency", ".45", ".64"), ("bias_audit", ".36", ".42")]:
        k = f"{s}:accuracy_pct"
        ml = _ols(f"chosen ~ suggest + screen + {BASE} + {k}", c)
        mg = _logit(f"chosen ~ suggest + screen + {BASE} + {k}", c)
        _row(f"{s} x error rate  LPM p / logit p",
             f"{ml.pvalues[k]:.2f} / {mg.pvalues[k]:.2f}", f"{pl} / {pg}")
    kh = "human_involved:accuracy_pct"
    mlh = _ols(f"chosen ~ human_involved + {BASE} + {kh}", c)
    mgh = _logit(f"chosen ~ human_involved + {BASE} + {kh}", c)
    _row("human x error rate  LPM p / logit p",
         f"{mlh.pvalues[kh]:.4f} / {mgh.pvalues[kh]:.2f}", ".0004 / .21")
    c12 = c[c.accuracy_pct <= 20]
    m12 = _ols(f"chosen ~ human_involved + {BASE} + {kh}", c12)
    _row("human x error rate, 10-20% subset (per 10 pp)",
         f"{m12.params[kh] * 10:+.3f} (p = {m12.pvalues[kh]:.2f})",
         "internal check; not reported in the text")

    print("=" * 92)
    print("Sec 4.4 -- attitude items (registered H5; reported descriptively)")
    print("=" * 92)
    leg, app, wd = r.Q9_1_legitimacy, r.Q9_2_intention_apply, r.Q9_3_intention_withdraw
    gap = app - leg
    t = gap.mean() / (gap.std(ddof=1) / np.sqrt(len(gap)))
    _row("paired diff / d_z / t",
         f"{gap.mean():.3f} / {gap.mean() / gap.std(ddof=1):.2f} / {t:.2f}",
         "0.389 / 0.42 / 18.56")
    _row("r(legit,apply) / (legit,withdraw) / (apply,withdraw)",
         f"{leg.corr(app):.2f} / {leg.corr(wd):.2f} / {app.corr(wd):.2f}", ".65 / -.46 / -.67")

    print("=" * 92)
    print("Sec 4.5 / App F -- secondary rating outcome, batch, left/right position")
    print("=" * 92)
    mr = _ols(f"rating ~ suggest + screen + {BASE}", c)
    _row("rating: suggest / appeal / transp / audit / acc",
         f"{mr.params['suggest']:+.3f} / {mr.params['appeal']:+.3f} / "
         f"{mr.params['transparency']:+.3f} / {mr.params['bias_audit']:+.3f} / "
         f"{mr.params['accuracy_pct']:+.3f}",
         "+0.653 / +0.303 / +0.304 / +0.147 / -0.026")
    ch = _ols(f"chosen ~ suggest + screen + {BASE}", c)
    terms = ["suggest", "screen", "appeal", "opt_out", "transparency", "bias_audit", "accuracy_pct"]
    rho = spearmanr([ch.params[t] for t in terms], [mr.params[t] for t in terms])[0]
    _row("rank corr(choice AMCE, rating AMCE)", f"{rho:.2f}", "0.89")
    mb = _ols(f"chosen ~ suggest + screen + {BASE} + batch_main", c)
    _row("batch indicator coef / p",
         f"{mb.params['batch_main']:+.4f} / {mb.pvalues['batch_main']:.2f}", "~0.0002 / .96")
    left = c[c.profile == c.profile.min()]
    _row("first-listed profile chosen rate", f"{left.chosen.mean() * 100:.1f}%", "~50.4%")

    print("=" * 92)
    print("App H -- convergent validity: revealed human-preference vs stated attitudes")
    print("=" * 92)
    gpref = c.groupby(["respondent_id", "human_involved"])["chosen"].mean().unstack("human_involved")
    hp = (gpref[1] - gpref[0]).rename("hp")
    mv = r.set_index("respondent_id").join(hp, how="inner").dropna(subset=["hp"])
    _row("corr(human-pref, legitimacy)", f"{mv['hp'].corr(mv.Q9_1_legitimacy):+.2f}", "-0.14")
    _row("corr(human-pref, intention to apply)", f"{mv['hp'].corr(mv.Q9_2_intention_apply):+.2f}", "-0.11")
    _row("corr(human-pref, intention to withdraw)", f"{mv['hp'].corr(mv.Q9_3_intention_withdraw):+.2f}", "+0.05")

    print("=" * 92)
    print(f"App H -- homogeneous-null SD 95% interval (seed {NULL_SEED}, {NULL_REPS} reps)")
    print("=" * 92)
    g = c.groupby(["respondent_id", "human_involved"])["chosen"].agg(["mean", "size"]).unstack("human_involved")
    pref = (g["mean"][1] - g["mean"][0]).dropna()
    nH = g["size"][1].loc[pref.index].values.astype(int)
    nA = g["size"][0].loc[pref.index].values.astype(int)
    pH = c.loc[c.human_involved == 1, "chosen"].mean()
    pA = c.loc[c.human_involved == 0, "chosen"].mean()
    rng = np.random.default_rng(NULL_SEED)
    sds = np.array([(rng.binomial(nH, pH) / nH - rng.binomial(nA, pA) / nA).std(ddof=0)
                    for _ in range(NULL_REPS)])
    lo, hi = np.percentile(sds, [2.5, 97.5])
    _row("null SD mean & 95% interval",
         f"{sds.mean():.3f} [{lo:.3f}, {hi:.3f}]", "0.27 [0.259, 0.276]")


if __name__ == "__main__":
    main()
