"""
figstyle.py
-----------
A single, shared visual theme for every figure in the AI-hiring conjoint paper.

Rationale for the design choices (see README for the full critique):

* Typography. Liberation Serif is metric-compatible with Times New Roman, so
  the figures match the manuscript body text. Math is rendered with the STIX
  set for the same reason. One theme => cross-figure consistency, which the
  original set lacked (some panels were black, others navy, others crimson).

* Colour. The palette is grayscale. Category distinctions rely on marker
  shape (filled circle = focal / equivalent; open square = baseline or flagged
  exception) and line style (solid vs dashed), never on hue; human involvement
  — the one estimate that behaves as an exception — is marked
  by an open square plus a short text tag. ACCENT and BLUE are retained as
  aliases of INK for API stability.

* Output. Every figure is written at 600 dpi PNG (screen / Word) *and* as a
  vector PDF (print / LaTeX). Nothing is rasterised at a low resolution.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------------------------------- #
# Palette -- BLACK & WHITE.  Category distinctions rely on marker SHAPE         #
# (filled circle vs open square) and LINE STYLE (solid vs dashed), not hue, so  #
# the figures are fully grayscale. The "exception" (human involvement) is       #
# marked by an open square + a short text tag, not by colour.                   #
# --------------------------------------------------------------------------- #
INK    = "#1A1A1A"   # primary estimates, reference lines, text (near-black)
ACCENT = "#1A1A1A"   # (kept as an alias; no longer a distinct colour)
BLUE   = "#1A1A1A"   # secondary series (distinguished by shape / line style)
GRAY   = "#8A8A8A"   # confidence-interval whiskers, grid, secondary text
BAR    = "#B8B8B8"   # fill for histogram / marginal bars (with a dark edge)
GRID   = "#DBDBDB"   # faint grid / separators
BAND   = "#EAEAEA"   # shaded equivalence region
BANDED = "#F0F0F0"   # alternating group background
SEQ    = "Greys"     # sequential colormap for the joint-distribution heatmap

def set_theme():
    """Apply the shared rcParams theme. Call once before plotting."""
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 11,
        "axes.titlesize": 12.5,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 10,
        "axes.edgecolor": INK,
        "axes.linewidth": 0.9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.9,
        "ytick.major.width": 0.9,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "axes.labelcolor": INK,
        "figure.dpi": 120,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.03,
        "pdf.fonttype": 42,   # embed real fonts (editable text) rather than curves
        "ps.fonttype": 42,
    })

def save(fig, name, outdir="figures"):
    """Save a figure as 600-dpi PNG *and* vector PDF into `outdir`."""
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}")
    plt.close(fig)
    print(f"  saved {name}.png / .pdf")
