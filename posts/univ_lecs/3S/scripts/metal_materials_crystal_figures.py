"""金属材料学の結晶構造・変形機構を説明する模式SVGを生成する。

生成物は初学者向けの概念図であり、原子位置・析出物寸法・方位関係を
定量的に表すものではない。
"""

from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/codex-mpl-metal-crystals")

import matplotlib.pyplot as plt
from matplotlib.patches import (
    Circle,
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
PALE_BLUE = "#eef5f8"
PALE_GOLD = "#fbf3d5"
GRID = "#cbd5df"
GRAY = "#64748b"

plt.rcParams.update(
    {
        "font.family": "Hiragino Sans",
        "font.size": 10,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "axes.titlecolor": NAVY,
        "text.color": NAVY,
        "svg.fonttype": "none",
        "svg.hashsalt": "metal-materials-crystal-figures-2026-07-24",
    }
)


def finish(fig: plt.Figure, name: str) -> None:
    """SVGを決定的に保存し、行末空白を除去する。"""

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


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = NAVY,
    width: float = 2.0,
    scale: float = 14,
    style: str = "-|>",
    zorder: int = 8,
) -> FancyArrowPatch:
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=scale,
        color=color,
        lw=width,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def _rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    facecolor: str = "white",
    edgecolor: str = GRID,
    linewidth: float = 1.4,
    radius: float = 0.12,
    zorder: int = 1,
) -> FancyBboxPatch:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.08,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        lw=linewidth,
        zorder=zorder,
    )
    ax.add_patch(box)
    return box


def _gamma_prime_cube(
    ax: plt.Axes,
    x: float,
    y: float,
    size: float,
) -> None:
    """立方体状γ'析出物を簡略な斜投影で描く。"""

    dx = 0.20
    dy = 0.16
    ax.add_patch(
        Rectangle(
            (x, y),
            size,
            size,
            facecolor=PALE_GOLD,
            edgecolor=NAVY,
            lw=1.5,
            zorder=3,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (x, y + size),
                (x + dx, y + size + dy),
                (x + size + dx, y + size + dy),
                (x + size, y + size),
            ],
            closed=True,
            facecolor=GOLD,
            edgecolor=NAVY,
            lw=1.0,
            zorder=4,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (x + size, y),
                (x + size + dx, y + dy),
                (x + size + dx, y + size + dy),
                (x + size, y + size),
            ],
            closed=True,
            facecolor=ORANGE,
            edgecolor=NAVY,
            lw=1.0,
            alpha=0.72,
            zorder=4,
        )
    )
    ax.text(
        x + size / 2,
        y + size / 2,
        "γ′",
        ha="center",
        va="center",
        fontsize=12,
        weight="bold",
        zorder=5,
    )


def _coherent_interface_inset(ax: plt.Axes) -> None:
    _rounded_box(
        ax,
        (8.38, 4.43),
        2.15,
        2.22,
        facecolor="white",
        edgecolor=GRID,
        linewidth=1.1,
        zorder=6,
    )
    ax.text(9.46, 6.43, "整合界面（拡大）", ha="center", weight="bold", fontsize=9, zorder=8)
    ax.plot([9.45, 9.45], [4.72, 6.18], color=NAVY, lw=1.3, ls="--", zorder=8)
    for x in [8.72, 9.08, 9.45, 9.82, 10.18]:
        for y in [4.92, 5.30, 5.68, 6.06]:
            color = BLUE if x < 9.45 else GOLD
            ax.add_patch(Circle((x, y), 0.075, fc=color, ec="white", lw=0.4, zorder=9))
    ax.text(8.88, 4.61, "γ", ha="center", fontsize=9, zorder=8)
    ax.text(9.99, 4.61, "γ′", ha="center", fontsize=9, zorder=8)
    ax.text(9.46, 4.42, "格子面がほぼ連続", ha="center", fontsize=8, color=GRAY, zorder=8)


