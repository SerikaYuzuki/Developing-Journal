"""金属材料学の変形・強化基礎を説明する模式図をSVGで生成する。

図は概念理解を目的とした模式図であり、曲線形状、原子配置、転位芯、
粒界応力の大きさを定量的に表すものではない。
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/codex-mpl-metal-materials-foundations")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
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
        "svg.hashsalt": "metal-materials-foundations-2026-07-24",
    }
)


def finish(fig: plt.Figure, name: str) -> None:
    """白背景の決定的なSVGとして保存し、行末空白を除去する。"""

    output_path = OUT / name
    fig.savefig(
        output_path,
        format="svg",
        bbox_inches="tight",
        facecolor="white",
        metadata={"Date": None},
    )
    plt.close(fig)
    svg = output_path.read_text(encoding="utf-8")
    output_path.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )


def toughness_stress_strain() -> None:
    """延性材と脆性材について、破断までの面積を比較する。"""

    ductile_x = np.array([0.0, 0.010, 0.030, 0.080, 0.160, 0.240, 0.300, 0.340])
    ductile_y = np.array([0.0, 0.54, 0.62, 0.72, 0.84, 0.93, 0.89, 0.78])
    brittle_x = np.array([0.0, 0.012, 0.025, 0.038, 0.052])
    brittle_y = np.array([0.0, 0.24, 0.49, 0.75, 1.04])

    ductile_xx = np.linspace(ductile_x.min(), ductile_x.max(), 360)
    ductile_yy = PchipInterpolator(ductile_x, ductile_y)(ductile_xx)
    brittle_xx = np.linspace(brittle_x.min(), brittle_x.max(), 160)
    brittle_yy = PchipInterpolator(brittle_x, brittle_y)(brittle_xx)

    fig, ax = plt.subplots(figsize=(9.8, 5.5))
    ax.fill_between(ductile_xx, 0, ductile_yy, color=TEAL, alpha=0.20)
    ax.fill_between(brittle_xx, 0, brittle_yy, color=RED, alpha=0.20)
    ax.plot(ductile_xx, ductile_yy, color=TEAL, lw=3.2, label="延性材")
    ax.plot(brittle_xx, brittle_yy, color=RED, lw=3.2, label="脆性材")
    ax.scatter(
        [ductile_x[-1], brittle_x[-1]],
        [ductile_y[-1], brittle_y[-1]],
        color=[TEAL, RED],
        marker="X",
        s=85,
        zorder=5,
    )

    ax.annotate(
        "破断",
        xy=(ductile_x[-1], ductile_y[-1]),
        xytext=(0.315, 0.61),
        arrowprops={"arrowstyle": "->", "color": TEAL},
        color=TEAL,
        ha="center",
    )
    ax.annotate(
        "破断",
        xy=(brittle_x[-1], brittle_y[-1]),
        xytext=(0.085, 1.06),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
    )
    ax.annotate(
        "破断までの面積\n＝ 単位体積あたりの吸収エネルギー\n＝ 靭性",
        xy=(0.19, 0.55),
        xytext=(0.22, 1.10),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        ha="center",
        va="top",
        weight="bold",
    )
    ax.text(
        0.083,
        0.86,
        "高い応力でも\n破断ひずみが小さい",
        color=RED,
        ha="left",
    )
    ax.text(
        0.265,
        0.32,
        "塑性変形で\n大きなエネルギーを吸収",
        color=TEAL,
        ha="center",
    )

    ax.set(
        xlim=(0, 0.38),
        ylim=(0, 1.16),
        xlabel=r"ひずみ $\varepsilon$  →",
        ylabel=r"応力 $\sigma$  →",
    )
    ax.set_title("靭性は「強さ」だけでなく、破断までの変形を含む", fontsize=15, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(alpha=0.18, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False)
    fig.text(
        0.5,
        0.015,
        "教育用模式図：曲線形状・応力・ひずみの値は定量データではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    finish(fig, "toughness-stress-strain.svg")


def _atom(ax: plt.Axes, x: float, y: float, *, color: str = BLUE, radius: float = 0.026) -> None:
    ax.add_patch(Circle((x, y), radius, fc=color, ec="white", lw=0.6, zorder=4))


def dislocation_slip() -> None:
    """完全結晶の一斉せん断と、転位芯の局所移動を対比する。"""

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.6))

    # 完全結晶：すべり面を挟む多数の結合を一斉に組み替える。
    ax = axes[0]
    ax.add_patch(Rectangle((0.04, 0.12), 0.92, 0.78, fc=LIGHT, ec="none", zorder=0))
    glide_y = 0.51
    ax.plot([0.07, 0.94], [glide_y, glide_y], color=GRAY, lw=1.4, ls="--")
    xs = np.linspace(0.13, 0.84, 7)
    bottom_ys = [0.24, 0.36, 0.46]
    top_ys = [0.58, 0.70, 0.82]
    shear = 0.075

    for y in bottom_ys:
        for x in xs:
            _atom(ax, x, y)
    for y in top_ys:
        for x in xs:
            ax.add_patch(Circle((x, y), 0.026, fill=False, ec=GRID, lw=1.0, ls="--"))
            _atom(ax, x + shear, y)
    for x in xs:
        ax.plot([x, x + shear], [0.46, 0.58], color=RED, lw=1.0, alpha=0.72)
    ax.add_patch(
        FancyArrowPatch(
            (0.31, 0.91),
            (0.70, 0.91),
            arrowstyle="-|>",
            mutation_scale=17,
            color=RED,
            lw=2.5,
        )
    )
    ax.text(0.50, 0.95, "上半分を一斉にずらす", color=RED, ha="center", weight="bold")
    ax.text(0.51, 0.535, "すべり面", color=GRAY, ha="center", fontsize=9)
    ax.text(
        0.50,
        0.075,
        "一面の多数の結合を同時に組み替える\n→ 大きな理想せん断応力が必要",
        ha="center",
        va="top",
        weight="bold",
    )
    ax.set_title("完全結晶：原子面の一斉せん断", weight="bold", fontsize=13)
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")

    # 実在結晶：余分な半原子面の端、すなわち転位芯だけが順次移動する。
    ax = axes[1]
    ax.add_patch(Rectangle((0.04, 0.28), 0.92, 0.62, fc=LIGHT, ec="none", zorder=0))
    glide_y = 0.52
    ax.plot([0.07, 0.94], [glide_y, glide_y], color=GRAY, lw=1.4, ls="--")
    lattice_xs = np.linspace(0.13, 0.87, 7)
    lattice_ys = [0.34, 0.45, 0.59, 0.70, 0.81]
    for y in lattice_ys:
        for x in lattice_xs:
            _atom(ax, x, y)

    core_x = 0.43
    future_x = 0.73
    for y in [0.59, 0.70, 0.81]:
        _atom(ax, core_x, y, color=ORANGE, radius=0.029)
    ax.plot([core_x, core_x], [0.55, 0.85], color=ORANGE, lw=2.0, alpha=0.8)
    ax.add_patch(Circle((core_x, glide_y), 0.052, fill=False, ec=RED, lw=2.3))
    ax.plot([future_x, future_x], [0.55, 0.85], color=GRAY, lw=1.5, ls=":", alpha=0.85)
    ax.add_patch(Circle((future_x, glide_y), 0.052, fill=False, ec=GRAY, lw=1.5, ls=":"))
    ax.add_patch(
        FancyArrowPatch(
            (core_x + 0.06, glide_y),
            (future_x - 0.06, glide_y),
            arrowstyle="-|>",
            mutation_scale=17,
            color=RED,
            lw=2.4,
        )
    )
    ax.annotate(
        "余分な半原子面",
        xy=(core_x, 0.76),
        xytext=(0.18, 0.88),
        arrowprops={"arrowstyle": "->", "color": ORANGE},
        color=ORANGE,
        ha="center",
    )
    ax.annotate(
        "転位芯",
        xy=(core_x, glide_y),
        xytext=(0.22, 0.57),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        weight="bold",
    )
    ax.text(
        0.50,
        0.285,
        "芯近傍の結合だけを順次組み替える",
        ha="center",
        va="bottom",
        weight="bold",
    )

    rug_x = np.linspace(0.10, 0.92, 300)
    rug_now = 0.13 + 0.11 * np.exp(-((rug_x - 0.34) / 0.075) ** 2)
    rug_future = 0.13 + 0.11 * np.exp(-((rug_x - 0.72) / 0.075) ** 2)
    ax.plot(rug_x, rug_now, color=TEAL, lw=3.0)
    ax.plot(rug_x, rug_future, color=GRAY, lw=2.0, ls=":")
    ax.add_patch(
        FancyArrowPatch(
            (0.43, 0.19),
            (0.63, 0.19),
            arrowstyle="-|>",
            mutation_scale=16,
            color=RED,
            lw=2.0,
        )
    )
    ax.text(0.50, 0.025, "じゅうたん全体ではなく「しわ」を移すのと同じ直感", ha="center")
    ax.set_title("実在結晶：転位の局所移動", weight="bold", fontsize=13)
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")

    fig.suptitle("塑性変形では、結晶全体を一度にずらす必要はない", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：原子配置、転位芯の形状、移動距離は定量的ではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.045, 1, 0.92))
    finish(fig, "dislocation-slip.svg")


def _grain_boundary(ax: plt.Axes, x: float, *, color: str = NAVY) -> None:
    y = np.linspace(0.18, 0.84, 160)
    waviness = 0.008 * np.sin(np.linspace(0, 7 * np.pi, y.size))
    ax.plot(x + waviness, y, color=color, lw=2.0, zorder=5)


def _pileup_panel(
    ax: plt.Axes,
    *,
    left_boundary: float,
    right_boundary: float,
    dislocations: list[float],
    transmitted: bool,
    title: str,
    grain_label: str,
) -> None:
    ax.add_patch(Rectangle((0.03, 0.16), 0.94, 0.70, fc=LIGHT, ec="none"))
    ax.axvspan(0.03, left_boundary, ymin=0.16, ymax=0.86, color=GOLD, alpha=0.10)
    ax.axvspan(right_boundary, 0.97, ymin=0.16, ymax=0.86, color=GOLD, alpha=0.10)
    _grain_boundary(ax, left_boundary)
    _grain_boundary(ax, right_boundary)

    slip_y = 0.50
    ax.plot([left_boundary, right_boundary], [slip_y, slip_y], color=BLUE, lw=2.0)
    ax.plot([right_boundary, 0.96], [slip_y, 0.65], color=BLUE, lw=1.7, ls="--")
    for x in dislocations:
        ax.text(x, slip_y + 0.015, r"$\perp$", color=RED, fontsize=18, ha="center", va="center")

    head_x = dislocations[-1]
    for radius, alpha in [(0.035, 0.75), (0.060, 0.45), (0.085, 0.22)]:
        ax.add_patch(Circle((head_x, slip_y), radius, fill=False, ec=RED, lw=1.3, alpha=alpha))

    ax.add_patch(
        FancyArrowPatch(
            (left_boundary + 0.06, 0.79),
            (left_boundary + 0.31, 0.79),
            arrowstyle="-|>",
            mutation_scale=16,
            color=NAVY,
            lw=2.0,
        )
    )
    ax.text(left_boundary + 0.18, 0.82, r"外力 $\tau$", ha="center", va="bottom")

    ax.add_patch(
        FancyArrowPatch(
            (left_boundary + 0.02, 0.25),
            (right_boundary - 0.02, 0.25),
            arrowstyle="<->",
            mutation_scale=14,
            color=GRAY,
            lw=1.5,
        )
    )
    ax.text((left_boundary + right_boundary) / 2, 0.205, grain_label, color=GRAY, ha="center")
    ax.text(right_boundary, 0.89, "粒界", ha="center", color=GRAY)

    if transmitted:
        ax.add_patch(
            FancyArrowPatch(
                (right_boundary - 0.01, slip_y + 0.01),
                (0.93, 0.63),
                arrowstyle="-|>",
                mutation_scale=18,
                color=TEAL,
                lw=3.0,
            )
        )
        ax.text(0.87, 0.70, "すべり伝達", color=TEAL, ha="center", weight="bold")
        ax.text(
            0.50,
            0.075,
            "長い堆積列 → 先頭応力が大きい\n小さい外力でも隣接粒へ伝達",
            ha="center",
            va="center",
            weight="bold",
        )
    else:
        ax.add_patch(
            FancyArrowPatch(
                (right_boundary - 0.08, slip_y + 0.01),
                (right_boundary - 0.015, slip_y + 0.01),
                arrowstyle="-|>",
                mutation_scale=15,
                color=GRAY,
                lw=2.0,
                ls="--",
            )
        )
        ax.text(right_boundary + 0.02, slip_y + 0.01, "×", color=RED, fontsize=20, va="center")
        ax.text(
            0.50,
            0.075,
            "短い堆積列 → 先頭応力が小さい\n粒界を越すには、より大きい外力が必要",
            ha="center",
            va="center",
            weight="bold",
        )

    ax.set_title(title, weight="bold", fontsize=13)
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")


def hall_petch() -> None:
    """古典的な転位堆積モデルで、大粒と小粒を比較する。"""

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))
    _pileup_panel(
        axes[0],
        left_boundary=0.08,
        right_boundary=0.88,
        dislocations=[0.31, 0.46, 0.58, 0.68, 0.75, 0.80, 0.835],
        transmitted=True,
        title="大きい結晶粒",
        grain_label=r"粒径 $d$：大",
    )
    _pileup_panel(
        axes[1],
        left_boundary=0.30,
        right_boundary=0.70,
        dislocations=[0.48, 0.58, 0.645],
        transmitted=False,
        title="小さい結晶粒",
        grain_label=r"粒径 $d$：小",
    )
    fig.suptitle("粒径を小さくすると、転位の堆積列が短くなる", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.062,
        r"Hall--Petch則：$\sigma_y=\sigma_0+k_y d^{-1/2}$",
        ha="center",
        weight="bold",
        fontsize=12,
    )
    fig.text(
        0.5,
        0.015,
        "教育用模式図：古典的pile-upモデルを示す。実材料では粒界からの転位放出なども寄与する。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.91))
    finish(fig, "hall-petch.svg")


def main() -> None:
    toughness_stress_strain()
    dislocation_slip()
    hall_petch()


if __name__ == "__main__":
    main()
