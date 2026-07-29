"""材料力学IIの過去問解説に用いる模式SVGを生成する。

添付された低解像度画像を拡大・トレースするのではなく、問題文の幾何、
Euler--Bernoulli梁理論、転位の解析式、結晶方位から再作図する。
応力--ひずみ曲線など実験値を用いない図には、図中にも「模式図」と明記する。
"""

from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/codex-mpl-materials-mechanics-ii")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle
from scipy.interpolate import PchipInterpolator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "材料力学II"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#17324d"
BLUE = "#457b9d"
TEAL = "#2a9d8f"
GOLD = "#e9c46a"
ORANGE = "#f4a261"
RED = "#e76f51"
PURPLE = "#6c5ce7"
LIGHT = "#f7f4ed"
PALE_BLUE = "#eef5f8"
PALE_GOLD = "#fbf3d5"
PALE_RED = "#fce8e5"
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
        "svg.hashsalt": "materials-mechanics-ii-2026-07-29",
    }
)


def finish(fig: plt.Figure, name: str) -> Path:
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
    return output_path


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = NAVY,
    width: float = 2.0,
    scale: float = 14,
    style: str = "-|>",
    zorder: int = 8,
    linestyle: str = "-",
) -> FancyArrowPatch:
    """共通スタイルの矢印を追加する。"""

    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=scale,
        color=color,
        lw=width,
        linestyle=linestyle,
        zorder=zorder,
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(patch)
    return patch


def dimension(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    *,
    color: str = GRAY,
    label_offset: tuple[float, float] = (0.0, 0.0),
) -> None:
    """両矢印の寸法線とラベルを追加する。"""

    arrow(
        ax,
        start,
        end,
        color=color,
        width=1.4,
        scale=11,
        style="<->",
        zorder=6,
    )
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ax.text(
        midpoint[0] + label_offset[0],
        midpoint[1] + label_offset[1],
        label,
        ha="center",
        va="center",
        color=color,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2},
        zorder=9,
    )


def _projected_cube(
    ax: plt.Axes,
    *,
    highlighted_face: int,
    face_index: int,
) -> None:
    """正の座標面を強調した投影立方体を描く。"""

    origin = np.array([1.55, 1.12])
    basis = {
        1: np.array([1.75, 0.0]),
        2: np.array([0.0, 1.65]),
        3: np.array([-0.78, -0.58]),
    }

    def point(x1: float, x2: float, x3: float) -> np.ndarray:
        return origin + x1 * basis[1] + x2 * basis[2] + x3 * basis[3]

    faces = {
        1: np.array(
            [
                point(1, 0, 0),
                point(1, 1, 0),
                point(1, 1, 1),
                point(1, 0, 1),
            ]
        ),
        2: np.array(
            [
                point(0, 1, 0),
                point(1, 1, 0),
                point(1, 1, 1),
                point(0, 1, 1),
            ]
        ),
        3: np.array(
            [
                point(0, 0, 0),
                point(1, 0, 0),
                point(1, 1, 0),
                point(0, 1, 0),
            ]
        ),
    }

    draw_order = tuple(
        index for index in (3, 2, 1) if index != highlighted_face
    ) + (highlighted_face,)
    base_colors = {1: "#e5edf2", 2: "#f1f5f7", 3: "#fafafa"}
    for index in draw_order:
        selected = index == highlighted_face
        polygon = Polygon(
            faces[index],
            closed=True,
            facecolor=PALE_GOLD if selected else base_colors[index],
            edgecolor=GOLD if selected else NAVY,
            linewidth=2.3 if selected else 1.6,
            zorder=9 if selected else 2 + index,
        )
        ax.add_patch(polygon)

    center = faces[highlighted_face].mean(axis=0)
    direction_colors = {1: RED, 2: TEAL, 3: BLUE}
    for direction_index in (1, 2, 3):
        vector = basis[direction_index]
        vector = vector / np.linalg.norm(vector)
        endpoint = center + 0.60 * vector
        arrow(
            ax,
            tuple(center),
            tuple(endpoint),
            color=direction_colors[direction_index],
            width=2.4,
            scale=14,
            zorder=12,
        )
        text_offset = {
            1: np.array([0.16, 0.04]),
            2: np.array([0.03, 0.08]),
            3: np.array([-0.17, -0.10]),
        }[direction_index]
        ax.text(
            *(endpoint + text_offset),
            rf"$\sigma_{{{face_index}{direction_index}}}$",
            color=direction_colors[direction_index],
            weight="bold",
            ha="center",
            va="center",
            fontsize=11,
            zorder=14,
        )

    triad_origin = np.array([0.63, 0.36])
    for index, label in ((1, r"$x_1$"), (2, r"$x_2$"), (3, r"$x_3$")):
        vector = basis[index] / np.linalg.norm(basis[index])
        endpoint = triad_origin + 0.52 * vector
        arrow(
            ax,
            tuple(triad_origin),
            tuple(endpoint),
            color=direction_colors[index],
            width=1.6,
            scale=10,
        )
        ax.text(
            *(endpoint + 0.10 * vector),
            label,
            color=direction_colors[index],
            ha="center",
            va="center",
            fontsize=9,
        )

    ax.set_title(
        rf"法線が $+x_{face_index}$ の面",
        fontsize=12,
        weight="bold",
        pad=8,
    )
    ax.set(xlim=(0.18, 4.25), ylim=(0.02, 3.27), aspect="equal")
    ax.axis("off")


def stress_cube_components() -> Path:
    """各座標面に働く応力成分の向きを示す。"""

    # 3面を横一列にするとスマートフォンで添字が読めなくなるため、
    # 縦に並べて各パネルの表示幅を確保する。
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 11.2))
    for face_index, ax in enumerate(axes, start=1):
        _projected_cube(
            ax,
            highlighted_face=face_index,
            face_index=face_index,
        )

    fig.suptitle(
        "応力立方体：面の向きと力の向きを二つの添字で表す",
        fontsize=16,
        weight="bold",
        y=0.99,
    )
    fig.text(
        0.5,
        0.018,
        r"本問の規約：$\sigma_{ij}$ の第1添字 $i$ は面の法線方向、第2添字 $j$ は力の方向。"
        r"反対側の面にはつり合う逆向きの応力が働く。",
        ha="center",
        color=GRAY,
        fontsize=9.5,
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.965), h_pad=0.6)
    return finish(fig, "stress-cube-components.svg")