def superalloy_gamma_gamma_prime() -> None:
    """γ/γ'整合組織と粒界B偏析の提案機構を描く。"""

    fig, (ax_micro, ax_boundary) = plt.subplots(
        1,
        2,
        figsize=(13.6, 6.2),
        gridspec_kw={"width_ratios": [1.42, 1.0]},
    )
    fig.suptitle(
        "Ni基超合金：γ/γ′整合組織と粒界設計",
        fontsize=16,
        weight="bold",
    )

    # γ母相チャネルと立方体状γ'析出物。
    ax = ax_micro
    ax.add_patch(
        Rectangle(
            (0.25, 0.42),
            10.45,
            6.47,
            facecolor=PALE_BLUE,
            edgecolor=NAVY,
            lw=1.5,
            zorder=0,
        )
    )
    ax.text(5.45, 7.22, "粒内：微細で高体積率の整合析出組織", ha="center", weight="bold", fontsize=12)

    for x in [0.72, 3.33, 5.94]:
        for y in [0.86, 4.48]:
            _gamma_prime_cube(ax, x, y, 1.72)

    ax.annotate(
        "γ母相チャネル",
        xy=(2.94, 3.43),
        xytext=(1.65, 3.78),
        arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.6},
        color=BLUE,
        weight="bold",
        ha="center",
        zorder=8,
    )

    # γチャネル内で湾曲し、γ'に阻害される転位。
    dislocation_x = [
        0.35 + index * (7.60 / 80)
        for index in range(81)
    ]
    dislocation_y = [
        3.47 + 0.25 * math.sin((x - 0.35) * math.pi / 1.30)
        for x in dislocation_x
    ]
    ax.plot(
        dislocation_x,
        dislocation_y,
        color=RED,
        lw=3.1,
        solid_capstyle="round",
        zorder=7,
    )
    _arrow(ax, (7.72, 3.47), (8.18, 3.47), color=RED, width=2.8, scale=15)
    ax.annotate(
        "転位は析出物で湾曲・切断抵抗を受ける\n→ 移動しにくく、高温強度が上がる",
        xy=(4.48, 3.47),
        xytext=(5.10, 2.90),
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.5},
        color=RED,
        ha="center",
        va="top",
        fontsize=9,
        weight="bold",
        zorder=10,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none", "alpha": 0.88},
    )

    _coherent_interface_inset(ax)
    ax.annotate(
        "",
        xy=(7.66, 6.34),
        xytext=(8.38, 5.55),
        arrowprops={"arrowstyle": "->", "color": GRAY, "lw": 1.2},
        zorder=7,
    )
    ax.text(
        0.55,
        0.58,
        "格子定数が近い → 低い界面エネルギーで微細分散を保ちやすい",
        fontsize=9,
        color=GRAY,
        va="bottom",
        zorder=8,
    )
    ax.set(xlim=(0, 10.95), ylim=(0, 7.55), aspect="equal")
    ax.axis("off")

    # 粒界B偏析と、複数ある提案機構。
    ax = ax_boundary
    ax.text(4.10, 7.22, "粒界：B偏析で粒界破壊を抑える", ha="center", weight="bold", fontsize=12)
    ax.add_patch(
        Polygon(
            [(0.35, 3.65), (4.02, 3.65), (3.82, 6.95), (0.35, 6.95)],
            closed=True,
            fc=LIGHT,
            ec=NAVY,
            lw=1.3,
            zorder=0,
        )
    )
    ax.add_patch(
        Polygon(
            [(4.02, 3.65), (7.85, 3.65), (7.85, 6.95), (3.82, 6.95)],
            closed=True,
            fc=PALE_BLUE,
            ec=NAVY,
            lw=1.3,
            zorder=0,
        )
    )
    boundary_y = [3.68, 4.05, 4.42, 4.80, 5.18, 5.56, 5.94, 6.32, 6.70, 6.93]
    boundary_x = [4.02, 3.99, 3.95, 3.92, 3.89, 3.86, 3.84, 3.82, 3.81, 3.82]
    ax.plot(boundary_x, boundary_y, color=NAVY, lw=2.3, zorder=4)
    for index, (x, y) in enumerate(zip(boundary_x[1:-1], boundary_y[1:-1], strict=True)):
        offset = -0.13 if index % 2 == 0 else 0.13
        ax.add_patch(Circle((x + offset, y), 0.105, fc=RED, ec="white", lw=0.6, zorder=7))
    ax.annotate(
        "Bの粒界偏析",
        xy=(3.91, 5.48),
        xytext=(5.52, 6.47),
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.5},
        color=RED,
        weight="bold",
        ha="center",
        zorder=8,
    )

    _arrow(ax, (1.05, 5.12), (3.42, 5.12), color=PURPLE, width=2.6, scale=15)
    _arrow(ax, (4.35, 4.66), (6.52, 4.66), color=PURPLE, width=2.6, scale=15)
    ax.text(1.90, 5.38, "転位", color=PURPLE, weight="bold", ha="center")
    ax.text(5.42, 4.92, "すべり伝達", color=PURPLE, weight="bold", ha="center")

    _rounded_box(
        ax,
        (0.42, 0.34),
        7.33,
        2.84,
        facecolor="white",
        edgecolor=GRID,
        linewidth=1.3,
        zorder=1,
    )
    ax.text(
        0.70,
        2.89,
        "B添加で提案されている機構",
        weight="bold",
        fontsize=11,
        va="top",
        zorder=5,
    )
    ax.text(
        0.70,
        2.49,
        "① 粒界凝集力を高める\n"
        "② 粒界からの転位放出・すべり伝達を助ける\n"
        "③ O・Hが関わる環境脆化を抑える可能性",
        fontsize=9.5,
        linespacing=1.55,
        va="top",
        zorder=5,
    )
    ax.text(
        0.70,
        0.58,
        "※ 単一機構に限定しない。組成・粒界性格・試験環境に依存。",
        color=RED,
        fontsize=8.7,
        weight="bold",
        va="bottom",
        zorder=5,
    )
    ax.set(xlim=(0, 8.15), ylim=(0, 7.55), aspect="equal")
    ax.axis("off")

    fig.text(
        0.5,
        0.018,
        "模式図・縮尺なし。γ′の形状・寸法・粒界機構は合金組成、温度、応力、環境で変化する。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    finish(fig, "superalloy-gamma-gamma-prime.svg")


def _draw_isometric_cube(ax: plt.Axes) -> None:
    front = [(0.95, 1.62), (5.15, 1.62), (5.15, 5.80), (0.95, 5.80)]
    shift = (1.25, 0.94)
    back = [(x + shift[0], y + shift[1]) for x, y in front]
    for polygon in [
        Polygon(front, closed=True, fc=PALE_BLUE, ec=NAVY, lw=1.6, alpha=0.45),
        Polygon(
            [front[2], front[3], back[3], back[2]],
            closed=True,
            fc=LIGHT,
            ec=NAVY,
            lw=1.3,
            alpha=0.68,
        ),
        Polygon(
            [front[1], front[2], back[2], back[1]],
            closed=True,
            fc=PALE_GOLD,
            ec=NAVY,
            lw=1.3,
            alpha=0.42,
        ),
    ]:
        ax.add_patch(polygon)
    for (x1, y1), (x2, y2) in zip(front, back, strict=True):
        ax.plot([x1, x2], [y1, y2], color=NAVY, lw=1.3)
    ax.add_patch(Polygon(back, closed=True, fill=False, ec=NAVY, lw=1.2))

    slip_planes = [
        ([(1.10, 2.15), (5.15, 2.15), (6.24, 2.97), (2.19, 2.97)], BLUE),
        ([(1.34, 1.62), (5.15, 5.18), (6.20, 5.97), (2.40, 2.40)], TEAL),
        ([(0.95, 4.82), (4.30, 1.62), (5.55, 2.56), (2.20, 5.77)], PURPLE),
    ]
    for points, color in slip_planes:
        ax.add_patch(
            Polygon(
                points,
                closed=True,
                fc=color,
                ec=color,
                lw=1.2,
                alpha=0.20,
                zorder=3,
            )
        )

    _arrow(ax, (1.48, 2.48), (4.42, 2.48), color=BLUE, width=2.3, scale=13)
    _arrow(ax, (2.20, 2.45), (4.58, 4.68), color=TEAL, width=2.3, scale=13)
    _arrow(ax, (1.80, 4.37), (3.96, 2.31), color=PURPLE, width=2.3, scale=13)


def _hexagon(center: tuple[float, float], radius: float) -> list[tuple[float, float]]:
    cx, cy = center
    return [
        (cx + radius, cy),
        (cx + radius / 2, cy + radius * 0.72),
        (cx - radius / 2, cy + radius * 0.72),
        (cx - radius, cy),
        (cx - radius / 2, cy - radius * 0.72),
        (cx + radius / 2, cy - radius * 0.72),
    ]


def _draw_hcp_prism(ax: plt.Axes) -> None:
    bottom = _hexagon((2.32, 2.00), 1.55)
    top = _hexagon((2.32, 5.42), 1.55)
    ax.add_patch(Polygon(bottom, closed=True, fc=LIGHT, ec=NAVY, lw=1.5, alpha=0.60))
    ax.add_patch(Polygon(top, closed=True, fc=TEAL, ec=NAVY, lw=1.6, alpha=0.24))
    for (x1, y1), (x2, y2) in zip(bottom, top, strict=True):
        ax.plot([x1, x2], [y1, y2], color=NAVY, lw=1.4)

    basal = _hexagon((2.32, 3.66), 1.55)
    ax.add_patch(Polygon(basal, closed=True, fc=TEAL, ec=TEAL, lw=1.5, alpha=0.24, zorder=3))
    _arrow(ax, (1.05, 3.66), (3.65, 3.66), color=TEAL, width=2.8, scale=14)
    ax.text(2.34, 3.93, r"底面$\{0001\}\langle a\rangle$", color=TEAL, ha="center", weight="bold")
    ax.text(2.34, 3.35, "低CRSS：室温で作動しやすい", color=TEAL, ha="center", fontsize=8.8)

    non_basal = [(2.65, 1.30), (3.52, 1.98), (2.00, 6.38), (1.12, 5.72)]
    ax.add_patch(
        Polygon(
            non_basal,
            closed=True,
            fc=ORANGE,
            ec=RED,
            lw=1.5,
            ls="--",
            alpha=0.18,
            zorder=4,
        )
    )
    ax.annotate(
        r"非底面すべり（柱面・錐面、$c+a$）"
        "\n高CRSS：室温では作動しにくい",
        xy=(2.28, 5.45),
        xytext=(4.47, 6.42),
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.3},
        color=RED,
        ha="center",
        fontsize=8.7,
        weight="bold",
    )


