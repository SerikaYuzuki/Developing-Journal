"""鉄鋼分野の補助模式図を決定的なSVGとして生成する。

図中の曲線位置、温度、時間、組織寸法は定性的な説明用であり、
材料設計へ使える定量データではない。
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    "/private/tmp/codex-mpl-metal-materials-steel-extra",
)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)


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
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "svg.hashsalt": "metal-materials-steel-extra-2026-07-24",
    }
)


def finish(fig: Figure, name: str) -> None:
    """SVGを保存し、Matplotlib由来の行末空白を除去する。"""

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


FP_START_T = np.array([0.85, 1.0, 1.4, 2.3, 4.5, 10.0, 30.0, 100.0])
FP_START_TEMP = np.array([520, 600, 680, 735, 770, 790, 800, 805])
FP_FINISH_T = np.array([1.1, 1.35, 2.0, 3.8, 8.0, 20.0, 60.0, 140.0])
FP_FINISH_TEMP = np.array([500, 570, 630, 675, 700, 710, 715, 715])
BAINITE_START_T = np.array([0.75, 0.95, 1.5, 2.8, 6.0])
BAINITE_START_TEMP = np.array([455, 500, 535, 550, 545])
BAINITE_FINISH_T = np.array([1.0, 1.4, 2.2, 4.0, 7.5])
BAINITE_FINISH_TEMP = np.array([440, 455, 445, 420, 385])


def _plot_base_cct(ax: Axes) -> None:
    """基準CCT境界をすべて実線で描く。"""

    ax.plot(FP_START_T, FP_START_TEMP, color=NAVY, lw=2.8)
    ax.plot(FP_FINISH_T, FP_FINISH_TEMP, color=NAVY, lw=1.7)
    ax.plot(BAINITE_START_T, BAINITE_START_TEMP, color=BLUE, lw=2.8)
    ax.plot(BAINITE_FINISH_T, BAINITE_FINISH_TEMP, color=BLUE, lw=1.7)
    ax.axhline(450, color=TEAL, lw=2.4)
    ax.text(17, 810, "F/P 開始", color=NAVY, weight="bold")
    ax.text(30, 720, "F/P 終了", color=NAVY)
    ax.text(2.7, 560, "B 開始", color=BLUE, weight="bold")
    ax.text(3.0, 402, "B 終了", color=BLUE)
    ax.text(0.23, 462, r"$M_\mathrm{s}$", color=TEAL, weight="bold")


def _format_cct_axis(ax: Axes, title: str) -> None:
    ax.set_xscale("log")
    ax.set(
        xlim=(0.2, 1200),
        ylim=(300, 900),
        xlabel="時間 / s（対数軸）",
        ylabel="温度 / °C",
        title=title,
    )
    ax.grid(True, which="both", alpha=0.24, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)


def cct_shifts() -> None:
    """Ni添加と旧γ粒粗大化によるCCT変化を比較する。"""

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.1), sharex=True, sharey=True)

    ax = axes[0]
    _plot_base_cct(ax)
    ni_time_scale = 6.0
    ni_temp_shift = -45
    ax.plot(
        FP_START_T * ni_time_scale,
        FP_START_TEMP + ni_temp_shift,
        color=PURPLE,
        lw=2.8,
        ls="--",
    )
    ax.plot(
        FP_FINISH_T * ni_time_scale,
        FP_FINISH_TEMP + ni_temp_shift,
        color=PURPLE,
        lw=1.7,
        ls="--",
    )
    ax.plot(
        BAINITE_START_T * 4.5,
        BAINITE_START_TEMP - 35,
        color=PURPLE,
        lw=2.8,
        ls="--",
    )
    ax.plot(
        BAINITE_FINISH_T * 4.5,
        BAINITE_FINISH_TEMP - 35,
        color=PURPLE,
        lw=1.7,
        ls="--",
    )
    ax.axhline(390, color=PURPLE, lw=2.2, ls="--")
    ax.annotate(
        "拡散変態が遅れる\n（右・低温側へ）",
        xy=(45, 730),
        xytext=(210, 835),
        arrowprops={"arrowstyle": "->", "color": PURPLE},
        color=PURPLE,
        ha="center",
        weight="bold",
    )
    ax.annotate(
        r"$M_\mathrm{s}$ 低下",
        xy=(0.32, 390),
        xytext=(0.48, 335),
        arrowprops={"arrowstyle": "->", "color": PURPLE},
        color=PURPLE,
        weight="bold",
    )
    _format_cct_axis(ax, "約5 mass% Ni添加")
    ax.legend(
        handles=[
            Line2D([0], [0], color=NAVY, lw=2.6, label="基準（実線）"),
            Line2D(
                [0],
                [0],
                color=PURPLE,
                lw=2.6,
                ls="--",
                label="Ni添加（破線）",
            ),
        ],
        loc="lower right",
        framealpha=0.95,
    )

    ax = axes[1]
    _plot_base_cct(ax)
    ax.plot(
        FP_START_T * 3.0,
        FP_START_TEMP,
        color=RED,
        lw=2.8,
        ls="--",
    )
    ax.plot(
        FP_FINISH_T * 2.0,
        FP_FINISH_TEMP,
        color=RED,
        lw=1.7,
        ls="--",
    )
    ax.annotate(
        "粒界核生成サイトが減少\nF/P開始が主に右へ",
        xy=(38, 780),
        xytext=(220, 850),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        weight="bold",
    )
    ax.annotate(
        r"$M_\mathrm{s}$ は概ね不変",
        xy=(1.0, 450),
        xytext=(3.5, 340),
        arrowprops={"arrowstyle": "->", "color": TEAL},
        color=TEAL,
        weight="bold",
    )
    _format_cct_axis(ax, "1300 °Cでγ化（旧γ粒粗大化）")
    ax.legend(
        handles=[
            Line2D([0], [0], color=NAVY, lw=2.6, label="基準（実線）"),
            Line2D(
                [0],
                [0],
                color=RED,
                lw=2.6,
                ls="--",
                label="1300 °C γ化（破線）",
            ),
        ],
        loc="lower right",
        framealpha=0.95,
    )

    fig.suptitle(
        "Fe–0.15 mass%C鋼：合金添加と旧γ粒径によるCCT変化",
        fontsize=15,
        weight="bold",
    )
    fig.text(
        0.5,
        0.012,
        "定性的模式図：曲線位置・変態温度・移動量は定量データではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    finish(fig, "fe015c-cct-shifts.svg")


def _panel_card(ax: Axes) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (0.02, 0.04),
            0.96,
            0.90,
            boxstyle="round,pad=0.018",
            facecolor="white",
            edgecolor=GRID,
            lw=1.3,
        )
    )
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")


def martensite_hierarchy() -> None:
    """旧γ粒からラスまでの階層と強化因子を示す。"""

    fig, axes = plt.subplots(1, 4, figsize=(12.6, 4.8))
    for ax in axes:
        _panel_card(ax)

    ax = axes[0]
    grain = Polygon(
        [(0.12, 0.18), (0.24, 0.82), (0.70, 0.88), (0.90, 0.58), (0.78, 0.16)],
        closed=True,
        facecolor=LIGHT,
        edgecolor=NAVY,
        lw=2.0,
    )
    ax.add_patch(grain)
    ax.add_patch(
        Polygon(
            [(0.17, 0.22), (0.27, 0.78), (0.48, 0.60), (0.47, 0.22)],
            closed=True,
            facecolor=TEAL,
            edgecolor="white",
            alpha=0.65,
        )
    )
    ax.add_patch(
        Polygon(
            [(0.27, 0.78), (0.68, 0.83), (0.70, 0.47), (0.48, 0.60)],
            closed=True,
            facecolor=GOLD,
            edgecolor="white",
            alpha=0.72,
        )
    )
    ax.add_patch(
        Polygon(
            [(0.48, 0.60), (0.70, 0.47), (0.83, 0.57), (0.74, 0.21), (0.47, 0.22)],
            closed=True,
            facecolor=PURPLE,
            edgecolor="white",
            alpha=0.50,
        )
    )
    ax.text(0.5, 0.97, "旧γ粒", ha="center", va="top", weight="bold", fontsize=13)
    ax.text(0.5, 0.08, "内部に複数のpacket", ha="center", color=GRAY)

    ax = axes[1]
    ax.add_patch(
        Polygon(
            [(0.12, 0.18), (0.30, 0.84), (0.88, 0.75), (0.70, 0.12)],
            closed=True,
            facecolor=LIGHT,
            edgecolor=NAVY,
            lw=1.8,
        )
    )
    block_colors = [TEAL, GOLD, PURPLE, ORANGE]
    for i, color in enumerate(block_colors):
        y0 = 0.20 + i * 0.145
        ax.add_patch(
            Polygon(
                [
                    (0.20 + 0.04 * i, y0),
                    (0.27 + 0.04 * i, y0 + 0.13),
                    (0.80 + 0.04 * i, y0 + 0.08),
                    (0.74 + 0.04 * i, y0 - 0.05),
                ],
                closed=True,
                facecolor=color,
                edgecolor="white",
                alpha=0.68,
            )
        )
    ax.text(0.5, 0.97, "packet", ha="center", va="top", weight="bold", fontsize=13)
    ax.text(0.5, 0.08, "同じ晶癖面を共有", ha="center", color=GRAY)

    ax = axes[2]
    ax.add_patch(
        Polygon(
            [(0.12, 0.18), (0.22, 0.83), (0.88, 0.73), (0.78, 0.10)],
            closed=True,
            facecolor=LIGHT,
            edgecolor=NAVY,
            lw=1.8,
        )
    )
    for i in range(8):
        y0 = 0.18 + i * 0.071
        ax.add_patch(
            Polygon(
                [
                    (0.18, y0),
                    (0.21, y0 + 0.045),
                    (0.83, y0 + 0.14),
                    (0.80, y0 + 0.095),
                ],
                closed=True,
                facecolor=BLUE if i % 2 == 0 else TEAL,
                edgecolor="white",
                alpha=0.72,
            )
        )
    ax.text(0.5, 0.97, "block", ha="center", va="top", weight="bold", fontsize=13)
    ax.text(0.5, 0.08, "近い結晶方位のlath群", ha="center", color=GRAY)

    ax = axes[3]
    ax.add_patch(
        Rectangle(
            (0.10, 0.53),
            0.80,
            0.31,
            facecolor=BLUE,
            edgecolor=NAVY,
            alpha=0.16,
            lw=1.8,
        )
    )
    x = np.linspace(0.14, 0.86, 120)
    for i in range(6):
        y = 0.58 + i * 0.042 + 0.012 * np.sin(10 * np.pi * x + i)
        ax.plot(x, y, color=RED if i % 2 == 0 else NAVY, lw=1.2)
    for x0, y0 in [(0.22, 0.60), (0.38, 0.74), (0.56, 0.64), (0.74, 0.77)]:
        ax.add_patch(Circle((x0, y0), 0.018, fill=False, ec=RED, lw=1.2))
    ax.annotate(
        "高転位密度",
        xy=(0.70, 0.70),
        xytext=(0.52, 0.90),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        weight="bold",
    )

    lattice_x = [0.24, 0.47, 0.70]
    lattice_y = [0.13, 0.27, 0.43]
    for x0 in lattice_x:
        for y0 in lattice_y:
            ax.add_patch(Circle((x0, y0), 0.018, fc=BLUE, ec=NAVY, lw=0.7))
    ax.plot([0.24, 0.70, 0.70, 0.24, 0.24], [0.13, 0.13, 0.43, 0.43, 0.13], color=GRAY, lw=1)
    ax.add_patch(Circle((0.47, 0.35), 0.025, fc=RED, ec=NAVY, lw=0.8))
    ax.annotate(
        "侵入C",
        xy=(0.47, 0.35),
        xytext=(0.77, 0.34),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        weight="bold",
    )
    ax.add_patch(
        FancyArrowPatch(
            (0.16, 0.13),
            (0.16, 0.43),
            arrowstyle="<->",
            mutation_scale=12,
            color=PURPLE,
            lw=1.4,
        )
    )
    ax.text(0.11, 0.28, r"$c>a$", rotation=90, ha="center", va="center", color=PURPLE)
    ax.text(0.5, 0.97, "lath", ha="center", va="top", weight="bold", fontsize=13)
    ax.text(0.5, 0.05, "Cによるbct格子ひずみ", ha="center", color=GRAY)

    for x0, x1 in [(0.245, 0.275), (0.495, 0.525), (0.745, 0.775)]:
        fig.add_artist(
            FancyArrowPatch(
                (x0, 0.51),
                (x1, 0.51),
                transform=fig.transFigure,
                arrowstyle="-|>",
                mutation_scale=16,
                color=NAVY,
                lw=1.5,
            )
        )

    fig.suptitle(
        "マルテンサイトの階層組織と強化因子（模式図）",
        fontsize=15,
        weight="bold",
    )
    fig.text(
        0.5,
        0.015,
        "各パネルの縮尺は共通ではない。階層境界・高転位密度・侵入Cの格子ひずみが転位運動を妨げる。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.91), w_pad=1.6)
    finish(fig, "martensite-hierarchy.svg")


def _arrow_between(
    ax: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    label_y: float,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=15,
            color=NAVY,
            lw=1.5,
        )
    )
    ax.text((start[0] + end[0]) / 2, label_y, label, ha="center", color=GRAY)


def _base_micro_box(
    ax: Axes,
    x0: float,
    y0: float,
    width: float,
    height: float,
    facecolor: str,
) -> None:
    ax.add_patch(
        Rectangle(
            (x0, y0),
            width,
            height,
            facecolor=facecolor,
            edgecolor=NAVY,
            lw=1.4,
        )
    )


def _draw_ferrite_pearlite(
    ax: Axes,
    x0: float,
    y0: float,
    width: float = 0.80,
    height: float = 0.52,
) -> None:
    _base_micro_box(ax, x0, y0, width, height, "#e8f5f2")
    ax.plot(
        [x0 + 0.31 * width, x0 + 0.38 * width, x0 + 0.34 * width],
        [y0, y0 + 0.26 * height, y0 + height],
        color=TEAL,
        lw=1,
    )
    ax.plot(
        [x0, x0 + 0.52 * width, x0 + width],
        [y0 + 0.60 * height, y0 + 0.55 * height, y0 + 0.70 * height],
        color=TEAL,
        lw=1,
    )
    colonies = [
        (x0 + 0.08 * width, y0 + 0.08 * height, 0.24 * width, 0.23 * height),
        (x0 + 0.58 * width, y0 + 0.58 * height, 0.30 * width, 0.25 * height),
    ]
    for cx, cy, cw, ch in colonies:
        ax.add_patch(Rectangle((cx, cy), cw, ch, fc=LIGHT, ec=ORANGE, lw=1))
        for j in range(4):
            yy = cy + (j + 1) * ch / 5
            ax.plot([cx + 0.03 * cw, cx + 0.97 * cw], [yy, yy], color=NAVY, lw=0.8)


def _draw_martensite(
    ax: Axes,
    x0: float,
    y0: float,
    width: float = 0.80,
    height: float = 0.52,
) -> None:
    _base_micro_box(ax, x0, y0, width, height, "#e7eef5")
    for i in range(9):
        xa = x0 + (0.04 + i * 0.095) * width
        xb = xa + 0.22 * width
        ax.plot(
            [xa, min(xb, x0 + 0.97 * width)],
            [y0 + 0.08 * height, y0 + 0.92 * height],
            color=BLUE if i % 2 == 0 else NAVY,
            lw=1.2,
        )


def _draw_alpha_gamma(
    ax: Axes,
    x0: float,
    y0: float,
    width: float = 0.80,
    height: float = 0.52,
) -> None:
    _base_micro_box(ax, x0, y0, width, height, "#e8f5f2")
    islands = [
        (0.22, 0.27, 0.20, 0.24),
        (0.62, 0.30, 0.25, 0.20),
        (0.47, 0.70, 0.21, 0.23),
        (0.82, 0.73, 0.16, 0.18),
    ]
    for cx, cy, ew, eh in islands:
        ax.add_patch(
            Ellipse(
                (x0 + cx * width, y0 + cy * height),
                ew * width,
                eh * height,
                facecolor=GOLD,
                edgecolor=NAVY,
                lw=0.9,
            )
        )


def _draw_alpha_martensite(
    ax: Axes,
    x0: float,
    y0: float,
    width: float = 0.80,
    height: float = 0.52,
) -> None:
    _base_micro_box(ax, x0, y0, width, height, "#e8f5f2")
    islands = [
        (0.20, 0.26, 0.22, 0.27, 18),
        (0.60, 0.28, 0.29, 0.18, -12),
        (0.48, 0.72, 0.23, 0.27, 8),
        (0.82, 0.72, 0.17, 0.20, -20),
    ]
    for cx, cy, ew, eh, angle in islands:
        ax.add_patch(
            Ellipse(
                (x0 + cx * width, y0 + cy * height),
                ew * width,
                eh * height,
                angle=angle,
                facecolor=BLUE,
                edgecolor=NAVY,
                lw=0.9,
            )
        )
        ax.plot(
            [
                x0 + (cx - 0.06) * width,
                x0 + (cx + 0.06) * width,
            ],
            [
                y0 + (cy - 0.07) * height,
                y0 + (cy + 0.07) * height,
            ],
            color="white",
            lw=0.8,
        )


def _format_heat_axis(ax: Axes, title: str, xmax: float) -> None:
    ax.axhline(727, color=GRAY, ls="--", lw=1.2)
    ax.axhline(850, color=GRAY, ls=":", lw=1.2)
    ax.axhspan(727, 850, color=GOLD, alpha=0.12)
    ax.text(0.12, 738, r"$A_\mathrm{c1}$", color=GRAY)
    ax.text(0.12, 860, r"$A_\mathrm{c3}$", color=GRAY)
    ax.set(
        xlim=(0, xmax),
        ylim=(0, 930),
        xlabel="時間（模式）",
        ylabel="温度 / °C",
        title=title,
    )
    ax.grid(alpha=0.20, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)


def dp_heat_treatment() -> None:
    """二種類の初期組織からDP鋼を得る経路を分けて示す。"""

    fig = plt.figure(figsize=(12.4, 6.2))
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=(1.0, 2.0),
        height_ratios=(1, 1),
        wspace=0.25,
        hspace=0.36,
    )
    temp_ax = fig.add_subplot(grid[:, 0])
    route_a = fig.add_subplot(grid[0, 1])
    route_b = fig.add_subplot(grid[1, 1])

    _format_heat_axis(temp_ax, "温度履歴", 6.0)
    temp_ax.plot(
        [0.0, 1.1, 3.2, 3.8, 5.5],
        [20, 790, 790, 20, 20],
        color=BLUE,
        lw=3,
    )
    temp_ax.text(2.15, 810, "二相域焼なまし\nα + γ", ha="center", weight="bold")
    temp_ax.annotate(
        "急冷：γ → M",
        xy=(3.55, 350),
        xytext=(4.25, 520),
        arrowprops={"arrowstyle": "->", "color": BLUE},
        color=BLUE,
        weight="bold",
    )
    temp_ax.text(
        3.0,
        105,
        "保持温度・時間で\nγ量と最終M量を調整",
        ha="center",
        color=GRAY,
    )

    for ax, title in [
        (route_a, "（a）初期組織：フェライト + パーライト"),
        (route_b, "（b）初期組織：マルテンサイト単相"),
    ]:
        ax.set(xlim=(0, 3.8), ylim=(0, 1.40))
        ax.axis("off")
        ax.set_title(title, loc="left", weight="bold", fontsize=11)
        for x0, label in [(0.12, "初期"), (1.49, "二相域保持"), (2.86, "急冷後")]:
            ax.text(x0 + 0.40, 1.20, label, ha="center", color=GRAY)

    y0 = 0.36
    _draw_ferrite_pearlite(route_a, 0.12, y0)
    _draw_alpha_gamma(route_a, 1.49, y0)
    _draw_alpha_martensite(route_a, 2.86, y0)
    _arrow_between(
        route_a,
        (0.95, 0.62),
        (1.43, 0.62),
        "P溶解\n+ 逆変態",
        1.00,
    )
    _arrow_between(route_a, (2.32, 0.62), (2.80, 0.62), "γ → M", 0.82)
    route_a.text(0.52, 0.18, "α + P", ha="center", weight="bold")
    route_a.text(1.89, 0.18, "α + γ", ha="center", weight="bold")
    route_a.text(3.26, 0.18, "α + M", ha="center", weight="bold")

    _draw_martensite(route_b, 0.12, y0)
    _draw_alpha_gamma(route_b, 1.49, y0)
    _draw_alpha_martensite(route_b, 2.86, y0)
    _arrow_between(
        route_b,
        (0.95, 0.62),
        (1.43, 0.62),
        "焼戻し・C再分配\n+ 逆変態",
        1.00,
    )
    _arrow_between(route_b, (2.32, 0.62), (2.80, 0.62), "γ → M", 0.82)
    route_b.text(0.52, 0.18, "M", ha="center", weight="bold")
    route_b.text(1.89, 0.18, "α + γ", ha="center", weight="bold")
    route_b.text(3.26, 0.18, "α + M", ha="center", weight="bold")

    fig.suptitle(
        "DP鋼：二相域で作ったγだけを急冷でMにする（模式図）",
        fontsize=15,
        weight="bold",
    )
    fig.text(
        0.5,
        0.012,
        "α：フェライト、P：パーライト、γ：オーステナイト、M：マルテンサイト。温度・時間・相分率は定性的。",
        ha="center",
        color=GRAY,
    )
    fig.subplots_adjust(
        left=0.06,
        right=0.985,
        bottom=0.14,
        top=0.83,
        wspace=0.24,
        hspace=0.52,
    )
    finish(fig, "dp-heat-treatment.svg")


def _draw_alpha_bainite_gamma(
    ax: Axes,
    x0: float,
    y0: float,
    width: float = 0.80,
    height: float = 0.52,
    retained: bool = False,
) -> None:
    _base_micro_box(ax, x0, y0, width, height, "#e8f5f2")
    for base_x, base_y in [(0.10, 0.16), (0.48, 0.50)]:
        for j in range(4):
            ax.plot(
                [
                    x0 + (base_x + 0.03 * j) * width,
                    x0 + (base_x + 0.28 + 0.03 * j) * width,
                ],
                [
                    y0 + base_y * height,
                    y0 + (base_y + 0.28) * height,
                ],
                color=ORANGE,
                lw=1.2,
            )
    gamma_color = PURPLE if retained else GOLD
    for cx, cy in [(0.35, 0.28), (0.76, 0.30), (0.30, 0.75), (0.78, 0.76)]:
        ax.add_patch(
            Ellipse(
                (x0 + cx * width, y0 + cy * height),
                0.15 * width,
                0.13 * height,
                facecolor=gamma_color,
                edgecolor=NAVY,
                lw=0.8,
            )
        )
    if retained:
        ax.plot(
            [x0 + 0.58 * width, x0 + 0.70 * width],
            [y0 + 0.15 * height, y0 + 0.42 * height],
            color=NAVY,
            lw=2.2,
        )


def trip_heat_treatment() -> None:
    """TRIP鋼の熱履歴と残留γ形成過程を示す。"""

    fig = plt.figure(figsize=(12.6, 5.5))
    grid = fig.add_gridspec(1, 2, width_ratios=(1.0, 2.25), wspace=0.25)
    temp_ax = fig.add_subplot(grid[0, 0])
    route_ax = fig.add_subplot(grid[0, 1])

    _format_heat_axis(temp_ax, "温度履歴", 8.0)
    temp_ax.axhspan(350, 480, color=TEAL, alpha=0.12)
    temp_ax.plot(
        [0.0, 1.0, 3.2, 3.8, 5.8, 6.4, 8.0],
        [20, 790, 790, 420, 420, 20, 20],
        color=PURPLE,
        lw=3,
    )
    temp_ax.text(2.15, 810, "二相域\nα + γ", ha="center", weight="bold")
    temp_ax.text(4.80, 445, "ベイナイト域保持", ha="center", weight="bold")
    temp_ax.annotate(
        "B生成時にCを\n未変態γへ排出",
        xy=(5.0, 420),
        xytext=(5.8, 610),
        arrowprops={"arrowstyle": "->", "color": PURPLE},
        color=PURPLE,
        ha="center",
    )
    temp_ax.text(
        4.6,
        110,
        "Si/Al：セメンタイト析出を抑制",
        ha="center",
        color=GRAY,
    )

    route_ax.set(xlim=(0, 5.25), ylim=(0, 1.50))
    route_ax.axis("off")
    route_ax.set_title("組織遷移", loc="left", weight="bold", fontsize=12)
    positions = [0.06, 1.36, 2.66, 3.96]
    stage_labels = ["初期", "二相域", "ベイナイト保持", "室温"]
    for x0, label in zip(positions, stage_labels, strict=True):
        route_ax.text(x0 + 0.40, 1.30, label, ha="center", color=GRAY)

    y0 = 0.55
    _draw_ferrite_pearlite(route_ax, positions[0], y0)
    _draw_alpha_gamma(route_ax, positions[1], y0)
    _draw_alpha_bainite_gamma(route_ax, positions[2], y0, retained=False)
    _draw_alpha_bainite_gamma(route_ax, positions[3], y0, retained=True)

    _arrow_between(
        route_ax,
        (positions[0] + 0.83, 0.81),
        (positions[1] - 0.05, 0.81),
        "P溶解",
        1.02,
    )
    _arrow_between(
        route_ax,
        (positions[1] + 0.83, 0.81),
        (positions[2] - 0.05, 0.81),
        "一部γ → B\nC → 残りのγ",
        1.05,
    )
    _arrow_between(
        route_ax,
        (positions[2] + 0.83, 0.81),
        (positions[3] - 0.05, 0.81),
        "C濃化γを\n室温まで保持",
        1.05,
    )

    captions = [
        "α + P",
        "α + γ",
        r"α + B + γ$_{\mathrm{C-rich}}$",
        r"α + B + γ$_\mathrm{R}$（+M）",
    ]
    for x0, caption in zip(positions, captions, strict=True):
        route_ax.text(x0 + 0.40, 0.36, caption, ha="center", weight="bold")
    route_ax.text(
        positions[3] + 0.40,
        0.15,
        "変形中：γR → M\n加工硬化を維持してくびれを遅らせる",
        ha="center",
        color=PURPLE,
        weight="bold",
    )

    fig.suptitle(
        "TRIP鋼：Cを未変態γへ濃化して残留させる（模式図）",
        fontsize=15,
        weight="bold",
    )
    fig.text(
        0.5,
        0.012,
        "α：フェライト、P：パーライト、B：ベイナイト、γR：残留オーステナイト、M：マルテンサイト。温度・時間・相分率は定性的。",
        ha="center",
        color=GRAY,
    )
    fig.subplots_adjust(
        left=0.065,
        right=0.985,
        bottom=0.17,
        top=0.82,
        wspace=0.25,
    )
    finish(fig, "trip-heat-treatment.svg")


def main() -> None:
    cct_shifts()
    martensite_hierarchy()
    dp_heat_treatment()
    trip_heat_treatment()


if __name__ == "__main__":
    main()
