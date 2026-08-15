#!/usr/bin/env python3
"""
make_figures.py
---------------
Regenerates every figure in the AI-hiring conjoint paper as a 600-dpi PNG and a
vector PDF, using a single shared theme (figstyle) and a provenance-tagged data
module (figure_data).

Usage
-----
    python make_figures.py            # build all figures into ./figures/
    python make_figures.py fig1 fig4  # build only the named figures

Figure keys (manuscript-aligned): fig1 fig2 fig3 fig4 fig5 (main),
figH1 (appendix), table2 (Table 2 mock-up), figS1 figS2 figS3 (supplementary)
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib import colors as mcolors
from pathlib import Path

import figstyle as S
import figure_data as FD

# Prefer values computed directly from the raw data (data/conjoints.csv +
# data/respondents.csv); fall back to the table-sourced constants otherwise.
try:
    import analysis
    D = analysis.compute_all("data/conjoints.csv", "data/respondents.csv")
    DATA_SOURCE = "computed from raw data"
except Exception as _e:            # noqa: BLE001 (any failure -> safe fallback)
    D = FD
    DATA_SOURCE = f"table-sourced constants ({type(_e).__name__})"
    for _attr in ("PREF_OBSERVED", "PREF_NULL", "TASK_ROWS"):
        if not hasattr(D, _attr):
            setattr(D, _attr, getattr(FD, _attr, None))

S.set_theme()
CAPHEIGHT = 3        # error-bar cap size
MS = 6.5             # marker size


# --------------------------------------------------------------------------- #
# Figure 1 -- grouped AMCE forest plot                                         #
# --------------------------------------------------------------------------- #
def fig1_amce():
    groups = [("process",   "Decision authority"),
              ("procedural", "Procedural features"),
              ("accuracy",   "Error rate")]
    y, ylab, rows = [], [], []
    cur = 0.0
    for gi, (gkey, _) in enumerate(groups):
        items = [r for r in D.AMCE if r[4] == gkey]
        for r in items:
            rows.append((cur, r)); cur -= 1.0
        cur -= 0.7  # inter-group gap
    ys = [t[0] for t in rows]
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.axvline(0, color=S.INK, lw=1.1, ls=(0, (4, 3)), zorder=1)
    # comparison line: the value of a 20 pp reduction in the error rate
    g20 = D.ACCURACY_20PP_GAIN
    ax.axvline(g20, color=S.GRAY, lw=1.2, ls=(0, (5, 3)), zorder=1)
    for yy, (lab, est, lo, hi, gkey) in rows:
        mfc = "white" if gkey == "accuracy" else S.INK
        ax.plot([lo, hi], [yy, yy], color=S.GRAY, lw=1.6, zorder=2,
                solid_capstyle="round")
        ax.plot(est, yy, "o", ms=MS, mfc=mfc, mec=S.INK, zorder=3)
        ax.annotate(f"{est:+.3f}", (hi, yy), xytext=(6, 0),
                    textcoords="offset points", va="center", ha="left",
                    fontsize=10, color=S.INK)
        ax.text(-0.052, yy, lab, va="center", ha="right", fontsize=11)
    # label the comparison line above the plot
    ax.annotate(f"20 pp error reduction ({g20:+.3f})", (g20, 1.02),
                ha="center", va="bottom", fontsize=10, color=S.GRAY)
    # group headers, placed in the gap just above each multi-row group
    for gkey, glabel in groups:
        gy = [yy for yy, r in rows if r[4] == gkey]
        if len(gy) < 2:
            continue
        ax.text(-0.052, max(gy) + 0.72, glabel, va="center", ha="right",
                fontsize=10, color=S.GRAY, style="italic")
    ax.set_xlim(-0.02, 0.36)
    ax.set_ylim(min(ys) - 0.9, 1.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Average marginal component effect on P(choice)")
    ax.set_xticks(np.arange(0.0, 0.351, 0.05))
    S.save(fig, "figure1_amce")


# --------------------------------------------------------------------------- #
# Figure 2 -- (A) equivalence forest  +  (B) human contrast by error rate      #
# --------------------------------------------------------------------------- #
def fig2_equivalence_contrast():
    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(7.4, 3.5), gridspec_kw={"width_ratios": [1.35, 1]})

    # ---- Panel A: error-rate x feature moderation, 90% CI, +/-SESOI band ----
    rows = list(reversed(D.MODERATION))          # human at bottom
    ys = np.arange(len(rows))
    axA.axvspan(-D.SESOI, D.SESOI, color=S.BAND, zorder=0)
    for x in (-D.SESOI, D.SESOI):
        axA.axvline(x, color=S.GRAY, lw=0.8, ls=":", zorder=1)
    axA.axvline(0, color=S.INK, lw=0.8, zorder=1)
    for yy, (lab, est, lo, hi, equiv) in zip(ys, rows):
        col = S.INK if equiv else S.ACCENT
        marker = "o" if equiv else "s"
        mfc = col if equiv else "white"
        axA.plot([lo, hi], [yy, yy], color=col, lw=1.7, solid_capstyle="round", zorder=2)
        axA.plot(est, yy, marker, ms=MS, mfc=mfc, mec=col, color=col, zorder=3)
        axA.text(-0.088, yy, lab, va="center", ha="right", fontsize=11,
                 color=col if not equiv else S.INK)
    axA.set_xlim(-0.085, 0.085)
    axA.set_ylim(-0.6, len(rows) - 0.4)
    axA.set_yticks([])
    axA.spines["left"].set_visible(False)
    axA.set_xlabel("Change in AMCE over 10$-$30% error  (90% CI)")
    axA.set_title("(A)  Error-rate $\\times$ feature moderation", fontsize=12.5)

    # ---- Panel B: P(chosen) human-involved vs AI-alone by error rate --------
    x = D.ERR_RATES
    axB.fill_between(x, D.P_AIALONE, D.P_HUMAN, color=S.BAND, zorder=0)
    axB.plot(x, D.P_HUMAN, "-o", color=S.BLUE, mfc=S.BLUE, mec=S.BLUE,
             lw=1.9, ms=MS, zorder=3, label="Human involved")
    axB.plot(x, D.P_AIALONE, "--s", color=S.INK, mfc="white", mec=S.INK,
             lw=1.7, ms=MS, zorder=3, label="AI decides alone")
    for xi, ph, pa, d in zip(x, D.P_HUMAN, D.P_AIALONE, D.HUMAN_CONTRAST):
        axB.annotate(f"+{d:.3f}", (xi, (ph + pa) / 2), xytext=(4, 0),
                     textcoords="offset points", ha="left", va="center",
                     fontsize=10, color=S.GRAY)
    axB.set_xticks(x)
    axB.set_ylim(0, 0.82)
    axB.set_xlim(8, 32)
    axB.set_xlabel("Error rate (%)")
    axB.set_ylabel("P(chosen)")
    axB.set_title("(B)  Human contrast by error rate", fontsize=12.5)
    axB.legend(frameon=False, loc="upper right", handlelength=1.8)
    fig.subplots_adjust(wspace=0.28)
    S.save(fig, "figure2_equivalence_contrast")


# --------------------------------------------------------------------------- #
# Figure 3 -- feature value with vs without a human (complementarity)          #
# --------------------------------------------------------------------------- #
def fig3_complementarity():
    fig, ax = plt.subplots(figsize=(6.6, 3.7))
    xs = np.arange(len(D.COMPLEMENTARITY))
    ax.axhline(0, color=S.GRAY, lw=0.9, ls=(0, (4, 3)), zorder=1)
    for xi, (lab, aE, aLo, aHi, hE, hLo, hHi, delta) in zip(xs, D.COMPLEMENTARITY):
        # connecting shift line
        ax.plot([xi, xi], [aE, hE], color=S.GRAY, lw=1.1, ls="-", zorder=1)
        # AI-alone (open square, ink) and human (filled circle, blue)
        ax.errorbar(xi - 0.10, aE, yerr=[[aE - aLo], [aHi - aE]], fmt="s",
                    ms=MS, mfc="white", mec=S.INK, color=S.INK,
                    capsize=CAPHEIGHT, lw=1.4, zorder=3)
        ax.errorbar(xi + 0.10, hE, yerr=[[hE - hLo], [hHi - hE]], fmt="o",
                    ms=MS, mfc=S.BLUE, mec=S.BLUE, color=S.BLUE,
                    capsize=CAPHEIGHT, lw=1.4, zorder=3)
        # delta annotation
        top = max(hHi, aHi)
        ax.annotate(f"$\\Delta$={delta:+.3f}", (xi, top), xytext=(0, 8),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=10, color=S.INK)
    ax.set_xticks(xs)
    ax.set_xticklabels([r[0] for r in D.COMPLEMENTARITY])
    ax.set_ylim(0, 0.205)
    ax.set_xlim(-0.6, len(xs) - 0.4)
    ax.set_ylabel("Feature AMCE on P(choice)")
    handles = [Line2D([0], [0], marker="s", ls="none", mfc="white", mec=S.INK,
                      color=S.INK, ms=MS, label="AI decides alone"),
               Line2D([0], [0], marker="o", ls="none", mfc=S.BLUE, mec=S.BLUE,
                      color=S.BLUE, ms=MS, label="Human involved")]
    ax.legend(handles=handles, frameon=False, loc="upper right", ncol=1,
              handlelength=1.2)
    S.save(fig, "figure3_complementarity")


# --------------------------------------------------------------------------- #
# Figure 4 -- joint distribution heatmap with marginals + doubt-but-engage box #
# --------------------------------------------------------------------------- #
def fig4_joint_distribution():
    counts = np.array(D.JOINT_COUNTS)            # rows=legitimacy, cols=intention
    N = counts.sum()
    col_marg = counts.sum(axis=0)                # intention marginal
    row_marg = counts.sum(axis=1)                # legitimacy marginal

    fig = plt.figure(figsize=(6.2, 5.6))
    gs = fig.add_gridspec(2, 4, width_ratios=[6, 1.1, 0.55, 0.30],
                          height_ratios=[1.1, 6], wspace=0.06, hspace=0.06)
    axH = fig.add_subplot(gs[1, 0])
    axT = fig.add_subplot(gs[0, 0], sharex=axH)
    axR = fig.add_subplot(gs[1, 1], sharey=axH)
    axC = fig.add_subplot(gs[1, 3])

    cmap = plt.get_cmap(S.SEQ)
    norm = mcolors.Normalize(vmin=0, vmax=counts.max())
    im = axH.imshow(counts, cmap=cmap, norm=norm, origin="lower",
                    extent=[0.5, 5.5, 0.5, 5.5], aspect="auto")
    # cell counts, contrast-aware
    for i in range(5):
        for j in range(5):
            v = counts[i, j]
            tc = "white" if norm(v) > 0.55 else S.INK
            axH.text(j + 1, i + 1, f"{v}", ha="center", va="center",
                     fontsize=10, color=tc)
    axH.plot([0.5, 5.5], [0.5, 5.5], color=S.GRAY, lw=1.0, ls=(0, (4, 3)), zorder=4)
    # doubt-but-engage quadrant: legitimacy<=2 & intention>=4
    box = Rectangle((3.5, 0.5), 2.0, 2.0, fill=False, edgecolor=S.ACCENT,
                    lw=1.8, zorder=5)
    axH.add_patch(box)
    dbe = counts[:2, 3:].sum()
    axH.annotate(f"n = {dbe}", (5.45, 0.60), ha="right", va="bottom",
                 fontsize=10, color=S.INK, zorder=6)
    axH.set_xticks(range(1, 6)); axH.set_yticks(range(1, 6))
    axH.set_xlabel("Intention to apply")
    axH.set_ylabel("Belief in legitimacy of AI hiring")

    # marginals
    axT.bar(range(1, 6), col_marg, color=S.BAR, edgecolor=S.INK, lw=0.5, width=0.9)
    axR.barh(range(1, 6), row_marg, color=S.BAR, edgecolor=S.INK, lw=0.5, height=0.9)
    for a in (axT, axR):
        a.axis("off")
    for j, v in enumerate(col_marg, start=1):
        axT.text(j, v, f"{v}", ha="center", va="bottom", fontsize=10, color=S.INK)
    for i, v in enumerate(row_marg, start=1):
        axR.text(v, i, f" {v}", ha="left", va="center", fontsize=10, color=S.INK)

    cb = fig.colorbar(im, cax=axC)
    cb.set_label("respondents", fontsize=11)
    cb.outline.set_edgecolor(S.INK); cb.outline.set_linewidth(0.8)
    S.save(fig, "figure4_joint_distribution")


# --------------------------------------------------------------------------- #
# Table 2  -- example paired-profile task (clean vector mock-up)              #
# --------------------------------------------------------------------------- #
def table2_task_mockup():
    rows = D.TASK_ROWS
    nrow = len(rows)
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.set_xlim(0, 3); ax.set_ylim(0, nrow + 1.7)
    ax.axis("off")
    col_x = [0.0, 1.15, 2.075]           # left edges of the three columns
    col_w = [1.15, 0.925, 0.925]
    top = nrow + 0.9
    # header (light-gray fill with dark text, matching Table 1)
    for cx, cw, txt in zip(col_x, col_w, ["Feature", "System A", "System B"]):
        ax.add_patch(Rectangle((cx, top), cw, 0.8, facecolor="#E8E8E8", edgecolor=S.GRID))
        ax.text(cx + 0.06, top + 0.4, txt, va="center", ha="left",
                color=S.INK, fontsize=11, fontweight="bold")
    # rows
    for r, (feat, a, b) in enumerate(rows):
        yy = top - (r + 1) * 0.8
        shade = S.BANDED if r % 2 == 0 else "white"
        ax.add_patch(Rectangle((col_x[0], yy), col_w[0], 0.8, facecolor=shade,
                               edgecolor=S.GRID))
        for cx, cw in zip(col_x[1:], col_w[1:]):
            ax.add_patch(Rectangle((cx, yy), cw, 0.8, facecolor="white",
                                   edgecolor=S.GRID))
        ax.text(col_x[0] + 0.06, yy + 0.4, feat, va="center", ha="left",
                fontsize=10, fontweight="bold", linespacing=1.0)
        ax.text(col_x[1] + 0.06, yy + 0.4, a, va="center", ha="left", fontsize=10)
        ax.text(col_x[2] + 0.06, yy + 0.4, b, va="center", ha="left", fontsize=10)
    # prompts
    ax.text(1.5, 0.55, "Which hiring system would you prefer to be evaluated by?"
            "    [ System A ]    [ System B ]", ha="center", va="center",
            fontsize=11, style="italic")
    ax.text(1.5, 0.12, "How acceptable is each system?  (1 = not at all \u2026 5 = completely)",
            ha="center", va="center", fontsize=10, color=S.GRAY)
    S.save(fig, "table2_task_mockup")


# --------------------------------------------------------------------------- #
# Supp. Fig. S1 -- marginal means, grouped, with 0.5 indifference line (Table C3)             #
# --------------------------------------------------------------------------- #
def figS1_marginal_means():
    order = ["Decision authority", "Error rate", "Explanation", "Opt-out",
             "Appeal", "Bias audit"]
    rows, y, ypos = [], 0.0, []
    for g in order:
        for r in [r for r in D.MARGINAL_MEANS if r[4] == g]:
            rows.append((y, r)); ypos.append(y); y -= 1.0
        y -= 0.9
    xL = 0.30
    fig, ax = plt.subplots(figsize=(7.0, 6.9))
    ax.axvline(0.5, color=S.INK, lw=1.1, ls=(0, (4, 3)), zorder=1)
    for gi, g in enumerate(order):
        gy = [yy for yy, r in rows if r[4] == g]
        if gi % 2 == 0:
            ax.axhspan(min(gy) - 0.5, max(gy) + 0.5, color=S.BANDED, zorder=0)
        ax.text(xL - 0.006, max(gy) + 0.55, g, va="center", ha="right",
                fontsize=10, color=S.GRAY, style="italic")   # header in the gap
    for yy, (lab, mm, lo, hi, g) in rows:
        ax.plot([lo, hi], [yy, yy], color=S.GRAY, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(mm, yy, "o", ms=5.8, mfc=S.INK, mec=S.INK, zorder=3)
        ax.text(xL - 0.006, yy, lab, va="center", ha="right", fontsize=11)  # left margin
    ax.set_xlim(xL, 0.66)
    ax.set_ylim(min(ypos) - 0.8, rows[0][0] + 1.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Marginal mean: P(system chosen)")
    S.save(fig, "figureS1_marginal_means")


# --------------------------------------------------------------------------- #
# Figure 5 -- SESOI sensitivity with nested threshold bands                   #
# --------------------------------------------------------------------------- #
def fig5_sesoi_sensitivity():
    rows = list(reversed(D.SENSITIVITY))         # human at bottom
    ys = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    t03, t05, t07 = D.SESOI_THRESHOLDS
    ax.axvspan(-t05, t05, color=S.BAND, zorder=0)
    ax.axvline(0, color=S.INK, lw=0.8, zorder=1)
    style = {t03: (":", "$\\pm$0.03"), t05: ("-", "$\\pm$0.05 (pre-registered)"),
             t07: ((0, (5, 3)), "$\\pm$0.07")}
    for t, (ls, _) in style.items():
        for x in (-t, t):
            ax.axvline(x, color=S.GRAY, lw=0.9, ls=ls, zorder=1)
    for yy, (lab, est, lo, hi, passed, equiv) in zip(ys, rows):
        marker = "o" if equiv else "s"
        mfc = S.INK if equiv else "white"
        ax.plot([lo, hi], [yy, yy], color=S.INK, lw=1.7, solid_capstyle="round", zorder=2)
        ax.plot(est, yy, marker, ms=MS, mfc=mfc, mec=S.INK, zorder=3)
        ax.text(-0.088, yy, lab, va="center", ha="right", fontsize=11, color=S.INK)
    # threshold legend along the top
    xs_leg = [(-t05 - t03) / 2, 0.0, (t05 + t07) / 2]
    labels = ["dotted = $\\pm$0.03", "solid = $\\pm$0.05 (pre-registered)", "dashed = $\\pm$0.07"]
    for xx, ll in zip([-0.06, 0.0, 0.06], labels):
        ax.text(xx, len(rows) - 0.35, ll, ha="center", va="bottom",
                fontsize=10, color=S.GRAY)
    ax.set_xlim(-0.085, 0.085)
    ax.set_ylim(-0.6, len(rows) + 0.1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Change in value across the 10$-$30% error range  (90% CI)")
    S.save(fig, "figure5_sesoi_sensitivity")


# --------------------------------------------------------------------------- #
# Supp. Fig. S2 -- conditional AMCE of human involvement by subgroup (Table E1)               #
# --------------------------------------------------------------------------- #
def figS2_subgroups():
    rows = D.SUBGROUPS
    # top-to-bottom, with a gap after the pooled row and between moderators
    ys, cur = [], 0.0
    lay = []
    prev_group = None
    for r in rows:
        if prev_group is not None and r[4] != prev_group:
            cur -= 0.6
        lay.append((cur, r)); cur -= 1.0; prev_group = r[4]
    fig, ax = plt.subplots(figsize=(6.7, 3.5))
    ax.axvline(D.POOLED_HUMAN_AMCE, color=S.ACCENT, lw=1.1, ls=(0, (4, 3)),
               zorder=1)
    for yy, (lab, est, lo, hi, g) in lay:
        ax.plot([lo, hi], [yy, yy], color=S.GRAY, lw=1.7, solid_capstyle="round", zorder=2)
        ax.plot(est, yy, "o", ms=MS, mfc=S.INK, mec=S.INK, zorder=3)
        ax.text(0.198, yy, lab, va="center", ha="right", fontsize=11)
    ax.set_xlim(0.20, 0.33)
    ax.set_ylim(lay[-1][0] - 0.8, lay[0][0] + 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Conditional AMCE of human involvement on P(chosen)")
    S.save(fig, "figureS2_subgroups")


# --------------------------------------------------------------------------- #
# Within-respondent human-preference statistic (Figure H1, Supp. Fig. S3)      #
# --------------------------------------------------------------------------- #
def _load_or_simulate_preference():
    """Return (observed, null, exact) arrays of the within-respondent statistic.

    If real per-respondent values were computed from the raw data (analysis.py),
    they are used directly and the figure is EXACT. Otherwise both arrays are
    SIMULATED to match the reported moments and are for display only.
    """
    obs = getattr(D, "PREF_OBSERVED", None)
    null = getattr(D, "PREF_NULL", None)
    if obs is not None and null is not None and len(obs):
        return np.asarray(obs), np.asarray(null), True

    # -- fallback simulation (only if raw data are absent) -------------------
    rng = np.random.default_rng(20260707)
    nH = rng.integers(4, 9, FD.N_RESP); nA = rng.integers(2, 7, FD.N_RESP)
    kH = rng.binomial(nH, 0.59); kA = rng.binomial(nA, 0.32)
    null = kH / nH - kA / nA
    null = (null - null.mean()) / null.std() * FD.PREF_SD_NULL + FD.PREF_MEAN
    null = np.clip(null, -1, 1)
    person = rng.normal(0, 1, FD.N_RESP)
    pH = np.clip(0.59 + 0.11 * person, 0.02, 0.98)
    pA = np.clip(0.32 - 0.11 * person, 0.02, 0.98)
    kH = rng.binomial(nH, pH); kA = rng.binomial(nA, pA)
    obs = rng.binomial(nH, pH) / nH - rng.binomial(nA, pA) / nA
    obs = (obs - obs.mean()) / obs.std() * FD.PREF_SD_OBSERVED + FD.PREF_MEAN
    return np.clip(obs, -1, 1), null, False


def figS3_preference_hist():
    obs, _, exact = _load_or_simulate_preference()
    fig, ax = plt.subplots(figsize=(6.8, 3.7))
    bins = np.linspace(-1, 1, 25)
    ax.hist(obs, bins=bins, color=S.BAR, edgecolor=S.INK, lw=0.6)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.20)                      # headroom for the labels
    ax.axvline(0, color=S.INK, lw=1.0, ls=(0, (4, 3)))
    ax.axvline(D.PREF_MEAN, color=S.INK, lw=1.6)
    ax.annotate(f"{D.PREF_SHARE_POS*100:.0f}% prefer a human (gap > 0)",
                (-0.98, ymax * 1.10), fontsize=10, ha="left", va="center", color=S.INK)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Individual preference for a human decision-maker\n"
                  "(within-respondent choice rate: human-involved $-$ AI-alone)")
    ax.set_ylabel("Number of respondents")
    if not exact:
        ax.text(0.02, 0.98, "illustrative reconstruction from reported moments",
                transform=ax.transAxes, fontsize=10, color=S.GRAY,
                va="top", ha="left", style="italic")
    S.save(fig, "figureS3_preference_hist")


def figH1_observed_vs_null():
    obs, null, exact = _load_or_simulate_preference()
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    bins = np.linspace(-1, 1, 25)
    ax.hist(obs, bins=bins, density=True, color=S.BAR,
            edgecolor=S.INK, lw=0.5, label="Observed (individual human preference)")
    from scipy.stats import gaussian_kde
    xx = np.linspace(-1, 1, 400)
    kde = gaussian_kde(null, bw_method=0.28)
    ax.plot(xx, kde(xx), color=S.ACCENT, lw=2.0, label="Homogeneous-preference benchmark")
    ax.axvline(0, color=S.GRAY, lw=0.9, ls=(0, (4, 3)))
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.22)                      # headroom for legend + note
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Within-respondent  P(choose human) $-$ P(choose AI-alone)")
    ax.set_ylabel("density")
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    if not exact:
        ax.text(0.02, 0.66, "illustrative reconstruction from reported moments",
                transform=ax.transAxes, fontsize=10, color=S.GRAY,
                va="top", ha="left", style="italic")
    S.save(fig, "figureH1_observed_vs_null")


# --------------------------------------------------------------------------- #
FIGS = {"table2": table2_task_mockup,       # manuscript Table 2
        "fig1":   fig1_amce,                 # manuscript Figure 1
        "fig2":   fig2_equivalence_contrast, # manuscript Figure 2
        "fig3":   fig3_complementarity,      # manuscript Figure 3
        "fig4":   fig4_joint_distribution,   # manuscript Figure 4
        "fig5":   fig5_sesoi_sensitivity,    # manuscript Figure 5
        "figH1":  figH1_observed_vs_null,    # manuscript Figure H1 (appendix)
        "figS1":  figS1_marginal_means,      # supplementary (tabulated as Table C3)
        "figS2":  figS2_subgroups,           # supplementary (tabulated as Table E1)
        "figS3":  figS3_preference_hist}     # supplementary (Appendix H)


def main(argv):
    keys = argv[1:] if len(argv) > 1 else list(FIGS)
    print("Building:", ", ".join(keys))
    for k in keys:
        if k not in FIGS:
            print(f"  ! unknown figure key: {k}"); continue
        FIGS[k]()
    print("Done -> ./figures/")


if __name__ == "__main__":
    main(sys.argv)