def cantilever_problem() -> Path:
    """先端集中荷重を受ける片持ち梁の問題配置を描く。"""

    fig, ax = plt.subplots(figsize=(11.2, 4.4))
    wall_x = 0.08
    beam_y = 0.63
    beam_start = 0.12
    beam_end = 0.90

    ax.plot(
        [wall_x, wall_x],
        [0.27, 0.90],
        color=NAVY,
        lw=4.0,
        solid_capstyle="butt",
    )
    for y in np.linspace(0.30, 0.88, 10):
        ax.plot(
            [wall_x - 0.045, wall_x],
            [y - 0.045, y],
            color=GRAY,
            lw=1.2,
        )

    ax.add_patch(
        Rectangle(
            (beam_start, beam_y - 0.055),
            beam_end - beam_start,
            0.11,
            facecolor=PALE_BLUE,
            edgecolor=NAVY,
            linewidth=2.2,
            zorder=3,
        )
    )
    arrow(
        ax,
        (beam_end, 0.90),
        (beam_end, beam_y + 0.07),
        color=RED,
        width=3.0,
        scale=18,
    )
    ax.text(
        beam_end + 0.018,
        0.92,
        r"$P$",
        color=RED,
        fontsize=16,
        weight="bold",
        ha="left",
        va="center",
    )

    ax.plot(
        [beam_start, beam_start],
        [0.20, beam_y - 0.075],
        color=GRID,
        lw=1.2,
    )
    ax.plot(
        [beam_end, beam_end],
        [0.20, beam_y - 0.075],
        color=GRID,
        lw=1.2,
    )
    dimension(
        ax,
        (beam_start, 0.25),
        (beam_end, 0.25),
        r"$L$",
        label_offset=(0, -0.02),
    )

    arrow(ax, (0.94, 0.45), (1.04, 0.45), color=NAVY, width=1.8, scale=11)
    ax.text(1.055, 0.45, r"$x$", ha="left", va="center", fontsize=11)
    arrow(ax, (0.94, 0.45), (0.94, 0.33), color=BLUE, width=1.8, scale=11)
    ax.text(0.94, 0.29, r"$z$", ha="center", va="top", fontsize=11, color=BLUE)

    ax.text(
        0.51,
        0.74,
        r"一様な $E,\ I$",
        ha="center",
        color=BLUE,
        fontsize=11,
        weight="bold",
    )
    ax.text(
        0.51,
        0.08,
        "固定端：変位と回転が0　／　自由端：集中荷重",
        ha="center",
        color=GRAY,
        fontsize=9.5,
    )
    ax.set(xlim=(0, 1.11), ylim=(0.0, 1.02), aspect="auto")
    ax.axis("off")
    fig.suptitle(
        "先端集中荷重を受ける片持ち梁",
        fontsize=15,
        weight="bold",
        y=0.96,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    return finish(fig, "cantilever-problem.svg")


def _style_distribution_axis(
    ax: plt.Axes,
    ylabel: str,
    *,
    zero_line: bool = True,
) -> None:
    """せん断力・曲げモーメント・たわみ図の共通体裁。"""

    if zero_line:
        ax.axhline(0, color=NAVY, lw=1.0)
    ax.grid(axis="x", color=GRID, lw=0.7, alpha=0.7)
    ax.set_xlim(0, 1)
    ax.set_ylabel(ylabel, rotation=0, labelpad=31, va="center", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)


def cantilever_solution() -> Path:
    """片持ち梁のV・M・たわみを無次元表示する。"""

    xi = np.linspace(0, 1, 500)
    shear = -np.ones_like(xi)
    moment = -(1 - xi)
    deflection = -(xi**2 * (3 - xi) / 2)

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10.6, 8.2),
        sharex=True,
        gridspec_kw={"hspace": 0.30},
    )

    axes[0].plot(xi, shear, color=RED, lw=3.0)
    axes[0].plot([0, 0], [0, -1], color=RED, lw=3.0)
    axes[0].plot([1, 1], [-1, 0], color=RED, lw=3.0)
    axes[0].fill_between(xi, 0, shear, color=RED, alpha=0.15)
    _style_distribution_axis(axes[0], r"$V/P$")
    axes[0].set_ylim(-1.35, 0.30)
    axes[0].text(0.50, -0.88, r"$V=-P$", color=RED, weight="bold", ha="center")

    axes[1].plot(xi, moment, color=BLUE, lw=3.0)
    axes[1].fill_between(xi, 0, moment, color=BLUE, alpha=0.15)
    _style_distribution_axis(axes[1], r"$M/(PL)$")
    axes[1].set_ylim(-1.18, 0.22)
    axes[1].text(
        0.24,
        -0.74,
        r"$M=-P(L-x)$",
        color=BLUE,
        weight="bold",
        ha="center",
    )

    axes[2].plot(xi, deflection, color=TEAL, lw=3.0)
    axes[2].fill_between(xi, 0, deflection, color=TEAL, alpha=0.14)
    _style_distribution_axis(axes[2], r"$w/\delta_L$")
    axes[2].set_ylim(-1.20, 0.17)
    axes[2].scatter([1], [-1], color=TEAL, s=50, zorder=5)
    axes[2].annotate(
        r"$\delta_L=\dfrac{PL^3}{3EI}$",
        xy=(1, -1),
        xytext=(0.64, -0.64),
        arrowprops={"arrowstyle": "->", "color": TEAL},
        color=TEAL,
        weight="bold",
        ha="center",
    )
    axes[2].set_xlabel(r"無次元位置 $x/L$")
    axes[2].set_xticks([0, 0.25, 0.50, 0.75, 1.0])
    axes[2].set_xticklabels(["0", "0.25", "0.50", "0.75", "1"])

    for ax in axes:
        ax.axvline(0, color=GRAY, lw=1.0, linestyle=":")
        ax.axvline(1, color=GRAY, lw=1.0, linestyle=":")

    fig.suptitle(
        "片持ち梁のせん断力・曲げモーメント・たわみ",
        fontsize=16,
        weight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.018,
        "符号規約：図の下向き荷重に対し、負のせん断力・負の曲げモーメント・下向きたわみを負で表示。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.subplots_adjust(left=0.13, right=0.97, top=0.90, bottom=0.12, hspace=0.32)
    return finish(fig, "cantilever-vmd-solution.svg")


def _support(ax: plt.Axes, x: float, y: float) -> None:
    """単純支持の三角記号を描く。"""

    triangle = Polygon(
        [[x, y], [x - 0.035, y - 0.09], [x + 0.035, y - 0.09]],
        closed=True,
        facecolor="white",
        edgecolor=NAVY,
        linewidth=1.8,
        zorder=5,
    )
    ax.add_patch(triangle)
    ax.plot([x - 0.055, x + 0.055], [y - 0.095, y - 0.095], color=NAVY, lw=1.5)


def rolling_roll_problem() -> Path:
    """中央幅aに等分布荷重を受ける単純支持ロールを描く。"""

    fig, ax = plt.subplots(figsize=(12.0, 4.9))
    left = 0.08
    right = 0.80
    y = 0.55
    load_left = 0.29
    load_right = 0.59

    ax.add_patch(
        Rectangle(
            (left, y - 0.045),
            right - left,
            0.09,
            facecolor=PALE_BLUE,
            edgecolor=NAVY,
            linewidth=2.2,
            zorder=3,
        )
    )
    _support(ax, left, y - 0.052)
    _support(ax, right, y - 0.052)

    for x in np.linspace(load_left, load_right, 10):
        arrow(
            ax,
            (x, 0.86),
            (x, y + 0.06),
            color=RED,
            width=1.9,
            scale=11,
        )
    ax.plot([load_left, load_right], [0.86, 0.86], color=RED, lw=2.0)
    ax.text(
        (load_left + load_right) / 2,
        0.91,
        r"等分布線荷重 $q$",
        color=RED,
        ha="center",
        weight="bold",
        fontsize=11,
    )

    for x in (left, right):
        ax.plot([x, x], [0.18, y - 0.13], color=GRID, lw=1.1)
    dimension(ax, (left, 0.22), (right, 0.22), r"$l$")

    for x in (load_left, load_right):
        ax.plot([x, x], [0.34, y - 0.07], color=GRID, lw=1.1)
    dimension(
        ax,
        (load_left, 0.37),
        (load_right, 0.37),
        r"$a$",
        label_offset=(0, -0.01),
    )

    circle_center = (0.99, 0.57)
    radius_y = 0.13
    ax.add_patch(
        Ellipse(
            circle_center,
            width=0.115,
            height=2 * radius_y,
            facecolor=LIGHT,
            edgecolor=NAVY,
            linewidth=2.0,
        )
    )
    dimension(
        ax,
        (circle_center[0], circle_center[1] - radius_y),
        (circle_center[0], circle_center[1] + radius_y),
        r"$d$",
        color=BLUE,
        label_offset=(0.045, 0),
    )
    ax.text(
        circle_center[0],
        0.35,
        "ロール断面",
        color=GRAY,
        ha="center",
        fontsize=9,
    )

    ax.text(
        0.44,
        0.08,
        r"荷重区間：$(l-a)/2\leq x\leq(l+a)/2$",
        ha="center",
        color=GRAY,
        fontsize=9.5,
    )
    ax.set(xlim=(0.0, 1.15), ylim=(0.0, 1.02))
    ax.axis("off")
    fig.suptitle(
        "中央の幅 $a$ に等分布荷重を受ける圧延ロールの梁モデル",
        fontsize=15,
        weight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    return finish(fig, "rolling-roll-problem.svg")


def rolling_roll_solution() -> Path:
    """中央部分等分布荷重のV・M・たわみを無次元表示する。"""

    alpha = 0.45
    xi = np.linspace(0, 1, 1001)
    c = (1 - alpha) / 2
    e = (1 + alpha) / 2

    shear = np.where(
        xi < c,
        0.5,
        np.where(xi <= e, 0.5 - (xi - c) / alpha, -0.5),
    )
    moment = np.where(
        xi < c,
        xi / 2,
        np.where(
            xi <= e,
            xi / 2 - (xi - c) ** 2 / (2 * alpha),
            (1 - xi) / 2,
        ),
    )

    reaction = alpha / 2
    c1 = -(
        reaction / 6
        - (1 - c) ** 4 / 24
        + (1 - e) ** 4 / 24
    )
    macaulay_c = np.maximum(xi - c, 0)
    macaulay_e = np.maximum(xi - e, 0)
    elastic_curve = (
        reaction * xi**3 / 6
        - macaulay_c**4 / 24
        + macaulay_e**4 / 24
        + c1 * xi
    )
    downward_deflection = -elastic_curve
    delta_max = alpha * (8 - 4 * alpha**2 + alpha**3) / 384
    deflection = -downward_deflection / delta_max

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10.8, 8.7),
        sharex=True,
        gridspec_kw={"hspace": 0.30},
    )

    axes[0].plot(xi, shear, color=RED, lw=3.0)
    axes[0].plot([0, 0], [0, 0.5], color=RED, lw=3.0)
    axes[0].plot([1, 1], [-0.5, 0], color=RED, lw=3.0)
    axes[0].fill_between(xi, 0, shear, color=RED, alpha=0.14)
    _style_distribution_axis(axes[0], r"$V/(qa)$")
    axes[0].set_ylim(-0.70, 0.70)
    axes[0].set_yticks([-0.5, 0, 0.5])

    axes[1].plot(xi, moment, color=BLUE, lw=3.0)
    axes[1].fill_between(xi, 0, moment, color=BLUE, alpha=0.14)
    _style_distribution_axis(axes[1], r"$M/(qal)$")
    axes[1].set_ylim(-0.025, max(moment) * 1.32)
    axes[1].scatter([0.5], [moment[len(moment) // 2]], color=BLUE, s=42, zorder=5)

    axes[2].plot(xi, deflection, color=TEAL, lw=3.0)
    axes[2].fill_between(xi, 0, deflection, color=TEAL, alpha=0.14)
    _style_distribution_axis(axes[2], r"$w/\delta_{\max}$")
    axes[2].set_ylim(-1.18, 0.13)
    axes[2].scatter([0.5], [-1], color=TEAL, s=48, zorder=5)
    axes[2].set_xlabel(r"無次元位置 $x/l$")

    for ax in axes:
        for boundary in (c, e):
            ax.axvline(boundary, color=GRAY, lw=1.0, linestyle=":")
        ax.text(
            c,
            ax.get_ylim()[1] * 0.86,
            r"$(l-a)/2$",
            ha="right",
            va="top",
            color=GRAY,
            fontsize=8.5,
        )
        ax.text(
            e,
            ax.get_ylim()[1] * 0.86,
            r"$(l+a)/2$",
            ha="left",
            va="top",
            color=GRAY,
            fontsize=8.5,
        )

    axes[2].annotate(
        r"$\delta_{\max}="
        r"\dfrac{qa(8l^3-4la^2+a^3)}{384EI}$",
        xy=(0.5, -1),
        xytext=(0.69, -0.60),
        arrowprops={"arrowstyle": "->", "color": TEAL},
        color=TEAL,
        weight="bold",
        ha="center",
    )
    axes[1].text(
        0.02,
        0.84,
        r"$I=\pi d^4/64$",
        transform=axes[1].transAxes,
        color=BLUE,
        weight="bold",
        fontsize=10.5,
    )

    fig.suptitle(
        "中央部分等分布荷重を受ける単純支持ロール",
        fontsize=16,
        weight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.020,
        r"形状例は $a/l=0.45$。曲線は梁の解析式から描いた無次元図であり、実験データではない。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.subplots_adjust(left=0.13, right=0.97, top=0.90, bottom=0.13, hspace=0.32)
    return finish(fig, "rolling-roll-vmd-solution.svg")


def screw_dislocation_geometry() -> Path:
    """時計回り角度とx3方向変位を示すらせん転位の模式図。"""

    fig, (ax_cross, ax_unwrap) = plt.subplots(1, 2, figsize=(12.0, 5.5))

    ax = ax_cross
    ax.add_patch(
        Circle(
            (0, 0),
            1.05,
            facecolor=PALE_BLUE,
            edgecolor=BLUE,
            linewidth=2.0,
            alpha=0.9,
        )
    )
    ax.add_patch(Circle((0, 0), 0.12, facecolor=NAVY, edgecolor=NAVY))
    arrow(ax, (-1.28, 0), (1.35, 0), color=RED, width=1.7, scale=11)
    arrow(ax, (0, -1.25), (0, 1.32), color=TEAL, width=1.7, scale=11)
    ax.text(1.38, 0, r"$x_1$", color=RED, ha="left", va="center", fontsize=11)
    ax.text(0, 1.35, r"$x_2$", color=TEAL, ha="center", va="bottom", fontsize=11)

    theta = np.linspace(0, 1.33 * math.pi, 220)
    radius = 0.72
    arc_x = radius * np.cos(theta)
    arc_y = radius * np.sin(theta)
    ax.plot(arc_x, arc_y, color=PURPLE, lw=3.0)
    tangent = np.array(
        [
            -math.sin(theta[-1]),
            math.cos(theta[-1]),
        ]
    )
    endpoint = np.array([arc_x[-1], arc_y[-1]])
    arrow(
        ax,
        tuple(endpoint - 0.08 * tangent),
        tuple(endpoint + 0.02 * tangent),
        color=PURPLE,
        width=2.4,
        scale=12,
    )
    radial_theta = 0.77
    radial_end = (0.93 * math.cos(radial_theta), 0.93 * math.sin(radial_theta))
    ax.plot([0, radial_end[0]], [0, radial_end[1]], color=GRAY, lw=1.5)
    ax.text(
        0.49 * math.cos(radial_theta) + 0.05,
        0.49 * math.sin(radial_theta),
        r"$r$",
        color=GRAY,
        fontsize=11,
    )
    ax.text(-0.50, 0.42, r"$\theta$", color=PURPLE, fontsize=14, weight="bold")
    ax.text(
        0,
        -1.45,
        "紙面上の時計回りを $\\theta>0$ と定義",
        ha="center",
        color=PURPLE,
        fontsize=9.5,
    )
    ax.text(
        0.15,
        0.10,
        "転位芯",
        color="white",
        fontsize=8,
        ha="left",
        va="bottom",
        bbox={"facecolor": NAVY, "edgecolor": "none", "pad": 2},
    )
    ax.set_title(r"$x_1$--$x_2$ 断面", weight="bold", fontsize=12)
    ax.set(xlim=(-1.55, 1.55), ylim=(1.62, -1.62), aspect="equal")
    ax.axis("off")

    ax = ax_unwrap
    ax.add_patch(
        Rectangle(
            (0.08, 0.16),
            0.80,
            0.66,
            facecolor=LIGHT,
            edgecolor=GRID,
            linewidth=1.5,
        )
    )
    arrow(ax, (0.13, 0.23), (0.82, 0.23), color=PURPLE, width=1.8, scale=11)
    arrow(ax, (0.13, 0.23), (0.13, 0.78), color=BLUE, width=1.8, scale=11)
    ax.text(0.84, 0.23, r"$\theta$", color=PURPLE, ha="left", va="center")
    ax.text(0.13, 0.81, r"$x_3$", color=BLUE, ha="center", va="bottom")
    ax.plot([0.13, 0.78], [0.23, 0.70], color=GOLD, lw=4.0, solid_capstyle="round")
    ax.scatter([0.13, 0.78], [0.23, 0.70], color=[NAVY, GOLD], s=55, zorder=6)
    ax.text(0.13, 0.17, r"$0$", ha="center", color=GRAY)
    ax.text(0.78, 0.17, r"$2\pi$", ha="center", color=PURPLE, weight="bold")
    dimension(
        ax,
        (0.91, 0.23),
        (0.91, 0.70),
        r"$b$",
        color=BLUE,
        label_offset=(0.05, 0),
    )
    ax.text(
        0.50,
        0.93,
        r"1周すると $x_3$ 方向に $b$ だけずれる",
        ha="center",
        va="center",
        color=NAVY,
        fontsize=11,
        weight="bold",
    )
    ax.text(
        0.50,
        0.07,
        "円周方向をほどいた模式表示（縮尺なし）",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    ax.set_title("多価変位のイメージ", weight="bold", fontsize=12)
    ax.set(xlim=(0, 1.02), ylim=(0, 1.02), aspect="equal")
    ax.axis("off")

    fig.suptitle(
        "らせん転位：角度の一周とBurgers vector",
        fontsize=16,
        weight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return finish(fig, "screw-dislocation-geometry.svg")


def _edge_symbol(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    *,
    color: str,
) -> None:
    """刃状転位を簡潔なT記号で描く。"""

    ax.plot([x - 0.15, x + 0.15], [y, y], color=color, lw=5.0, solid_capstyle="butt")
    ax.plot([x, x], [y, y + 0.20], color=color, lw=5.0, solid_capstyle="butt")
    ax.text(x, y + 0.28, label, color=color, ha="center", weight="bold", fontsize=11)


def edge_dislocation_pair() -> Path:
    """x2=d上を滑る二本の平行刃状転位を描く。"""

    fig, ax = plt.subplots(figsize=(9.4, 6.0))
    origin = np.array([0.0, 0.0])
    second = np.array([1.55, 1.25])

    arrow(ax, (-0.35, 0), (3.10, 0), color=NAVY, width=1.9, scale=12)
    arrow(ax, (0, -0.30), (0, 2.35), color=NAVY, width=1.9, scale=12)
    ax.text(3.15, 0, r"$x_1$", ha="left", va="center", fontsize=12)
    ax.text(0, 2.40, r"$x_2$", ha="center", va="bottom", fontsize=12)

    ax.plot(
        [-0.05, 3.0],
        [second[1], second[1]],
        color=GRAY,
        lw=1.5,
        linestyle="--",
    )
    ax.text(
        2.95,
        second[1] + 0.08,
        r"滑り面 $x_2=d$",
        color=GRAY,
        ha="right",
        va="bottom",
    )
    ax.plot(
        [second[0], second[0]],
        [0, second[1]],
        color=GRID,
        lw=1.3,
        linestyle=":",
    )
    dimension(
        ax,
        (-0.20, 0),
        (-0.20, second[1]),
        r"$d$",
        color=BLUE,
        label_offset=(-0.08, 0),
    )
    dimension(
        ax,
        (0, -0.18),
        (second[0], -0.18),
        r"$x_1$",
        color=PURPLE,
        label_offset=(0, -0.06),
    )

    _edge_symbol(ax, *origin, "転位 I", color=BLUE)
    _edge_symbol(ax, *second, "転位 II", color=RED)
    arrow(
        ax,
        (second[0] - 0.48, second[1] - 0.20),
        (second[0] - 0.22, second[1] - 0.20),
        color=PURPLE,
        width=1.8,
        scale=10,
        style="<->",
    )
    arrow(
        ax,
        (second[0] + 0.22, second[1] - 0.20),
        (second[0] + 0.48, second[1] - 0.20),
        color=PURPLE,
        width=1.8,
        scale=10,
        style="<->",
    )
    ax.text(
        second[0],
        second[1] - 0.34,
        r"$x_1$方向だけ摩擦なく滑る",
        color=PURPLE,
        ha="center",
        fontsize=9.5,
    )

    arrow(ax, (0.10, 0.38), (0.67, 0.38), color=BLUE, width=2.1, scale=12)
    ax.text(0.38, 0.47, r"$\boldsymbol{b}_{I}\parallel+x_1$", color=BLUE, ha="center")
    arrow(
        ax,
        (1.70, 1.70),
        (2.27, 1.70),
        color=RED,
        width=2.1,
        scale=12,
    )
    ax.text(
        1.98,
        1.79,
        r"$\boldsymbol{b}_{II}\parallel\pm x_1$",
        color=RED,
        ha="center",
    )

    ax.add_patch(Circle((2.72, 1.82), 0.075, facecolor="white", edgecolor=NAVY, lw=1.5))
    ax.scatter([2.72], [1.82], color=NAVY, s=18, zorder=6)
    ax.text(
        2.72,
        2.02,
        r"$\boldsymbol{t}\parallel+x_3$（紙面手前）",
        ha="center",
        fontsize=9.5,
    )

    ax.text(
        1.55,
        2.25,
        r"実距離は $\sqrt{x_1^2+d^2}$。$d$ は二つの滑り面の間隔。",
        ha="center",
        color=GRAY,
        fontsize=9.5,
    )
    ax.set(xlim=(-0.45, 3.25), ylim=(-0.45, 2.55), aspect="equal")
    ax.axis("off")
    fig.suptitle(
        "平行な二本の刃状転位と滑り拘束",
        fontsize=16,
        weight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    return finish(fig, "edge-dislocation-pair.svg")


def edge_dislocation_force() -> Path:
    """刃状転位IIの無次元滑り力と安定点を示す。"""

    xi = np.linspace(-4.0, 4.0, 1601)
    force_same = xi * (xi**2 - 1) / (xi**2 + 1) ** 2
    force_opposite = -force_same

    # 安定点の注記をスマートフォンでも読めるよう、二条件を縦に並べる。
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(7.2, 9.8),
        sharex=True,
        sharey=True,
    )
    configurations = (
        (
            axes[0],
            force_same,
            "同符号のBurgers vector",
            TEAL,
            [0],
            [-1, 1],
        ),
        (
            axes[1],
            force_opposite,
            "異符号のBurgers vector",
            RED,
            [-1, 1],
            [0],
        ),
    )

    for ax, values, title, color, stable_points, unstable_points in configurations:
        ax.axhline(0, color=NAVY, lw=1.0)
        ax.axvline(0, color=GRID, lw=0.9)
        ax.plot(xi, values, color=color, lw=3.0)
        ax.fill_between(xi, 0, values, color=color, alpha=0.10)
        ax.scatter(
            stable_points,
            np.zeros(len(stable_points)),
            s=85,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=6,
            label="安定",
        )
        ax.scatter(
            unstable_points,
            np.zeros(len(unstable_points)),
            s=85,
            facecolor="white",
            edgecolor=color,
            linewidth=2.2,
            zorder=6,
            label="不安定",
        )
        for root in (-1, 0, 1):
            ax.axvline(root, color=GRID, lw=0.8, linestyle=":")
        for root in stable_points:
            ax.annotate(
                "安定",
                xy=(root, 0),
                xytext=(root, -0.25),
                arrowprops={"arrowstyle": "->", "color": color},
                color=color,
                ha="center",
                weight="bold",
            )
        for root in unstable_points:
            ax.annotate(
                "不安定",
                xy=(root, 0),
                xytext=(root, 0.24),
                arrowprops={"arrowstyle": "->", "color": color},
                color=color,
                ha="center",
                fontsize=9,
            )
        ax.set_title(title, weight="bold", fontsize=12)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-0.34, 0.34)
        ax.set_xticks([-4, -2, -1, 0, 1, 2, 4])
        ax.grid(color=GRID, lw=0.6, alpha=0.55)
        ax.set_xlabel(r"$\xi=x_1/d$")
        ax.legend(loc="lower right", frameon=True, fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel(
        r"$\dfrac{f_1}{\mu b_Ib_{II}/[2\pi(1-\nu)d]}$",
        fontsize=11,
    )
    fig.suptitle(
        r"滑り方向のPeach--Koehler力："
        r"$g(\xi)=\dfrac{\xi(\xi^2-1)}{(\xi^2+1)^2}$",
        fontsize=15,
        weight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.018,
        "解析式から描いた無次元図。安定性は点線上の滑り自由度について判定し、"
        "滑り面に垂直なclimb方向の力は拘束反力が受け持つ。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.tight_layout(rect=(0.02, 0.055, 0.99, 0.93), h_pad=1.2)
    return finish(fig, "edge-dislocation-force.svg")


def fcc_123_specimen() -> Path:
    """[123]引張と観察面(bar301)を示す試験片模式図。"""

    fig, ax = plt.subplots(figsize=(5.6, 7.8))
    front = np.array(
        [
            [1.10, 0.55],
            [3.30, 0.55],
            [3.24, 1.38],
            [2.90, 1.82],
            [2.90, 4.18],
            [3.24, 4.62],
            [3.30, 5.45],
            [1.10, 5.45],
            [1.16, 4.62],
            [1.50, 4.18],
            [1.50, 1.82],
            [1.16, 1.38],
        ]
    )
    offset = np.array([0.36, 0.23])
    side_indices = [1, 2, 3, 4, 5, 6]
    side = np.vstack(
        [
            front[side_indices],
            (front[side_indices] + offset)[::-1],
        ]
    )
    ax.add_patch(
        Polygon(
            side,
            closed=True,
            facecolor="#d9e8ee",
            edgecolor=NAVY,
            linewidth=1.8,
            zorder=1,
        )
    )
    ax.add_patch(
        Polygon(
            front,
            closed=True,
            facecolor=PALE_BLUE,
            edgecolor=NAVY,
            linewidth=2.4,
            zorder=3,
        )
    )
    ax.text(
        2.20,
        3.18,
        r"観察面 $(\bar{3}01)$",
        ha="center",
        color=BLUE,
        weight="bold",
        fontsize=11,
        zorder=5,
    )

    arrow(ax, (2.20, 5.58), (2.20, 6.15), color=RED, width=2.8, scale=16)
    arrow(ax, (2.20, 0.42), (2.20, -0.13), color=RED, width=2.8, scale=16)
    ax.text(
        2.42,
        5.93,
        r"引張軸 $[123]$",
        color=RED,
        weight="bold",
        fontsize=11,
        ha="left",
    )
    ax.text(
        2.20,
        0.90,
        "単結晶試験片",
        color=GRAY,
        fontsize=9.5,
        ha="center",
    )

    ax.text(
        2.20,
        -0.30,
        "試験片外形は模式表示。結晶方位を問題条件として用いる。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    ax.set(xlim=(0.45, 4.05), ylim=(-0.52, 6.38), aspect="equal")
    ax.axis("off")
    fig.suptitle(
        "FCC単結晶試験片の引張軸と観察面",
        fontsize=16,
        weight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    return finish(fig, "fcc-123-specimen.svg")


def fcc_slip_trace() -> Path:
    """観察面上の引張軸とすべり線の角度を示す。"""

    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    plane_left = 0.62
    plane_bottom = 0.86
    plane_width = 6.00
    plane_height = 4.78
    ax.add_patch(
        Rectangle(
            (plane_left, plane_bottom),
            plane_width,
            plane_height,
            facecolor=PALE_BLUE,
            edgecolor=BLUE,
            linewidth=2.0,
            zorder=1,
        )
    )
    ax.text(
        plane_left + 0.22,
        plane_bottom + plane_height - 0.24,
        r"観察面 $(\bar{3}01)$ を正面から見た模式図",
        color=BLUE,
        ha="left",
        va="top",
        weight="bold",
        fontsize=12,
    )

    center = np.array([3.58, 3.12])
    ax.plot(
        [center[0], center[0]],
        [plane_bottom + 0.48, plane_bottom + plane_height - 0.58],
        color=RED,
        lw=1.8,
        linestyle="--",
        zorder=3,
    )
    arrow(
        ax,
        (center[0], plane_bottom + plane_height - 1.03),
        (center[0], plane_bottom + plane_height - 0.42),
        color=RED,
        width=2.6,
        scale=14,
    )
    ax.text(
        center[0] + 0.18,
        plane_bottom + plane_height - 0.72,
        r"引張方向 $[123]$",
        color=RED,
        ha="left",
        va="center",
        weight="bold",
        fontsize=11,
    )

    line_angle = math.radians(25.4)
    direction = np.array([math.cos(line_angle), math.sin(line_angle)])
    for offset_y in np.linspace(-0.20, 0.20, 5):
        start = center + np.array([0, offset_y]) - 1.55 * direction
        end = center + np.array([0, offset_y]) + 1.55 * direction
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=PURPLE,
            lw=2.3,
            zorder=6,
        )
    ax.text(
        center[0] + 1.72,
        center[1] + 0.47,
        r"すべり線 $[1\bar{2}3]$",
        color=PURPLE,
        fontsize=10.5,
        ha="left",
        va="center",
        weight="bold",
    )

    arc = Arc(
        tuple(center),
        1.78,
        1.78,
        angle=0,
        theta1=25.4,
        theta2=90,
        color=GOLD,
        lw=2.8,
        zorder=8,
    )
    ax.add_patch(arc)
    ax.text(
        center[0] + 0.52,
        center[1] + 0.76,
        r"$\theta\simeq64.6^\circ$",
        color=GOLD,
        fontsize=13,
        weight="bold",
    )

    ax.text(
        plane_left + plane_width / 2,
        0.48,
        r"$[\bar{3}01]\cdot[123]=0$ より、引張軸は観察面内にある。",
        ha="center",
        color=GRAY,
        fontsize=10,
    )
    ax.set(xlim=(0.22, 7.05), ylim=(0.20, 6.18), aspect="equal")
    ax.axis("off")
    fig.suptitle(
        "観察面上の引張方向とすべり線",
        fontsize=16,
        weight="bold",
        y=0.97,
    )
    fig.text(
        0.5,
        0.018,
        "結晶方位から描いた模式図。角度は図から測らず、方向ベクトルの内積で求める。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.91))
    return finish(fig, "fcc-slip-trace.svg")


def single_polycrystal_stress_strain() -> Path:
    """単結晶と多結晶の典型的な公称応力--ひずみ曲線を比較する。"""

    single_x = np.array([0.0, 0.018, 0.026, 0.055, 0.11, 0.18, 0.245, 0.285])
    single_y = np.array([0.0, 0.33, 0.39, 0.42, 0.55, 0.73, 0.82, 0.76])
    poly_x = np.array([0.0, 0.018, 0.027, 0.050, 0.10, 0.16, 0.205, 0.235])
    poly_y = np.array([0.0, 0.35, 0.53, 0.64, 0.79, 0.94, 1.00, 0.91])

    single_xx = np.linspace(single_x.min(), single_x.max(), 500)
    poly_xx = np.linspace(poly_x.min(), poly_x.max(), 450)
    single_yy = PchipInterpolator(single_x, single_y)(single_xx)
    poly_yy = PchipInterpolator(poly_x, poly_y)(poly_xx)

    fig, ax = plt.subplots(figsize=(10.2, 6.2))
    ax.plot(single_xx, single_yy, color=BLUE, lw=3.2, label="単結晶")
    ax.plot(poly_xx, poly_yy, color=RED, lw=3.2, label="多結晶")
    ax.scatter(
        [single_x[2], poly_x[2]],
        [single_y[2], poly_y[2]],
        color=[BLUE, RED],
        s=62,
        zorder=6,
    )
    ax.scatter(
        [single_x[-1], poly_x[-1]],
        [single_y[-1], poly_y[-1]],
        color=[BLUE, RED],
        marker="X",
        s=75,
        zorder=6,
    )

    ax.annotate(
        "容易すべり後に\n多重すべり・加工硬化",
        xy=(0.085, 0.49),
        xytext=(0.125, 0.29),
        arrowprops={"arrowstyle": "->", "color": BLUE},
        color=BLUE,
        ha="center",
        fontsize=9.5,
    )
    ax.annotate(
        "粒界拘束・方位分布\n多重すべりで滑らかに硬化",
        xy=(0.090, 0.76),
        xytext=(0.16, 0.57),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        fontsize=9.5,
    )
    ax.text(
        0.031,
        0.33,
        "降伏は\n方位依存",
        color=BLUE,
        ha="left",
        va="top",
        fontsize=9,
    )
    ax.text(
        0.032,
        0.57,
        "平均的には\n高い降伏応力",
        color=RED,
        ha="left",
        va="bottom",
        fontsize=9,
    )
    ax.text(
        0.285,
        0.72,
        "破断",
        color=BLUE,
        ha="left",
        va="center",
        fontsize=9,
    )
    ax.text(
        0.235,
        0.94,
        "破断",
        color=RED,
        ha="left",
        va="center",
        fontsize=9,
    )

    ax.set_xlabel(r"公称ひずみ $\varepsilon$")
    ax.set_ylabel(r"公称応力 $\sigma$")
    ax.set(xlim=(0, 0.33), ylim=(0, 1.13))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", frameon=True, fontsize=10.5)
    ax.set_title(
        "単結晶と多結晶の典型的な応力--ひずみ応答",
        fontsize=15,
        weight="bold",
        pad=14,
    )
    fig.text(
        0.5,
        0.035,
        "教育用模式図・定量値ではない。同じ組成を想定した一般傾向であり、"
        "単結晶方位、多結晶の粒径・集合組織・熱処理により曲線の大小関係は変わり得る。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.tight_layout(rect=(0.04, 0.08, 0.98, 0.98))
    return finish(fig, "single-polycrystal-stress-strain.svg")


def cleavage_traction() -> Path:
    """単軸引張下の斜め結晶面と応力ベクトルの分解を描く。"""

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    specimen = Rectangle(
        (0.9, 0.75),
        6.2,
        3.0,
        facecolor=PALE_BLUE,
        edgecolor=NAVY,
        linewidth=2.0,
    )
    ax.add_patch(specimen)

    for y in (1.45, 2.25, 3.05):
        arrow(ax, (0.9, y), (0.18, y), color=RED, width=2.0, scale=13)
        arrow(ax, (7.1, y), (7.82, y), color=RED, width=2.0, scale=13)
    ax.text(0.28, 3.45, r"$\sigma\,\boldsymbol{e}_1$", color=RED, ha="left")
    ax.text(7.72, 3.45, r"$\sigma\,\boldsymbol{e}_1$", color=RED, ha="right")

    plane_start = np.array([3.05, 0.82])
    plane_end = np.array([4.55, 3.68])
    ax.plot(
        [plane_start[0], plane_end[0]],
        [plane_start[1], plane_end[1]],
        color=GOLD,
        linewidth=7,
        solid_capstyle="round",
        alpha=0.75,
        zorder=4,
    )
    midpoint = (plane_start + plane_end) / 2
    normal = np.array([plane_end[1] - plane_start[1], -(plane_end[0] - plane_start[0])])
    normal = normal / np.linalg.norm(normal)
    tangent = (plane_end - plane_start) / np.linalg.norm(plane_end - plane_start)

    normal_base = midpoint - 0.62 * tangent
    arrow(
        ax,
        tuple(normal_base),
        tuple(normal_base + 1.05 * normal),
        color=TEAL,
        width=2.5,
        scale=14,
    )
    ax.text(
        *(normal_base + 1.22 * normal),
        r"$\boldsymbol{n}$",
        color=TEAL,
        weight="bold",
        ha="center",
        va="center",
    )

    traction_end = midpoint + np.array([1.65, 0.0])
    arrow(
        ax,
        tuple(midpoint),
        tuple(traction_end),
        color=BLUE,
        width=2.6,
        scale=15,
    )
    ax.text(
        traction_end[0] + 0.12,
        traction_end[1] + 0.12,
        r"$\boldsymbol{t}=\boldsymbol{\sigma}^{\mathsf{T}}\boldsymbol{n}$",
        color=BLUE,
        ha="left",
        weight="bold",
    )

    normal_length = float(np.dot(np.array([1.65, 0.0]), normal))
    normal_end = midpoint + normal_length * normal
    arrow(
        ax,
        tuple(midpoint),
        tuple(normal_end),
        color=PURPLE,
        width=2.2,
        scale=13,
        zorder=10,
    )
    ax.plot(
        [normal_end[0], traction_end[0]],
        [normal_end[1], traction_end[1]],
        color=GRAY,
        linewidth=1.4,
        linestyle="--",
    )
    ax.text(
        *(midpoint + 0.52 * normal - 0.18 * tangent),
        r"$\sigma_n\boldsymbol{n}$",
        color=PURPLE,
        ha="right",
        va="center",
    )
    ax.text(
        midpoint[0] - 0.33,
        midpoint[1] + 0.78,
        "結晶面",
        color=GOLD,
        weight="bold",
        rotation=62,
        ha="center",
    )

    arrow(ax, (1.2, 0.35), (2.1, 0.35), color=NAVY, width=1.7, scale=11)
    ax.text(2.23, 0.35, r"$x_1$", va="center")
    ax.set(xlim=(-0.05, 8.05), ylim=(0.05, 4.15), aspect="equal")
    ax.axis("off")
    ax.set_title(
        "任意の結晶面に作用する応力ベクトル",
        fontsize=15,
        weight="bold",
        pad=12,
    )
    fig.tight_layout()
    return finish(fig, "cleavage-traction.svg")


def stress_coordinate_rotation() -> Path:
    """主応力座標から45度回転した座標軸を描く。"""

    fig, ax = plt.subplots(figsize=(6.8, 5.6))
    origin = np.array([0.0, 0.0])
    arrow(ax, tuple(origin), (2.65, 0.0), color=NAVY, width=2.1, scale=13)
    arrow(ax, tuple(origin), (0.0, 2.65), color=NAVY, width=2.1, scale=13)
    ax.text(2.82, -0.03, r"$x_1$", color=NAVY, va="center", fontsize=12)
    ax.text(0.03, 2.83, r"$x_2$", color=NAVY, ha="left", fontsize=12)

    theta = math.pi / 4
    e1p = np.array([math.cos(theta), math.sin(theta)])
    e2p = np.array([-math.sin(theta), math.cos(theta)])
    arrow(ax, tuple(origin), tuple(2.65 * e1p), color=RED, width=2.7, scale=14)
    arrow(ax, tuple(origin), tuple(2.65 * e2p), color=BLUE, width=2.7, scale=14)
    ax.text(*(2.88 * e1p), r"$x_1^{\prime}$", color=RED, fontsize=12, ha="center")
    ax.text(*(2.88 * e2p), r"$x_2^{\prime}$", color=BLUE, fontsize=12, ha="center")

    arc = Arc(
        (0, 0),
        1.45,
        1.45,
        theta1=0,
        theta2=45,
        edgecolor=GOLD,
        linewidth=2.5,
    )
    ax.add_patch(arc)
    arrow(
        ax,
        (0.72 * math.cos(math.radians(39)), 0.72 * math.sin(math.radians(39))),
        (0.72 * math.cos(theta), 0.72 * math.sin(theta)),
        color=GOLD,
        width=1.8,
        scale=10,
    )
    ax.text(0.78, 0.31, r"$45^\circ$", color=GOLD, weight="bold")

    circle = Circle((0, 0), 0.17, facecolor="white", edgecolor=TEAL, linewidth=2)
    ax.add_patch(circle)
    ax.plot(0, 0, marker=".", markersize=9, color=TEAL)
    ax.text(
        0.19,
        -0.28,
        r"$x_3=x_3^{\prime}$（紙面手前）",
        color=TEAL,
        ha="left",
    )

    ax.axhline(0, color=GRID, lw=0.8, zorder=0)
    ax.axvline(0, color=GRID, lw=0.8, zorder=0)
    ax.set(xlim=(-2.55, 3.2), ylim=(-0.75, 3.15), aspect="equal")
    ax.axis("off")
    ax.set_title(
        "座標軸を反時計回りに回す受動変換",
        fontsize=15,
        weight="bold",
        pad=12,
    )
    fig.tight_layout()
    return finish(fig, "stress-coordinate-rotation.svg")


def mises_tresca_yield_loci() -> Path:
    """平面応力空間でMises楕円とTresca六角形を比較する。"""

    fig, ax = plt.subplots(figsize=(7.2, 6.7))
    angles = np.linspace(0, 2 * np.pi, 721)
    c = np.cos(angles)
    s = np.sin(angles)
    radius = 1.0 / np.sqrt(c**2 - c * s + s**2)
    ax.plot(
        radius * c,
        radius * s,
        color=BLUE,
        linewidth=2.8,
        label="Mises",
    )

    tresca = np.array(
        [
            [1, 0],
            [1, 1],
            [0, 1],
            [-1, 0],
            [-1, -1],
            [0, -1],
            [1, 0],
        ],
        dtype=float,
    )
    ax.plot(
        tresca[:, 0],
        tresca[:, 1],
        color=RED,
        linewidth=2.8,
        label="Tresca",
    )

    line = np.linspace(-1.2, 1.2, 101)
    ax.plot(
        line,
        -line,
        color=TEAL,
        linestyle="--",
        linewidth=1.8,
        label=r"純せん断 $\sigma_2=-\sigma_1$",
    )
    mises_point = np.array([1 / math.sqrt(3), -1 / math.sqrt(3)])
    tresca_point = np.array([0.5, -0.5])
    ax.scatter(*mises_point, s=62, color=BLUE, edgecolor="white", zorder=10)
    ax.scatter(*tresca_point, s=62, color=RED, edgecolor="white", zorder=10)
    ax.annotate(
        r"$|\tau|/\sigma_{\mathrm{y}}=1/\sqrt{3}$",
        xy=mises_point,
        xytext=(0.72, -0.88),
        color=BLUE,
        arrowprops={"arrowstyle": "->", "color": BLUE},
        fontsize=9.5,
    )
    ax.annotate(
        r"$|\tau|/\sigma_{\mathrm{y}}=1/2$",
        xy=tresca_point,
        xytext=(0.63, -0.43),
        color=RED,
        arrowprops={"arrowstyle": "->", "color": RED},
        fontsize=9.5,
    )

    ax.axhline(0, color=NAVY, lw=1.0)
    ax.axvline(0, color=NAVY, lw=1.0)
    ax.set_xlabel(r"$\sigma_1/\sigma_{\mathrm{y}}$")
    ax.set_ylabel(r"$\sigma_2/\sigma_{\mathrm{y}}$")
    ax.set(xlim=(-1.25, 1.25), ylim=(-1.25, 1.25), aspect="equal")
    ax.grid(color=GRID, lw=0.7, alpha=0.65)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", fontsize=9.5, frameon=True)
    ax.set_title(
        "Mises条件とTresca条件の降伏曲線",
        fontsize=15,
        weight="bold",
        pad=12,
    )
    fig.tight_layout()
    return finish(fig, "mises-tresca-yield-loci.svg")


def _truss_support(
    ax: plt.Axes,
    x: float,
    y: float,
    support: str,
) -> None:
    """平面トラス用のピン・ローラー・固定支持を描く。"""

    if support == "fixed":
        ax.plot([x + 0.04, x + 0.04], [y - 0.42, y + 0.42], color=NAVY, lw=3)
        for offset in np.linspace(-0.34, 0.34, 5):
            ax.plot(
                [x + 0.04, x + 0.24],
                [y + offset, y + offset - 0.15],
                color=GRAY,
                lw=1.0,
            )
        return

    triangle = Polygon(
        [[x, y - 0.04], [x - 0.23, y - 0.35], [x + 0.23, y - 0.35]],
        closed=True,
        facecolor="white",
        edgecolor=NAVY,
        linewidth=1.5,
    )
    ax.add_patch(triangle)
    base_y = y - 0.40
    if support == "roller":
        for dx in (-0.12, 0.12):
            ax.add_patch(
                Circle(
                    (x + dx, base_y),
                    0.055,
                    facecolor="white",
                    edgecolor=NAVY,
                    linewidth=1.2,
                )
            )
        base_y -= 0.08
    ax.plot([x - 0.32, x + 0.32], [base_y, base_y], color=NAVY, lw=1.4)


def truss_determinacy() -> Path:
    """4種類のトラスと支持条件をベクターで清書する。"""

    fig, axes = plt.subplots(1, 4, figsize=(12.4, 3.8))
    cases = (
        ("(a)", [(0, 0), (0, 1), (1.5, 1), (1.5, 0)], [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], ("pin", "roller"), (5, 4, 3, 0)),
        ("(b)", [(0, 0), (0, 1), (1.5, 1), (1.5, 0)], [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)], ("pin", "roller"), (6, 4, 3, 1)),
        ("(c)", [(0, 0), (0, 1), (1.5, 1), (1.5, 0)], [(0, 1), (1, 2), (2, 3), (0, 2)], ("pin", "pin"), (4, 4, 4, 0)),
        ("(d)", [(0, 0), (0, 1), (1.5, 1), (1.5, 0)], [(0, 1), (1, 2), (2, 3), (0, 2)], ("pin", "fixed"), (4, 4, 5, 1)),
    )

    for ax, (label, nodes, members, supports, _counts) in zip(axes, cases):
        points = np.asarray(nodes, dtype=float)
        for i, j in members:
            ax.plot(
                [points[i, 0], points[j, 0]],
                [points[i, 1], points[j, 1]],
                color=BLUE,
                linewidth=2.6,
                zorder=2,
            )
        for x, y in points:
            ax.add_patch(
                Circle(
                    (x, y),
                    0.065,
                    facecolor="white",
                    edgecolor=NAVY,
                    linewidth=1.7,
                    zorder=6,
                )
            )
        _truss_support(ax, *points[0], supports[0])
        _truss_support(ax, *points[3], supports[1])
        ax.set_title(label, fontsize=13, weight="bold", pad=4)
        ax.set(xlim=(-0.45, 1.95), ylim=(-0.57, 1.27), aspect="equal")
        ax.axis("off")

    fig.suptitle(
        "平面トラスの部材配置と支持条件",
        fontsize=15,
        weight="bold",
        y=1.02,
    )
    fig.tight_layout()
    return finish(fig, "truss-determinacy.svg")


def afm_cantilever() -> Path:
    """AFMカンチレバーの側面と断面寸法を描く。"""

    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    ax.add_patch(
        Rectangle(
            (0.75, 1.65),
            6.0,
            0.36,
            facecolor=PALE_BLUE,
            edgecolor=NAVY,
            linewidth=2.0,
        )
    )
    ax.plot([0.75, 0.75], [1.05, 2.65], color=NAVY, lw=4)
    for y in np.linspace(1.12, 2.55, 8):
        ax.plot([0.42, 0.75], [y - 0.16, y], color=GRAY, lw=1.1)
    arrow(ax, (6.75, 2.72), (6.75, 1.05), color=RED, width=2.5, scale=15)
    ax.text(
        6.88,
        2.55,
        r"$P=100\,\mu\mathrm{N}$",
        color=RED,
        ha="left",
        va="center",
        weight="bold",
    )
    dimension(
        ax,
        (0.75, 0.82),
        (6.75, 0.82),
        r"$L=200\,\mu\mathrm{m}$",
        label_offset=(0, -0.14),
    )

    inset_x, inset_y = 7.55, 1.35
    section_w, section_h = 1.5, 0.72
    ax.add_patch(
        Rectangle(
            (inset_x, inset_y),
            section_w,
            section_h,
            facecolor=PALE_GOLD,
            edgecolor=NAVY,
            linewidth=1.8,
        )
    )
    dimension(
        ax,
        (inset_x, inset_y + section_h + 0.33),
        (inset_x + section_w, inset_y + section_h + 0.33),
        r"$b=50\,\mu\mathrm{m}$",
    )
    dimension(
        ax,
        (inset_x + section_w + 0.32, inset_y),
        (inset_x + section_w + 0.32, inset_y + section_h),
        r"$h=5\,\mu\mathrm{m}$",
        label_offset=(0.55, 0),
    )
    arrow(
        ax,
        (inset_x - 0.42, inset_y + section_h + 0.65),
        (inset_x - 0.42, inset_y + section_h + 0.10),
        color=RED,
        width=1.8,
        scale=10,
    )
    ax.text(
        inset_x - 0.42,
        inset_y + section_h + 0.80,
        "荷重方向",
        color=RED,
        ha="center",
        fontsize=9,
    )
    ax.text(
        inset_x + section_w / 2,
        0.62,
        "長方形断面",
        ha="center",
        color=NAVY,
        weight="bold",
        fontsize=10,
    )
    ax.text(3.75, 2.25, r"$E=200\,\mathrm{GPa}$", ha="center", color=BLUE)
    ax.set(xlim=(0.0, 10.25), ylim=(0.15, 3.25), aspect="equal")
    ax.axis("off")
    ax.set_title(
        "AFMカンチレバーの梁モデルと断面",
        fontsize=15,
        weight="bold",
        pad=10,
    )
    fig.tight_layout()
    return finish(fig, "afm-cantilever.svg")


def screw_dislocation_pair() -> Path:
    """同符号ならせん転位対と斥力を断面図で示す。"""

    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    positions = (-1.55, 1.55)
    for x in positions:
        ax.add_patch(
            Circle(
                (x, 0),
                0.28,
                facecolor=PALE_BLUE,
                edgecolor=BLUE,
                linewidth=2.3,
            )
        )
        ax.plot(x, 0, marker=".", markersize=13, color=BLUE)
        ax.text(
            x,
            -0.55,
            r"$+x_3$",
            color=BLUE,
            ha="center",
            fontsize=10,
        )
    ax.text(-1.55, 0.52, "転位 I", color=NAVY, ha="center", weight="bold")
    ax.text(1.55, 0.52, "転位 II", color=NAVY, ha="center", weight="bold")
    dimension(
        ax,
        (-1.55, 0.82),
        (1.55, 0.82),
        r"$r$",
        label_offset=(0, 0.16),
    )
    arrow(ax, (-3.15, -0.73), (-2.35, -0.73), color=NAVY, width=1.5, scale=9)
    ax.text(-2.22, -0.73, r"$x_1$", va="center", fontsize=9)
    arrow(ax, (-3.15, -0.73), (-3.15, 0.02), color=NAVY, width=1.5, scale=9)
    ax.text(-3.12, 0.14, r"$x_2$", ha="left", fontsize=9)
    ax.set(xlim=(-3.5, 3.5), ylim=(-0.95, 1.45), aspect="equal")
    ax.axis("off")
    ax.set_title(
        "平行ならせん転位間の相互作用",
        fontsize=15,
        weight="bold",
        pad=10,
    )
    fig.tight_layout()
    return finish(fig, "screw-dislocation-pair.svg")


def schmid_factor_geometry() -> Path:
    """Schmid則の引張軸・面法線・すべり方向を模式化する。"""

    fig, ax = plt.subplots(figsize=(7.7, 5.7))
    plane = Polygon(
        [[-2.4, -0.65], [1.45, -1.25], [2.55, 0.45], [-1.3, 1.05]],
        closed=True,
        facecolor=PALE_GOLD,
        edgecolor=GOLD,
        linewidth=2.0,
        alpha=0.82,
    )
    ax.add_patch(plane)
    origin = np.array([0.0, 0.0])
    load = np.array([0.65, 2.55])
    normal = np.array([-0.60, 2.15])
    slip = np.array([2.25, -0.35])
    arrow(ax, tuple(origin), tuple(load), color=RED, width=2.7, scale=15)
    arrow(ax, tuple(origin), tuple(normal), color=TEAL, width=2.6, scale=15)
    arrow(ax, tuple(origin), tuple(slip), color=BLUE, width=2.6, scale=15)
    ax.text(*(load + np.array([0.08, 0.16])), r"$\boldsymbol{L}$", color=RED, fontsize=13, weight="bold")
    ax.text(*(normal + np.array([-0.15, 0.15])), r"$\boldsymbol{n}$", color=TEAL, fontsize=13, weight="bold")
    ax.text(*(slip + np.array([0.16, -0.04])), r"$\boldsymbol{d}$", color=BLUE, fontsize=13, weight="bold")

    phi1 = math.degrees(math.atan2(normal[1], normal[0]))
    phi2 = math.degrees(math.atan2(load[1], load[0]))
    arc_phi = Arc((0, 0), 1.55, 1.55, theta1=phi2, theta2=phi1, color=PURPLE, lw=2)
    ax.add_patch(arc_phi)
    ax.text(-0.02, 0.83, r"$\phi$", color=PURPLE, fontsize=12, weight="bold")

    slip_angle = math.degrees(math.atan2(slip[1], slip[0]))
    arc_lambda = Arc(
        (0, 0),
        2.15,
        2.15,
        theta1=slip_angle,
        theta2=phi2,
        color=ORANGE,
        lw=2,
    )
    ax.add_patch(arc_lambda)
    ax.text(0.91, 0.56, r"$\lambda$", color=ORANGE, fontsize=12, weight="bold")

    ax.text(-1.72, -0.60, "すべり面", color=GOLD, weight="bold", rotation=-8)
    ax.set(xlim=(-2.75, 3.0), ylim=(-1.65, 3.0), aspect="equal")
    ax.axis("off")
    ax.set_title(
        "Schmid則の幾何",
        fontsize=15,
        weight="bold",
        pad=10,
    )
    fig.tight_layout()
    return finish(fig, "schmid-factor-geometry.svg")


def main() -> None:
    """全図を生成し、生成先を表示する。"""

    generators = (
        stress_cube_components,
        cleavage_traction,
        stress_coordinate_rotation,
        mises_tresca_yield_loci,
        truss_determinacy,
        cantilever_problem,
        cantilever_solution,
        afm_cantilever,
        rolling_roll_problem,
        rolling_roll_solution,
        screw_dislocation_geometry,
        screw_dislocation_pair,
        edge_dislocation_pair,
        edge_dislocation_force,
        schmid_factor_geometry,
        fcc_123_specimen,
        fcc_slip_trace,
        single_polycrystal_stress_strain,
    )
    for generator in generators:
        output_path = generator()
        print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
