# Figures and statistics for the AI-hiring conjoint paper — reproducible package

Regenerates all ten figures **directly from the raw data**
(`data/conjoints.csv`, `data/respondents.csv`) as **600-dpi PNG** and **vector
PDF**, from a single shared **black-and-white** theme, and reproduces the
principal estimates and conclusions of the manuscript (see the version-sensitivity
note below). Every plotted quantity is computed from the microdata; nothing is
hand-entered or simulated. **The output file names match the manuscript's figure and table numbers**, except `figureS1`–`figureS3`, which are supplementary displays of quantities the manuscript tabulates instead (Tables C3 and E1 and Appendix H) and have no numbered counterpart in the text. The full correspondence is given in the mapping table below (for example, manuscript Figure 1 is `figure1_amce`). Manuscript Table 2 is the live-instrument screenshot `figures/table2_screenshot.png`, which is captured from the survey environment rather than script-generated; `table2_task_mockup` is retained as the script-generated approximation of the same task layout.

```
AI_hiring_all_replication/
├── README.md
├── requirements.txt
├── analysis.py               ← computes every figure input from the raw CSVs
├── reproduce_statistics.py   ← reproduces every reported number NOT in a figure
├── figstyle.py               ← shared theme + palette + save helper
├── figure_data.py            ← table-sourced constants (fallback if CSVs absent)
├── make_figures.py           ← one function per figure; uses analysis.py by default
├── data/
│   ├── conjoints.csv          ← 30,704 profile-level rows
│   └── respondents.csv        ← 1,919 respondents
└── figures/                  ← output (PNG + PDF), named to match the manuscript: figure1…figure5, figureH1, table2, figureS1…figureS3, plus table2_screenshot.png (captured, not generated)
```

## How to regenerate

```bash
pip install -r requirements.txt
python analysis.py             # prints the figure inputs as a check
python reproduce_statistics.py # prints every other reported number vs the paper
python make_figures.py         # all figures -> ./figures/ (computed from data/)
python make_figures.py fig1 fig4   # only the named figures
```

`make_figures.py` calls `analysis.compute_all()` on the two CSVs. If the data
were removed, it falls back to the constants in `figure_data.py` (and marks
Figure H1 and `figureS3` as illustrative). With the data present, everything is exact.

## The estimation (reproduces the manuscript)

OLS linear probability model, **standard errors clustered by respondent**, the
error rate entered continuously (per +1 pp), decision authority as two dummies
against "AI decides alone", and each procedural feature as a 0/1 indicator.

**Codebook note (manuscript terminology).** The data columns keep their
original names; they map to the manuscript's terms as follows:
`decision_process_code` = decision authority, `accuracy_pct` = error rate
(share of qualified applicants wrongly rejected), `transparency` = explanation.
Manuscript Table 2 is a screenshot of the live instrument and shows the full
on-screen wording ("Decision process"; "Accuracy (qualified applicants wrongly
rejected)"; "Transparency"); the generated `table2_task_mockup` mirrors that
wording. Both match the note in Section 3.2 of the manuscript.

* **`analysis.py`** verifies the figure inputs — AMCEs (Table C1), marginal means
  (Table C3), error-rate moderations and equivalence (Table D1), complementarity
  interactions (Table E2), subgroup conditional AMCEs (Table E1), and the
  within-respondent preference moments of Appendix H (mean 0.29, observed
  SD 0.30, null SD 0.27, 76.6% positive) — all to
  the third decimal. It also computes a model-implied between-person SD (≈ 0.13);
  this quantity is not reported in the manuscript, whose Appendix H interprets
  only the observed-versus-null comparison and does not identify a model-free
  individual-level variance.
* **`reproduce_statistics.py`** verifies everything else: the sample
  characteristics (Table B1), the planned contrasts
  (Table C2), the individual-facing-vs-audit contrasts on both the AMCE and
  marginal-mean scales (Sec 4.1, H4), the 20 pp error reduction as a benchmark for
  human involvement and the CI for the difference between the two (Sec 4.1), the
  exploratory decision-authority sequence by error-rate interaction (Sec 4.2), the
  conditional AMCEs at the 10% error
  rate (Sec 4.2; registered H2(a), subsumed under H1a), the decision-authority nested F (= 838 or 432, ordering
  dependent; Sec 4.5), the logit-link interaction checks (Table E2), the attitude-item
  paired test and correlations (Sec 4.4; registered H5, reported descriptively), the secondary
  acceptability-rating AMCEs and rank correlation (Sec 4.5 / App F), the batch and
  left/right position checks, the convergent-validity correlations between the
  revealed human-preference and the stated attitudes (App H), and the
  **homogeneous-null SD 95% interval,
  [0.259, 0.276]** (fixed seed `20260707`, 10,000 replications).

**Version sensitivity.** Point estimates and 95% CIs reproduce exactly. The
*p-values of the non-significant interactions* (Table E2) depend on the
finite-sample cluster-robust correction and can move in the second decimal
across library versions; each remains non-significant, so no conclusion changes.
Pin the versions in `requirements.txt` (e.g. `pip freeze > locked.txt`) for
bitwise agreement.

## Data provenance — all figures EXACT (computed from `data/`)