def _draw_twin_rotation(ax: plt.Axes) -> None:
    _rounded_box(
        ax,
        (5.20, 1.08),
        4.38,
        5.60,
        facecolor="white",
        edgecolor=GRID,
        linewidth=1.2,
        zorder=0,
    )
    ax.text(
        7.39,
        6.41,
        r"$\{10\bar{1}2\}$引張双晶",
        ha="center",
        weight="bold",
        fontsize=10.5,
    )

    original = Polygon(
        [(5.58, 3.35), (6.92, 3.35), (6.92, 5.42), (5.58, 5.42)],
        closed=True,
        fc=PALE_BLUE,
        ec=NAVY,
        lw=1.4,
    )
    rotated = Polygon(
        [(7.86, 3.18), (9.19, 3.70), (8.43, 5.64), (7.10, 5.11)],
        closed=True,
        fc=PALE_GOLD,
        ec=NAVY,
        lw=1.4,
    )
    ax.add_patch(original)
    ax.add_patch(rotated)
    for y in [3.72, 4.10, 4.48, 4.86]:
        ax.plot([5.73, 6.77], [y, y], color=BLUE, lw=1.3)
    for offset in [0.25, 0.63, 1.01, 1.39]:
        x1 = 7.12 + 0.18 * offset
        y1 = 3.46 + offset
        ax.plot([x1, x1 + 1.02], [y1, y1 + 0.40], color=GOLD, lw=1.3)
    _arrow(ax, (6.78, 4.18), (7.46, 4.36), color=PURPLE, width=2.2, scale=13)
    ax.text(6.23, 3.10, "双晶前", ha="center", fontsize=8.5)
    ax.text(8.24, 3.00, "格子方位が回転", ha="center", color=PURPLE, fontsize=8.5, weight="bold")

    ax.text(
        7.39,
        2.57,
        "荷重方向・集合組織で\nSchmid因子と双晶せん断の向きが変わる",
        ha="center",
        va="center",
        fontsize=8.7,
    )
    _arrow(ax, (5.63, 1.55), (5.63, 2.23), color=RED, width=1.8, scale=11)
    _arrow(ax, (6.12, 2.23), (6.12, 1.55), color=RED, width=1.8, scale=11)
    ax.text(7.70, 1.67, "正負を反転しても同じようには作動しない\n＝ 極性・方位依存", color=RED, fontsize=8.5, weight="bold", va="center")


