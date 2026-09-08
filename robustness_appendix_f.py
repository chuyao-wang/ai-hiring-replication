#!/usr/bin/env python3
"""robustness_appendix_f.py -- specification checks behind Appendix F.

Re-estimates the primary AMCE model under each data-quality restriction and
each positional control, and reports how far every attribute effect moves
from the preregistered baseline.

    python3 robustness_appendix_f.py

Baseline: OLS linear probability model of the binary profile choice on the
randomized attribute levels, standard errors clustered by respondent, the
specification of Table C1. Restrictions are applied ONE AT A TIME; the joint
restriction is reported separately because it drops 232 respondents at once.

"Shift" is the absolute change in an effect between the baseline and the
specification. Three columns report it over widening sets of quantities:
the four procedural features; those plus the two decision-authority levels;
and those plus the 20-percentage-point error-rate gain, which is a derived
quantity (the continuous coefficient times 20) rather than an AMCE.
"""
from __future__ import annotations
import ast, warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

BASE = "accuracy_pct + transparency + opt_out + appeal + bias_audit"
FORM = f"chosen ~ suggest + screen + {BASE}"
PROC = ["appeal", "opt_out", "transparency", "bias_audit"]
AUTH = ["suggest", "screen"]


def load(conjoints="data/conjoints.csv", respondents="data/respondents.csv"):
    c = pd.read_csv(conjoints)
    r = pd.read_csv(respondents)
    c["suggest"] = (c.decision_process_code == "suggest_human_decides").astype(int)
    c["screen"] = (c.decision_process_code == "screen_human_decides").astype(int)
    c = c.merge(r[["respondent_id", "duration_seconds", "flag_straightline_rating",
                   "flag_always_same_side", "flag_manip_fail"]],
                on="respondent_id", how="left")
    # attr_row_order stores the displayed order of the six attributes as a list.
    # Controlling for it as a 720-level factor is meaningless; control instead
    # for the row position each attribute occupied.
    pos = c.attr_row_order.map(lambda s: {v: i for i, v in enumerate(ast.literal_eval(s))})
    for j, nm in enumerate(["p_auth", "p_err", "p_expl", "p_opt", "p_app", "p_aud"]):
        c[nm] = pos.map(lambda d, j=j: d[j])
    return c, r


def fit(d, formula=FORM):
    return smf.ols(formula, data=d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d["respondent_id"]})


def effects(model, has_continuous_error=True):
    e = {t: model.params[t] for t in PROC + AUTH}
    e["acc20"] = model.params["accuracy_pct"] * -20 if has_continuous_error else np.nan
    return e


def main():
    c, r = load()
    base = effects(fit(c))
    print("Baseline AMCEs (Table C1): "
          "suggest {suggest:+.3f}  screen {screen:+.3f}  appeal {appeal:+.3f}  "
          "opt-out {opt_out:+.3f}  explanation {transparency:+.3f}  "
          "audit {bias_audit:+.3f}".format(**base))
    print(f"20-percentage-point error reduction: {base['acc20']:+.3f}\n")

    med = r.duration_seconds.median()
    anyflag = ((c.flag_straightline_rating == 1) | (c.flag_always_same_side == 1)
               | (c.flag_manip_fail == 1))
    specs = [
        (f"Completion time > 1/3 of median ({med/3:.0f} s)", c[c.duration_seconds > med / 3], FORM),
        ("Drop straight-lined ratings", c[c.flag_straightline_rating != 1], FORM),
        ("Drop always-same-side choosers", c[c.flag_always_same_side != 1], FORM),
        ("Drop failed manipulation check", c[c.flag_manip_fail != 1], FORM),
        ("Drop all three quality flags jointly", c[~anyflag], FORM),
        ("Task-position control", c, FORM + " + C(task)"),
        ("Attribute-row-position controls", c, FORM + " + p_auth + p_err + p_expl + p_opt + p_app + p_aud"),
        ("Profile-position control", c, FORM + " + C(profile)"),
        ("Unordered error-rate coding", c,
         "chosen ~ suggest + screen + C(accuracy_pct) + transparency + opt_out + appeal + bias_audit"),
    ]
    head = ("specification", "N", "4 procedural", "+ authority", "+ 20pp gain")
    print(f"{head[0]:42s}{head[1]:>6s}{head[2]:>15s}{head[3]:>14s}{head[4]:>14s}")
    print("-" * 91)
    worst = [0.0, 0.0, 0.0]
    singly = [0.0, 0.0, 0.0]          # excludes the joint-restriction row
    for name, d, formula in specs:
        cont = "C(accuracy_pct)" not in formula
        e = effects(fit(d, formula), cont)
        s1 = max(abs(e[t] - base[t]) for t in PROC)
        s2 = max(s1, max(abs(e[t] - base[t]) for t in AUTH))
        s3 = s2 if np.isnan(e["acc20"]) else max(s2, abs(e["acc20"] - base["acc20"]))
        worst = [max(worst[0], s1), max(worst[1], s2), max(worst[2], s3)]
        if "jointly" not in name:
            singly = [max(singly[0], s1), max(singly[1], s2), max(singly[2], s3)]
        print(f"{name:42s}{d.respondent_id.nunique():6d}{s1:15.4f}{s2:14.4f}{s3:14.4f}")
    print("-" * 91)
    print(f"{'MAXIMUM over the nine specifications':42s}{'':6s}"
          f"{worst[0]:15.4f}{worst[1]:14.4f}{worst[2]:14.4f}")
    print(f"\nApplied one at a time, no restriction or control moves an AMCE by more "
          f"than {singly[1]:.3f} in choice probability "
          f"({singly[2]:.3f} counting the 20-percentage-point error-rate gain).")
    print(f"Dropping all three quality flags at once moves an AMCE by at most "
          f"{worst[1]:.3f}.")


if __name__ == "__main__":
    main()