| Manuscript reference | File | What it shows | Source computation |
|---|---|---|---|
| Table 2 | `table2_screenshot`           | the paired-profile task as respondents saw it | captured from the live instrument (not script-generated) |
| — (not in the manuscript) | `table2_task_mockup`          | script-generated approximation of the same task layout | fixed illustrative levels (UI mock-up) |
| Figure 1 | `figure1_amce`                 | AMCEs on P(choice) | main LPM; 95% CI |
| Figure 2 (Panel A) | `figure2_equivalence_contrast` | error-rate × feature/human moderation | interaction × 20 over 10–30%; 90% CI; TOST vs SESOI 0.05 |
| Figure 2 (Panel B) | `figure2_equivalence_contrast` | P(chosen) human-involved vs AI-alone by error | cell means of `chosen` |
| Figure 3 | `figure3_complementarity`      | feature AMCE with vs without a human | LPM within `human_involved` subsets; exact 95% CI |
| Figure 4 | `figure4_joint_distribution`   | legitimacy × intention joint distribution | crosstab of the two attitude items (sums to 1,919) |
| Figure 5 | `figure5_sesoi_sensitivity`    | SESOI sensitivity (±0.03/±0.05/±0.07) | same moderations vs nested thresholds |
| Figure H1 | `figureH1_observed_vs_null`    | observed vs homogeneous-preference null | parametric null from population rates + each respondent's task counts |
| Supp. fig. (Table C3) | `figureS1_marginal_means`      | marginal means (tabulated in Table C3) | cell means; cluster-robust 95% CI |
| Supp. fig. (Table E1) | `figureS2_subgroups`           | conditional AMCE of human involvement by subgroup (tabulated in Table E1) | LPM per subgroup; 95% CI |
| Supp. fig. (Appendix H) | `figureS3_preference_hist`     | within-respondent human-preference histogram | per-respondent P(chosen\|human) − P(chosen\|AI-alone) |

## Design of the figure set

*Figure numbers in this section and the notes below refer to the **manuscript** figure numbers.*

* **Black-and-white, one theme everywhere.** All figures are grayscale.
  Category distinctions rely on **marker shape** (filled circle = the focal /
  equivalent case; open square = the contrast baseline or the flagged
  exception) and **line style** (solid = focal series; dashed = baseline /
  reference lines), never on hue. Human involvement — the one estimate
  that behaves as an exception — is marked by an open square plus a short
  "not equivalent" tag (Figures 2A and 5), so the encoding is consistent and
  prints cleanly in black and white.
* **Typography matches the manuscript** (Liberation Serif ≡ Times metrics; STIX
  maths).
* **True print resolution** — 600-dpi PNG + editable vector PDF (fonts embedded,
  `pdf.fonttype = 42`).
* **Figure 1** groups the attributes and sets the continuous error-rate effect
  apart (open marker) with a full-range annotation (≈ −0.285 across
  10→30%), defusing the unit-mixing hazard of the original.
* **Figure 2** styles human involvement as the open-square "not
  equivalent" exception; Panel B shows the exact contrasts and a floor note.
* **Figure 3** joins each pair with a shift line, orders by the size of the shift
  so the flat opt-out ends the sequence, and labels Δ and "≈0 (unchanged)".
* **Figure 4** adds marginal histograms, a diagonal reference line, and an
  outlined doubt-but-engage box (150; 7.8%).

## Notes

* The homogeneous-preference null (Fig H1) uses a fixed seed (`20260707`) for a
  stable curve; the observed histogram is deterministic.
* `figure_data.py` is retained only as an offline fallback; when `data/` is
  present it is not used for any plotted value except the static Table 2 mock-up levels.

## Revision note (2026-07-27)

The plotted row label for the pooled human-involvement estimate reads **"Human involvement"**
(previously "Human decision-maker"), and the Appendix H legend reads **"Homogeneous-preference
benchmark"** (previously "null"), so that the figures use the manuscript's terms. `analysis.py`,
`figure_data.py`, and `make_figures.py` were updated and `figure2`, `figure5`, and `figureH1`
regenerated; no plotted value changed. The Figure 2 embedded in the previous manuscript draft
predated the current script (panel A title), and the manuscript now carries the regenerated file.

## Revision note (2026-07-27, second pass)

`reproduce_statistics.py` now also reproduces the two quantities added to the
manuscript in this revision: the benchmark comparison in Section 4.1 (a 20 pp error
reduction, +0.285, against pooled human involvement, +0.272, difference +0.013,
95% CI [-0.007, 0.033]) and the exploratory decision-authority sequence by
error-rate interaction in Section 4.2 ("AI suggests" minus "AI screens first" of
+0.027, +0.030 and +0.032 at the three error rates; change over the range +0.005,
95% CI [-0.026, 0.036], p = .77; proportional benchmark about +0.055; own
moderations against AI-alone of -0.044 and -0.048). Both reproduce the manuscript
to the third decimal. The `human x error rate, 10-20% subset` line is relabelled as
an internal diagnostic, since the manuscript now makes that point with the Panel B
marginal means (0.285, 0.289 and 0.239) instead. No data, estimator, figure or
manuscript number changed.
