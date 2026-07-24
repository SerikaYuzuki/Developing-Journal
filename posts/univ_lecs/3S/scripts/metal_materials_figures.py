"""金属材料学の学習用模式図をSVGで生成する。

添付された低解像度の試験図を読みやすく描き直すことが目的であり、
状態図・CCT図・時効曲線の座標は定量データではない。
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/codex-mpl-metal-materials")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle
from scipy.interpolate import PchipInterpolator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "金属材料学"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#17324d"
BLUE = "#457b9d"
TEAL = "#2a9d8f"
GOLD = "#e9c46a"
ORANGE = "#f4a261"
RED = "#e76f51"
PURPLE = "#6c5ce7"
LIGHT = "#f7f4ed"
GRID = "#cbd5df"
GRAY = "#64748b"

plt.rcParams.update(
    {
        "font.family": "Hiragino Sans",
        "font.size": 10,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "axes.titlecolor": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "text.color": NAVY,
        "svg.fonttype": "none",
    }
)


def finish(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def phase_diagrams() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.2))
    fig.suptitle("Cu binary systems — schematic phase-diagram reading", fontsize=15, weight="bold")

    # Cu–Ni: complete solid solution.
    ax = axes[0, 0]
    x = np.linspace(0, 1, 300)
    base = 1358 + (1728 - 1358) * x
    lens = 155 * np.sin(np.pi * x)
    ax.plot(x, base + 0.55 * lens, color=RED, lw=2.5)
    ax.plot(x, base - 0.45 * lens, color=BLUE, lw=2.5)
    ax.fill_between(x, base - 0.45 * lens, base + 0.55 * lens, color=GOLD, alpha=0.35)
    ax.text(0.5, 1650, "L", ha="center", weight="bold")
    ax.text(0.5, 1445, "L + α", ha="center")
    ax.text(0.5, 1190, "α (fcc solid solution)", ha="center", weight="bold")
    ax.set_ylim(1050, 1830)
    ax.set_title("(a) Cu–Ni: complete solid solution")
    ax.set_xticks([0, 1], ["Cu", "Ni"])
    ax.set_ylabel("Temperature / K")

    # Cu–Fe: Cu-rich solvus only; falling solubility on cooling.
    ax = axes[0, 1]
    x = np.linspace(0, 10, 300)
    solvus = 430 + 1010 * np.sqrt(np.clip(x / 6.0, 0, 1))
    solvus[x > 6] = np.nan
    ax.plot(x, solvus, color=RED, lw=2.8)
    ax.fill_between(x, 350, solvus, where=~np.isnan(solvus), color=BLUE, alpha=0.12)
    ax.text(1.2, 1180, "α-Cu\n(Fe in solution)", ha="center")
    ax.text(5.8, 610, "α-Cu + Fe-rich phase", ha="center", weight="bold")
    ax.annotate(
        "solubility decreases\non cooling",
        xy=(1.5, 925),
        xytext=(5.2, 1200),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        ha="center",
    )
    ax.set_ylim(350, 1500)
    ax.set_title("(b) Cu-rich Cu–Fe: precipitation")
    ax.set_xticks([0, 10], ["Cu", "Fe →"])
    ax.set_ylabel("Temperature / K")
    ax.text(0.98, 0.04, "Cu-rich corner; not to scale", transform=ax.transAxes, ha="right", color=GRAY)

    # Cu–As: finite solid solubility and intermetallic at higher content.
    ax = axes[1, 0]
    x = np.linspace(0, 15, 300)
    solvus = 420 + 520 * np.sqrt(np.clip(x / 7.0, 0, 1))
    solvus[x > 7] = np.nan
    ax.plot(x, solvus, color=TEAL, lw=2.8)
    ax.axvspan(11.5, 13.2, color=PURPLE, alpha=0.22)
    ax.text(2.1, 1020, "α-Cu\n(As in solution)", ha="center")
    ax.text(7.0, 520, "α-Cu + As-rich phase", ha="center")
    ax.text(12.35, 980, "Cu₃As-\nrelated", ha="center", weight="bold")
    ax.set_ylim(350, 1350)
    ax.set_title("(c) Cu-rich Cu–As: appreciable solubility")
    ax.set_xticks([0, 15], ["Cu", "As →"])
    ax.set_xlabel("Solute content")
    ax.set_ylabel("Temperature / K")
    ax.text(0.98, 0.04, "topology only; not to scale", transform=ax.transAxes, ha="right", color=GRAY)

    # Cu–Bi: negligible solid solubility and low-temperature eutectic.
    ax = axes[1, 1]
    x = np.linspace(0, 2.0, 300)
    liquidus = 1358 - 340 * np.sqrt(x / 2)
    ax.plot(x, liquidus, color=RED, lw=2.6)
    ax.axhline(544, color=BLUE, lw=2.2)
    ax.axvspan(0, 0.055, color=TEAL, alpha=0.18)
    ax.text(0.65, 1210, "L", ha="center")
    ax.text(1.1, 830, "α-Cu + L", ha="center")
    ax.text(1.0, 450, "α-Cu + Bi", ha="center", weight="bold")
    ax.annotate(
        "near-zero bulk\nsolubility",
        xy=(0.04, 700),
        xytext=(0.58, 990),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        ha="center",
    )
    ax.set_ylim(350, 1450)
    ax.set_title("(d) Cu-rich Cu–Bi: phase separation")
    ax.set_xticks([0, 2], ["Cu", "Bi →"])
    ax.set_xlabel("Solute content")
    ax.set_ylabel("Temperature / K")
    ax.text(0.98, 0.04, "Cu-rich corner; not to scale", transform=ax.transAxes, ha="right", color=GRAY)

    for ax in axes.flat:
        ax.grid(alpha=0.25, color=GRID)
        ax.spines[["top", "right"]].set_visible(False)
    fig.text(
        0.5,
        0.01,
        "Purpose: compare phase constitution near dilute Cu. Horizontal scales differ; no quantitative reading.",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    finish(fig, "cu-binary-schematic.svg")


def _grain_network(ax: plt.Axes) -> None:
    polygons = [
        [(0, 0), (0.43, 0), (0.48, 0.43), (0.25, 0.62), (0, 0.50)],
        [(0.43, 0), (1, 0), (1, 0.43), (0.73, 0.57), (0.48, 0.43)],
        [(0, 0.50), (0.25, 0.62), (0.42, 1), (0, 1)],
        [(0.25, 0.62), (0.48, 0.43), (0.73, 0.57), (0.78, 1), (0.42, 1)],
        [(0.73, 0.57), (1, 0.43), (1, 1), (0.78, 1)],
    ]
    for p in polygons:
        ax.add_patch(Polygon(p, closed=True, facecolor=LIGHT, edgecolor=NAVY, lw=1.5))
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")


def cu_microstructures() -> None:
    rng = np.random.default_rng(241)
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.7))
    titles = [
        "Cu–Ni\nsolid solution",
        "Cu–Fe\nFe-rich clusters",
        "Cu–As\nbulk solute",
        "Cu–Bi\nGB segregation",
    ]
    for ax, title in zip(axes, titles, strict=True):
        _grain_network(ax)
        ax.set_title(title, fontsize=11, weight="bold")

    # Random isolated Ni.
    pts = rng.uniform(0.06, 0.94, size=(35, 2))
    axes[0].scatter(pts[:, 0], pts[:, 1], s=18, color=BLUE, edgecolor="white", lw=0.4)
    axes[0].text(0.5, -0.12, "isolated spins → no long-range order", ha="center", transform=axes[0].transAxes)

    # Fe clusters.
    centers = np.array([[0.27, 0.30], [0.66, 0.73], [0.78, 0.23]])
    for center in centers:
        pts = center + rng.normal(scale=0.035, size=(12, 2))
        axes[1].scatter(pts[:, 0], pts[:, 1], s=23, color=RED, edgecolor="white", lw=0.4)
    axes[1].text(0.5, -0.12, "Fe-rich regions → exchange coupling", ha="center", transform=axes[1].transAxes)

    # Random bulk As.
    pts = rng.uniform(0.06, 0.94, size=(45, 2))
    axes[2].scatter(pts[:, 0], pts[:, 1], s=17, color=PURPLE, edgecolor="white", lw=0.4)
    axes[2].text(0.5, -0.12, "many bulk scatterers → ρ increases", ha="center", transform=axes[2].transAxes)

    # Bi along representative grain boundaries.
    gb_paths = [
        np.column_stack([np.linspace(0.26, 0.48, 10), np.linspace(0.62, 0.43, 10)]),
        np.column_stack([np.linspace(0.48, 0.73, 11), np.linspace(0.43, 0.57, 11)]),
        np.column_stack([np.linspace(0.73, 0.78, 9), np.linspace(0.57, 1.0, 9)]),
    ]
    for pts in gb_paths:
        axes[3].scatter(pts[:, 0], pts[:, 1], s=25, color=RED, edgecolor="white", lw=0.4, zorder=5)
    axes[3].text(0.5, -0.12, "thin GB layer → cohesion decreases", ha="center", transform=axes[3].transAxes)

    fig.suptitle("Dilute solute does not imply the same spatial distribution", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.88))
    finish(fig, "cu-microstructure-models.svg")


def age_hardening_curve() -> None:
    log_t = np.array([-3, -2.0, -1.65, -1.25, -1.0, -0.35, 0.25, 0.75, 1.15, 1.45, 1.8, 2.25, 2.7, 3.0])
    hardness = np.array([60, 60, 61, 69, 80, 87, 91, 103, 116, 119, 114, 98, 87, 83])
    xx = np.linspace(-3, 3, 700)
    yy = PchipInterpolator(log_t, hardness)(xx)

    fig, ax = plt.subplots(figsize=(9.6, 5.3))
    stage_spans = [
        (-2.0, -1.0, BLUE, "A"),
        (-1.0, 0.75, TEAL, "B"),
        (0.75, 1.65, GOLD, "C"),
        (1.65, 3.0, RED, "D"),
    ]
    for left, right, color, label in stage_spans:
        ax.axvspan(10**left, 10**right, color=color, alpha=0.12)
        ax.text(10 ** ((left + right) / 2), 133, label, ha="center", weight="bold", fontsize=14, color=color)
    ax.semilogx(10**xx, yy, color=NAVY, lw=3)
    peak_x = 10**xx[np.argmax(yy)]
    peak_y = np.max(yy)
    ax.scatter([peak_x], [peak_y], color=RED, s=50, zorder=5)
    ax.annotate(
        "peak-aged",
        xy=(peak_x, peak_y),
        xytext=(32, 128),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        ha="center",
    )
    ax.text(2.0e-3, 48, "supersaturated\nsolid solution", ha="center")
    ax.text(3.0e-2, 68, "GP zones", ha="center")
    ax.text(0.6, 83, "GP2 / θ″", ha="center")
    ax.text(18, 103, "fine θ″ / θ′", ha="center")
    ax.text(250, 75, "coarsened θ′ / θ\n(over-aged)", ha="center")
    ax.set(xlim=(1e-3, 1e3), ylim=(40, 140), xlabel="Ageing time / day", ylabel="Hardness (schematic)")
    ax.set_title("Al–4 wt% Cu aged near 148 °C — schematic", fontsize=14, weight="bold")
    ax.grid(True, which="both", alpha=0.30, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(
        0.5,
        0.01,
        "Redrawn from the supplied exam figure. Values between labelled points are illustrative, not digitised measurements.",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    finish(fig, "alcu-age-hardening.svg")


def precipitation_stages() -> None:
    rng = np.random.default_rng(82)
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.8))
    stage_info = [
        ("A: GP zones", "coherent + shearable"),
        ("B: GP2 / θ″", "strain field + cutting"),
        ("C: near peak", "fine obstacles + bypass"),
        ("D: over-ageing", "coarse + wide spacing"),
    ]
    for ax, (title, subtitle) in zip(axes, stage_info, strict=True):
        ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
        ax.set_facecolor(LIGHT)
        ax.set_title(title, weight="bold")
        ax.text(0.5, 0.04, subtitle, ha="center", color=GRAY, fontsize=9)
        ax.axis("off")

    # A: many tiny coherent zones and a nearly straight dislocation.
    for x, y in rng.uniform([0.08, 0.18], [0.92, 0.88], size=(38, 2)):
        axes[0].add_patch(Circle((x, y), 0.015, color=BLUE, alpha=0.8))
    axes[0].plot([0.05, 0.95], [0.50, 0.54], color=RED, lw=2.4)

    # B: plate-like coherent particles.
    for x, y in rng.uniform([0.10, 0.20], [0.90, 0.88], size=(18, 2)):
        axes[1].add_patch(Rectangle((x - 0.045, y - 0.008), 0.09, 0.016, color=TEAL, alpha=0.9))
        axes[1].add_patch(Circle((x, y), 0.065, fill=False, ec=TEAL, alpha=0.16, lw=5))
    axes[1].plot([0.05, 0.95], [0.46, 0.58], color=RED, lw=2.4)

    # C: fine non-shearable particles; bowed line.
    centers = [(0.18, 0.55), (0.42, 0.55), (0.67, 0.55), (0.88, 0.55)]
    for x, y in centers:
        axes[2].add_patch(Circle((x, y), 0.055, fc=GOLD, ec=NAVY, lw=1.2))
    for (x0, _), (x1, _) in zip(centers[:-1], centers[1:], strict=True):
        x = np.linspace(x0 + 0.055, x1 - 0.055, 80)
        mid = (x0 + x1) / 2
        radius = (x1 - x0) / 2
        y = 0.55 - 0.16 * np.sqrt(np.clip(1 - ((x - mid) / radius) ** 2, 0, 1))
        axes[2].plot(x, y, color=RED, lw=2.3)
    axes[2].annotate("Orowan bowing", xy=(0.54, 0.41), xytext=(0.55, 0.18), ha="center", arrowprops={"arrowstyle": "->"})

    # D: few coarse particles and broad gaps.
    for x, y, r in [(0.20, 0.58, 0.12), (0.75, 0.48, 0.14)]:
        axes[3].add_patch(Circle((x, y), r, fc=ORANGE, ec=NAVY, lw=1.2))
    axes[3].plot([0.03, 0.95], [0.29, 0.40], color=RED, lw=2.3)
    axes[3].annotate("large λ", xy=(0.47, 0.35), xytext=(0.48, 0.14), ha="center", arrowprops={"arrowstyle": "<->"})

    fig.suptitle("Precipitate evolution and dislocation interaction", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    finish(fig, "alcu-precipitation-stages.svg")


def cct_diagram() -> None:
    fig, ax = plt.subplots(figsize=(9.6, 6.0))
    ax.set_xscale("log")

    # Schematic transformation boundaries.
    t_f_s = np.array([0.85, 1.0, 1.4, 2.3, 4.5, 10, 30, 100])
    T_f_s = np.array([520, 600, 680, 735, 770, 790, 800, 805])
    t_f_f = np.array([1.1, 1.35, 2.0, 3.8, 8, 20, 60, 140])
    T_f_f = np.array([500, 570, 630, 675, 700, 710, 715, 715])
    t_b_s = np.array([0.75, 0.95, 1.5, 2.8, 6.0])
    T_b_s = np.array([455, 500, 535, 550, 545])
    t_b_f = np.array([1.0, 1.4, 2.2, 4.0, 7.5])
    T_b_f = np.array([440, 455, 445, 420, 385])

    ax.plot(t_f_s, T_f_s, color=TEAL, lw=2.8, label="diffusional start")
    ax.plot(t_f_f, T_f_f, color=TEAL, lw=2.8, ls="--", label="diffusional finish")
    ax.plot(t_b_s, T_b_s, color=ORANGE, lw=2.6, label="bainite start")
    ax.plot(t_b_f, T_b_f, color=ORANGE, lw=2.6, ls="--", label="bainite finish")
    ax.axhline(450, color=BLUE, lw=2.4)
    ax.text(0.23, 460, "$M_s$", color=BLUE, weight="bold")

    # Cooling paths A and B.
    t = np.logspace(-0.55, 2.25, 400)
    logt = np.log10(t)
    T_A = 870 - 610 * (logt + 0.55) / 0.85
    T_B = 870 - 610 * (logt + 0.55) / 2.75
    ax.plot(t[T_A > 300], T_A[T_A > 300], color=NAVY, lw=2.0, ls="-.", label="cooling A")
    ax.plot(t[T_B > 300], T_B[T_B > 300], color=PURPLE, lw=2.0, ls="-.", label="cooling B")
    ax.text(0.55, 560, "A", color=NAVY, fontsize=13, weight="bold")
    ax.text(70, 570, "B", color=PURPLE, fontsize=13, weight="bold")

    # Numbered fields, following the supplied diagram's reading task.
    labels = [
        (0.45, 705, "① γ"),
        (7.0, 755, "② γ + α"),
        (4.0, 635, "③ α + P"),
        (2.3, 495, "④ B"),
        (0.50, 365, "⑤ M"),
    ]
    for x, y, text in labels:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": GRID, "alpha": 0.92},
        )
    ax.text(0.20, 845, "austenitised", color=GRAY)
    ax.set(
        xlim=(0.2, 180),
        ylim=(300, 900),
        xlabel="Time / s (log scale)",
        ylabel="Temperature / °C",
        title="Fe–0.15 wt% C continuous-cooling map — schematic",
    )
    ax.grid(True, which="both", alpha=0.28, color=GRID)
    ax.legend(ncol=3, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.23))
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(
        0.5,
        0.01,
        "γ: austenite, α: ferrite, P: pearlite, B: bainite, M: martensite. Curves are redrawn for concept reading.",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    finish(fig, "fe015c-cct-schematic.svg")


def heat_treatments() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.3), sharex=True, sharey=True)
    processes = [
        ("Full anneal", RED, "furnace cool", 0.50),
        ("Normalise", TEAL, "air cool", 0.72),
        ("Quench", BLUE, "rapid cool", 0.94),
        ("Temper after quench", PURPLE, "reheat below A₁", None),
    ]
    for ax, (title, color, note, slope) in zip(axes.flat, processes, strict=True):
        ax.axhline(727, color=GRAY, ls="--", lw=1.3)
        ax.text(0.15, 742, "$A_1$", color=GRAY)
        ax.axhspan(760, 835, color=GOLD, alpha=0.13)
        if title != "Temper after quench":
            x = [0, 1.2, 2.4, 3.2]
            y = [20, 820, 820, 820]
            ax.plot(x, y, color=color, lw=3)
            end_x = 7.8
            end_y = 20
            ax.plot([3.2, end_x], [820, end_y], color=color, lw=3)
            ax.annotate(note, xy=(5.7, 360), xytext=(4.7, 520), arrowprops={"arrowstyle": "->", "color": color}, color=color)
            if slope is not None:
                ax.text(6.8, 105 + 110 * (1 - slope), f"relative rate\n{slope:.2f}", ha="center", color=GRAY, fontsize=8)
        else:
            ax.plot([0, 0.8, 1.4], [820, 820, 20], color=BLUE, lw=2.4, alpha=0.55)
            ax.plot([1.4, 2.4, 3.2, 5.0, 6.0], [20, 540, 540, 540, 20], color=color, lw=3)
            ax.annotate(note, xy=(3.6, 540), xytext=(4.7, 680), arrowprops={"arrowstyle": "->", "color": color}, color=color)
        ax.set_title(title, weight="bold")
        ax.set(xlim=(0, 8), ylim=(0, 900))
        ax.grid(alpha=0.20, color=GRID)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("Temperature / °C")
    for ax in axes[1, :]:
        ax.set_xlabel("Time (schematic)")
    fig.suptitle("Steel heat-treatment paths and cooling-rate hierarchy", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    finish(fig, "steel-heat-treatments.svg")


def dp_trip_processes() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10.8, 7.2), sharex=True)
    for ax in axes:
        ax.axhline(727, color=GRAY, ls="--", lw=1.2)
        ax.text(0.12, 740, "$A_1$", color=GRAY)
        ax.axhline(850, color=GRAY, ls=":", lw=1.2)
        ax.text(0.12, 862, "$A_3$", color=GRAY)
        ax.grid(alpha=0.20, color=GRID)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(0, 930)
        ax.set_ylabel("Temperature / °C")

    # DP.
    ax = axes[0]
    x = [0, 1, 2.7, 4.0, 4.6, 7.5]
    y = [20, 790, 790, 790, 20, 20]
    ax.plot(x, y, color=BLUE, lw=3)
    ax.axhspan(727, 850, color=GOLD, alpha=0.12)
    ax.text(2.5, 820, "intercritical anneal: α + γ", ha="center")
    ax.annotate("quench: γ → M", xy=(4.35, 390), xytext=(5.4, 560), arrowprops={"arrowstyle": "->", "color": BLUE}, color=BLUE)
    ax.text(6.3, 110, "final: ferrite + martensite", ha="center", weight="bold")
    ax.set_title("Dual-phase steel", weight="bold")

    # TRIP.
    ax = axes[1]
    x = [0, 1, 2.4, 3.3, 3.8, 5.8, 6.3, 8.0]
    y = [20, 790, 790, 790, 420, 420, 20, 20]
    ax.plot(x, y, color=PURPLE, lw=3)
    ax.axhspan(350, 480, color=TEAL, alpha=0.12)
    ax.text(2.2, 820, "intercritical: α + γ", ha="center")
    ax.text(4.8, 455, "bainitic hold", ha="center", weight="bold")
    ax.annotate("C partitions to γ", xy=(5.0, 420), xytext=(6.1, 610), arrowprops={"arrowstyle": "->", "color": PURPLE}, color=PURPLE)
    ax.text(7.2, 115, "final: α + bainite + retained γ", ha="center", weight="bold")
    ax.set_title("TRIP-assisted steel", weight="bold")
    ax.set_xlabel("Time (schematic)")
    fig.suptitle("Intercritical processing builds multiphase steels", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    finish(fig, "dp-trip-heat-treatment.svg")


def tmcp_process() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=True)
    for ax in axes:
        ax.set(xlim=(0, 10), ylim=(300, 1250), xlabel="Process time", ylabel="Temperature / °C")
        ax.grid(alpha=0.20, color=GRID)
        ax.spines[["top", "right"]].set_visible(False)
        ax.axhspan(800, 980, color=GOLD, alpha=0.10)
    axes[0].plot([0, 2, 4, 6, 10], [1200, 1120, 980, 880, 500], color=GRAY, lw=3)
    for x in [2.0, 3.1, 4.0]:
        axes[0].annotate("roll", xy=(x, 1020), xytext=(x, 1130), ha="center", arrowprops={"arrowstyle": "-|>", "color": NAVY})
    axes[0].text(7.8, 700, "air cooling", ha="center")
    axes[0].text(7.2, 420, "coarser ferrite + pearlite", ha="center", weight="bold")
    axes[0].set_title("Conventional hot rolling", weight="bold")

    axes[1].plot([0, 1.7, 3.0, 5.8, 6.2, 10], [1200, 1080, 930, 820, 650, 400], color=TEAL, lw=3)
    for x, y in [(1.5, 1100), (2.6, 970), (3.8, 900), (5.0, 850)]:
        axes[1].annotate("roll", xy=(x, y - 45), xytext=(x, y + 65), ha="center", arrowprops={"arrowstyle": "-|>", "color": NAVY})
    axes[1].annotate("accelerated cooling", xy=(6.3, 635), xytext=(7.5, 820), arrowprops={"arrowstyle": "->", "color": TEAL}, color=TEAL)
    axes[1].text(4.8, 750, "pancaked γ\n+ high nucleation density", ha="center")
    axes[1].text(8.0, 420, "fine ferrite / bainite", ha="center", weight="bold")
    axes[1].set_title("TMCP", weight="bold")
    fig.suptitle("Rolling temperature and cooling rate control final grain size", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    finish(fig, "tmcp-comparison.svg")


def l12_kw() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))

    # Ordered lattice and APB.
    ax = axes[0]
    for i in range(7):
        for j in range(5):
            color = RED if (i % 2 == 0 and j % 2 == 0) else BLUE
            ax.add_patch(Circle((i, j), 0.11, fc=color, ec="white", lw=0.5))
    ax.axvspan(3.05, 3.65, color=GOLD, alpha=0.35)
    ax.plot([3.35, 3.35], [-0.3, 4.3], color=NAVY, lw=2, ls="--")
    ax.text(3.35, 4.45, "APB", ha="center", weight="bold")
    ax.add_patch(FancyArrowPatch((1.0, -0.55), (2.4, -0.55), arrowstyle="-|>", mutation_scale=15, color=RED, lw=2))
    ax.text(1.7, -0.9, r"$a/2\langle110\rangle$", ha="center")
    ax.add_patch(FancyArrowPatch((4.0, -0.55), (5.4, -0.55), arrowstyle="-|>", mutation_scale=15, color=RED, lw=2))
    ax.text(4.7, -0.9, r"$a/2\langle110\rangle$", ha="center")
    ax.set(xlim=(-0.4, 6.4), ylim=(-1.2, 4.8), aspect="equal")
    ax.axis("off")
    ax.set_title("Superdislocation pair + antiphase boundary", weight="bold")

    # Cross-slip lock.
    ax = axes[1]
    p111 = Polygon([(0.5, 0.8), (5.7, 0.8), (7.0, 2.2), (1.8, 2.2)], closed=True, fc=BLUE, ec=NAVY, alpha=0.16)
    p100 = Polygon([(3.8, 0.4), (6.2, 1.4), (6.2, 4.3), (3.8, 3.3)], closed=True, fc=GOLD, ec=NAVY, alpha=0.24)
    ax.add_patch(p111)
    ax.add_patch(p100)
    ax.plot([1.1, 4.1], [1.45, 1.45], color=RED, lw=3)
    ax.plot([4.1, 5.5], [1.45, 2.05], color=RED, lw=3)
    ax.plot([5.5, 5.5], [2.05, 3.45], color=RED, lw=3)
    ax.text(1.8, 1.0, "{111} glide", ha="center")
    ax.text(5.65, 3.85, "{100}\ncross-slip", ha="center")
    ax.annotate("sessile KW lock", xy=(5.5, 2.8), xytext=(2.5, 3.8), arrowprops={"arrowstyle": "->", "color": NAVY}, weight="bold")
    ax.set(xlim=(0, 7.3), ylim=(0, 4.6), aspect="equal")
    ax.axis("off")
    ax.set_title("Thermally activated cube cross-slip", weight="bold")

    fig.suptitle(r"$L1_2$ Ni$_3$Al: order makes an ordinary fcc translation incomplete", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    finish(fig, "l12-apb-kear-wilsdorf.svg")


def main() -> None:
    phase_diagrams()
    cu_microstructures()
    age_hardening_curve()
    precipitation_stages()
    cct_diagram()
    heat_treatments()
    dp_trip_processes()
    tmcp_process()
    l12_kw()


if __name__ == "__main__":
    main()