def al_mg_slip_twinning() -> None:
    """fcc Alとhcp Mgの変形自由度を対比する。"""

    fig, (ax_al, ax_mg) = plt.subplots(1, 2, figsize=(14.0, 6.5))
    fig.suptitle("AlとMg：室温で作動できる変形モードの違い", fontsize=16, weight="bold")

    ax = ax_al
    ax.text(4.35, 7.42, "fcc Al：複数のすべり系が作動", ha="center", weight="bold", fontsize=12)
    _draw_isometric_cube(ax)
    ax.text(
        4.34,
        6.52,
        r"主すべり系：$\{111\}\langle110\rangle$",
        ha="center",
        color=BLUE,
        weight="bold",
    )
    ax.annotate(
        r"異なる$\{111\}$面と$\langle110\rangle$方向",
        xy=(3.60, 3.30),
        xytext=(6.50, 4.40),
        arrowprops={"arrowstyle": "->", "color": NAVY, "lw": 1.3},
        ha="center",
        fontsize=9,
    )
    _rounded_box(
        ax,
        (0.62, 0.25),
        7.50,
        1.02,
        facecolor="white",
        edgecolor=GRID,
        linewidth=1.2,
    )
    ax.text(
        4.37,
        0.76,
        "4面 × 各3方向 ＝ 12すべり系（独立な系を5つ以上確保）\n"
        "低いCRSSで多重すべり → 隣接粒に合わせて形を変えやすい",
        ha="center",
        va="center",
        fontsize=9.3,
        weight="bold",
    )
    ax.set(xlim=(0, 8.65), ylim=(0, 7.75), aspect="equal")
    ax.axis("off")

    ax = ax_mg
    ax.text(5.03, 7.42, "hcp Mg：底面すべりだけでは自由度が不足", ha="center", weight="bold", fontsize=12)
    _draw_hcp_prism(ax)
    _draw_twin_rotation(ax)
    ax.text(
        4.95,
        0.49,
        r"作動条件：$\tau_{\mathrm{RSS}}=m\sigma\geq\tau_{\mathrm{CRSS}}$"
        "　（方位で $m$、変形モードでCRSSが異なる）",
        ha="center",
        va="center",
        fontsize=9.1,
        weight="bold",
    )
    ax.set(xlim=(0, 9.85), ylim=(0, 7.75), aspect="equal")
    ax.axis("off")

    fig.text(
        0.5,
        0.018,
        "模式図・縮尺なし。すべり面の投影、双晶回転角、CRSSの大小は概念的に示している。",
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    finish(fig, "al-mg-slip-twinning.svg")


def main() -> None:
    superalloy_gamma_gamma_prime()
    al_mg_slip_twinning()


if __name__ == "__main__":
    main()
