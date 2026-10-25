"""Shared matplotlib style for IEEE column-width figures (Times New Roman, 8 pt labels)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL_W_IN = 3.5   # 252 pt column
def apply():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8, "legend.fontsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "lines.linewidth": 1.0, "lines.markersize": 3.5,
        "axes.linewidth": 0.6, "grid.linewidth": 0.4, "figure.dpi": 300, "savefig.dpi": 300,
        "axes.grid": True, "grid.alpha": 0.3, "legend.frameon": False,
        "axes.spines.top": False, "axes.spines.right": False,
    })
