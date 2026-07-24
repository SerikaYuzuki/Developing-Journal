"""金属材料学の頻出問題へ一対一に対応する模式図をSVGで生成する。

複数概念を一枚へ詰め込まず、問題文を読んだ直後に必要となる概念だけを
分離して示す。図中の寸法、原子配置、曲線形状は定量データではない。
"""

from __future__ import annotations

import itertools
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/codex-mpl-metal-materials-problem-order")

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
        "svg.hashsalt": "metal-materials-problem-order-2026-07-24",
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


def orowan_mechanism() -> None:
    """非切断粒子間の張り出しと、通過後のOrowan loopを描く。"""

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.8))
    centers = [(0.27, 0.64), (0.73, 0.64)]
    particle_radius = 0.075

    # 臨界張り出し。
    ax = axes[0]
    ax.add_patch(Rectangle((0.03, 0.12), 0.94, 0.77, fc=LIGHT, ec="none"))
    for x, y in centers:
        ax.add_patch(Circle((x, y), particle_radius, fc=GOLD, ec=NAVY, lw=1.6, zorder=5))

    bow_radius = (centers[1][0] - centers[0][0]) / 2
    bow_mid_x = (centers[0][0] + centers[1][0]) / 2
    arc_x = np.linspace(centers[0][0], centers[1][0], 240)
    arc_y = centers[0][1] - np.sqrt(
        np.clip(bow_radius**2 - (arc_x - bow_mid_x) ** 2, 0, None)
    )
    ax.plot([0.05, centers[0][0]], [centers[0][1], centers[0][1]], color=RED, lw=3.0)
    ax.plot(arc_x, arc_y, color=RED, lw=3.0)
    ax.plot([centers[1][0], 0.95], [centers[1][1], centers[1][1]], color=RED, lw=3.0)

    ax.add_patch(
        FancyArrowPatch(
            (centers[0][0], 0.82),
            (centers[1][0], 0.82),
            arrowstyle="<->",
            mutation_scale=15,
            color=GRAY,
            lw=1.7,
        )
    )
    ax.text(0.50, 0.845, r"有効自由間隔 $\lambda$", color=GRAY, ha="center")

    radius_tip_x = 0.60
    radius_tip_y = centers[0][1] - np.sqrt(
        bow_radius**2 - (radius_tip_x - bow_mid_x) ** 2
    )
    ax.add_patch(
        FancyArrowPatch(
            (bow_mid_x, centers[0][1]),
            (radius_tip_x, radius_tip_y),
            arrowstyle="<->",
            mutation_scale=13,
            color=BLUE,
            lw=1.8,
        )
    )
    ax.text(0.57, 0.52, r"$R$", color=BLUE, ha="center", weight="bold")

    ax.add_patch(
        FancyArrowPatch(
            (centers[0][0], centers[0][1] - 0.015),
            (centers[0][0], centers[0][1] - 0.16),
            arrowstyle="-|>",
            mutation_scale=14,
            color=TEAL,
            lw=2.0,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (centers[1][0], centers[1][1] - 0.16),
            (centers[1][0], centers[1][1] - 0.015),
            arrowstyle="-|>",
            mutation_scale=14,
            color=TEAL,
            lw=2.0,
        )
    )
    ax.text(0.235, 0.49, r"$T$", color=TEAL, weight="bold")
    ax.text(0.755, 0.49, r"$T$", color=TEAL, weight="bold")

    ax.add_patch(
        FancyArrowPatch(
            (0.50, 0.40),
            (0.50, 0.23),
            arrowstyle="-|>",
            mutation_scale=16,
            color=PURPLE,
            lw=2.4,
        )
    )
    ax.text(0.525, 0.30, r"単位長さ当たりの力 $\tau b$", color=PURPLE, va="center")
    ax.text(
        0.50,
        0.145,
        r"臨界付近：$R\simeq\lambda/2,\quad \tau b\simeq T/R$",
        ha="center",
        weight="bold",
    )
    ax.set_title("粒子間で連続転位線が張り出す", fontsize=13, weight="bold")
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")

    # 通過後：主転位は前進し、粒子の周囲へループだけを残す。
    ax = axes[1]
    ax.add_patch(Rectangle((0.03, 0.12), 0.94, 0.77, fc=LIGHT, ec="none"))
    for x, y in centers:
        ax.add_patch(Circle((x, y), particle_radius, fc=GOLD, ec=NAVY, lw=1.6, zorder=5))
        ax.add_patch(Circle((x, y), particle_radius + 0.055, fill=False, ec=RED, lw=2.8))
    ax.plot([0.07, 0.93], [0.30, 0.30], color=RED, lw=3.0)
    ax.add_patch(
        FancyArrowPatch(
            (0.71, 0.30),
            (0.91, 0.30),
            arrowstyle="-|>",
            mutation_scale=16,
            color=RED,
            lw=2.5,
        )
    )
    ax.annotate(
        "粒子周囲に残る\nOrowan loop",
        xy=(0.27, 0.77),
        xytext=(0.50, 0.84),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        weight="bold",
    )
    ax.annotate(
        "通過後の転位",
        xy=(0.72, 0.30),
        xytext=(0.62, 0.18),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
    )
    ax.text(0.50, 0.50, "粒子は切断されない", ha="center", color=GRAY)
    ax.set_title("通過後、粒子周囲へループを残す", fontsize=13, weight="bold")
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")

    fig.suptitle("Orowan機構：非切断粒子を転位が迂回する", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：粒子径、転位形状、力の矢印は定量的ではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.045, 1, 0.92))
    finish(fig, "orowan-mechanism.svg")


def _grain_network(ax: plt.Axes) -> None:
    polygons = [
        [(0, 0), (0.43, 0), (0.48, 0.43), (0.25, 0.62), (0, 0.50)],
        [(0.43, 0), (1, 0), (1, 0.43), (0.73, 0.57), (0.48, 0.43)],
        [(0, 0.50), (0.25, 0.62), (0.42, 1), (0, 1)],
        [(0.25, 0.62), (0.48, 0.43), (0.73, 0.57), (0.78, 1), (0.42, 1)],
        [(0.73, 0.57), (1, 0.43), (1, 1), (0.78, 1)],
    ]
    for polygon in polygons:
        ax.add_patch(Polygon(polygon, closed=True, facecolor=LIGHT, edgecolor=NAVY, lw=1.7))
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal")
    ax.axis("off")


def cu_ni_fe_microstructures() -> None:
    """Cu–Ni孤立固溶とCu–Fe析出だけを比較する。"""

    rng = np.random.default_rng(241)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.0))
    for ax in axes:
        _grain_network(ax)

    ni_points = rng.uniform(0.06, 0.94, size=(42, 2))
    axes[0].scatter(
        ni_points[:, 0],
        ni_points[:, 1],
        s=30,
        color=BLUE,
        edgecolor="white",
        lw=0.5,
        zorder=5,
    )
    axes[0].annotate(
        "Ni原子は置換固溶し、互いに孤立",
        xy=(0.61, 0.70),
        xytext=(0.48, 1.07),
        arrowprops={"arrowstyle": "->", "color": BLUE},
        color=BLUE,
        ha="center",
        weight="bold",
        annotation_clip=False,
    )
    axes[0].text(
        0.50,
        -0.12,
        "Ni–Ni交換相互作用が長距離に連結しない\n→ 巨視的には常磁性的",
        ha="center",
        transform=axes[0].transAxes,
        weight="bold",
    )
    axes[0].set_title("Cu–Ni：希薄固溶体", fontsize=13, weight="bold", pad=48)

    cluster_centers = np.array([[0.26, 0.28], [0.67, 0.74], [0.80, 0.25]])
    for center in cluster_centers:
        points = center + rng.normal(scale=0.034, size=(14, 2))
        axes[1].scatter(
            points[:, 0],
            points[:, 1],
            s=33,
            color=RED,
            edgecolor="white",
            lw=0.5,
            zorder=5,
        )
    axes[1].annotate(
        "Fe-rich析出物・クラスタ",
        xy=(0.67, 0.74),
        xytext=(0.53, 1.07),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        weight="bold",
        annotation_clip=False,
    )
    axes[1].text(
        0.50,
        -0.12,
        "粒子内でFe原子が隣接し交換結合\n→ 強磁性的応答を示し得る",
        ha="center",
        transform=axes[1].transAxes,
        weight="bold",
    )
    axes[1].set_title("Cu–Fe：析出組織", fontsize=13, weight="bold", pad=48)

    fig.suptitle("微量磁性元素でも、空間分布が違えば磁気応答が変わる", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：析出状態・粒径・磁気応答は熱処理と温度に依存する。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.90), w_pad=4.0)
    finish(fig, "cu-ni-fe-microstructures.svg")


def _electron_path(ax: plt.Axes) -> None:
    path = np.array(
        [
            [0.08, 0.80],
            [0.23, 0.74],
            [0.36, 0.62],
            [0.51, 0.69],
            [0.66, 0.53],
            [0.82, 0.59],
            [0.94, 0.45],
        ]
    )
    ax.plot(path[:, 0], path[:, 1], color=TEAL, lw=2.5, zorder=6)
    ax.add_patch(
        FancyArrowPatch(
            path[-2],
            path[-1],
            arrowstyle="-|>",
            mutation_scale=16,
            color=TEAL,
            lw=2.2,
            zorder=7,
        )
    )


def cu_as_bi_microstructures() -> None:
    """Cu–As粒内固溶とCu–Bi粒界偏析だけを比較する。"""

    rng = np.random.default_rng(317)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.0))
    for ax in axes:
        _grain_network(ax)

    as_points = rng.uniform(0.06, 0.94, size=(48, 2))
    axes[0].scatter(
        as_points[:, 0],
        as_points[:, 1],
        s=27,
        color=PURPLE,
        edgecolor="white",
        lw=0.5,
        zorder=5,
    )
    _electron_path(axes[0])
    axes[0].annotate(
        "Asは粒内へ置換固溶",
        xy=(0.62, 0.70),
        xytext=(0.48, 1.07),
        arrowprops={"arrowstyle": "->", "color": PURPLE},
        color=PURPLE,
        ha="center",
        weight="bold",
        annotation_clip=False,
    )
    axes[0].text(
        0.50,
        -0.12,
        "粒内全体に多数の電子散乱中心\n→ 電気抵抗が大きく増加",
        ha="center",
        transform=axes[0].transAxes,
        weight="bold",
    )
    axes[0].set_title("Cu–As：粒内固溶", fontsize=13, weight="bold", pad=48)

    gb_paths = [
        np.column_stack([np.linspace(0.26, 0.48, 12), np.linspace(0.62, 0.43, 12)]),
        np.column_stack([np.linspace(0.48, 0.73, 13), np.linspace(0.43, 0.57, 13)]),
        np.column_stack([np.linspace(0.73, 0.78, 11), np.linspace(0.57, 1.0, 11)]),
    ]
    for points in gb_paths:
        axes[1].scatter(
            points[:, 0],
            points[:, 1],
            s=33,
            color=RED,
            edgecolor="white",
            lw=0.5,
            zorder=7,
        )
    crack_path = np.vstack([gb_paths[0], gb_paths[1][1:], gb_paths[2][1:]])
    axes[1].plot(
        crack_path[:, 0],
        crack_path[:, 1],
        color=RED,
        lw=3.2,
        alpha=0.75,
        zorder=6,
    )
    axes[1].annotate(
        "Biは粒界へ偏析・第二相化",
        xy=(0.63, 0.51),
        xytext=(0.54, 1.07),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
        ha="center",
        weight="bold",
        annotation_clip=False,
    )
    axes[1].text(
        0.50,
        -0.12,
        r"粒界凝集力を低下 → 粒界脆化"
        "\n"
        r"$d\gg\ell_e$ なら体積抵抗への寄与は比較的小さい",
        ha="center",
        transform=axes[1].transAxes,
        weight="bold",
    )
    axes[1].set_title("Cu–Bi：粒界偏析", fontsize=13, weight="bold", pad=48)

    fig.suptitle("同じ微量添加でも、電子とき裂の通り道にいる場所が違う", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：固溶・偏析量と粒界被覆率は定量的ではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.90), w_pad=4.0)
    finish(fig, "cu-as-bi-microstructures.svg")


def _project_l12(point: tuple[float, float, float]) -> tuple[float, float]:
    x, y, z = point
    return 0.12 + 0.54 * x + 0.26 * y, 0.16 + 0.58 * z + 0.20 * y


def l12_apb() -> None:
    """L1₂単位胞と、二本の超部分転位に挟まれたAPBを描く。"""

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))

    # L1₂単位胞：Alは頂点、Niは面心。
    ax = axes[0]
    cube_edges = []
    for point in itertools.product([0.0, 1.0], repeat=3):
        for axis in range(3):
            neighbor = list(point)
            neighbor[axis] = 1.0 - neighbor[axis]
            neighbor_tuple = tuple(neighbor)
            if point < neighbor_tuple:
                cube_edges.append((point, neighbor_tuple))
    for start, end in cube_edges:
        x0, y0 = _project_l12(start)
        x1, y1 = _project_l12(end)
        ax.plot([x0, x1], [y0, y1], color=GRAY, lw=1.6, zorder=1)

    corners = list(itertools.product([0.0, 1.0], repeat=3))
    face_centers = [
        (0.5, 0.5, 0.0),
        (0.5, 0.5, 1.0),
        (0.5, 0.0, 0.5),
        (0.5, 1.0, 0.5),
        (0.0, 0.5, 0.5),
        (1.0, 0.5, 0.5),
    ]
    corner_xy = np.array([_project_l12(point) for point in corners])
    face_xy = np.array([_project_l12(point) for point in face_centers])
    ax.scatter(
        corner_xy[:, 0],
        corner_xy[:, 1],
        s=160,
        color=ORANGE,
        edgecolor="white",
        lw=0.7,
        zorder=4,
    )
    ax.scatter(
        face_xy[:, 0],
        face_xy[:, 1],
        s=160,
        color=BLUE,
        edgecolor="white",
        lw=0.7,
        zorder=5,
    )
    ax.annotate(
        "Al：立方体の頂点",
        xy=corner_xy[1],
        xytext=(0.13, 0.91),
        arrowprops={"arrowstyle": "->", "color": ORANGE},
        color=ORANGE,
        weight="bold",
    )
    ax.annotate(
        "Ni：各面の中心",
        xy=face_xy[3],
        xytext=(0.62, 0.06),
        arrowprops={"arrowstyle": "->", "color": BLUE},
        color=BLUE,
        weight="bold",
    )
    ax.text(0.50, 0.02, r"Ni$_3$Al：Ni 3個に対してAl 1個", ha="center")
    ax.set_title(r"$L1_2$規則構造", fontsize=13, weight="bold")
    ax.set(xlim=(0, 1.02), ylim=(0, 1.02), aspect="equal")
    ax.axis("off")

    # 二本のa/2<110>転位に挟まれたAPB ribbon。
    ax = axes[1]
    ax.add_patch(Rectangle((0.03, 0.16), 0.94, 0.73, fc=LIGHT, ec="none"))
    trailing_x = 0.37
    leading_x = 0.69
    ax.axvspan(trailing_x, leading_x, ymin=0.16, ymax=0.89, color=GOLD, alpha=0.30)
    lattice_x = np.linspace(0.09, 0.91, 9)
    lattice_y = np.linspace(0.27, 0.77, 5)
    for i, x in enumerate(lattice_x):
        for j, y in enumerate(lattice_y):
            al_site = i % 2 == 0 and j % 2 == 0
            if trailing_x < x < leading_x:
                al_site = i % 2 == 1 and j % 2 == 0
            color = ORANGE if al_site else BLUE
            ax.add_patch(Circle((x, y), 0.026, fc=color, ec="white", lw=0.5, zorder=5))

    ax.plot([trailing_x, trailing_x], [0.19, 0.86], color=RED, lw=2.5, ls="--")
    ax.plot([leading_x, leading_x], [0.19, 0.86], color=RED, lw=2.5, ls="--")
    ax.text(
        trailing_x,
        0.94,
        r"後続転位" "\n" r"$a/2\langle110\rangle$",
        color=RED,
        ha="center",
        weight="bold",
    )
    ax.text(
        leading_x,
        0.94,
        r"先行転位" "\n" r"$a/2\langle110\rangle$",
        color=RED,
        ha="center",
        weight="bold",
    )
    ax.text(0.53, 0.52, "APB\n（逆位相境界）", ha="center", weight="bold")
    ax.add_patch(
        FancyArrowPatch(
            (0.20, 0.12),
            (0.85, 0.12),
            arrowstyle="-|>",
            mutation_scale=17,
            color=NAVY,
            lw=2.0,
        )
    )
    ax.text(0.52, 0.065, "すべり方向", ha="center")
    ax.text(
        0.50,
        -0.035,
        "先行転位が規則位相をずらし、後続転位が通過すると回復",
        ha="center",
        transform=ax.transAxes,
    )
    ax.set_title("二本の転位に挟まれたAPB", fontsize=13, weight="bold", pad=28)
    ax.set(xlim=(0, 1), ylim=(0, 1.03), aspect="equal")
    ax.axis("off")

    fig.suptitle(r"$L1_2$規則配列と逆位相境界", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：投影方向、転位芯幅、APB幅は定量的ではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.91), w_pad=3.5)
    finish(fig, "l12-apb.svg")


def kear_wilsdorf() -> None:
    """交差すべりによるKear–Wilsdorf lockと強度の温度依存を描く。"""

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))

    # {111}から{100}への交差すべり。
    ax = axes[0]
    plane_111 = Polygon(
        [(0.35, 0.18), (5.80, 0.18), (7.00, 1.65), (1.55, 1.65)],
        closed=True,
        fc=BLUE,
        ec=NAVY,
        alpha=0.15,
    )
    plane_100 = Polygon(
        [(3.75, 0.04), (6.20, 1.10), (6.20, 4.15), (3.75, 3.10)],
        closed=True,
        fc=GOLD,
        ec=NAVY,
        alpha=0.27,
    )
    ax.add_patch(plane_111)
    ax.add_patch(plane_100)
    ax.plot([0.85, 3.90], [0.95, 0.95], color=RED, lw=3.3)
    ax.plot([3.90, 5.25], [0.95, 1.56], color=RED, lw=3.3)
    ax.plot([5.25, 5.25], [1.56, 3.30], color=RED, lw=3.3)
    ax.text(1.60, 0.46, r"$\{111\}$ 主すべり面", ha="center")
    ax.text(5.55, 3.70, r"$\{100\}$ cube面", ha="center")
    ax.annotate(
        "交差すべり",
        xy=(4.60, 1.26),
        xytext=(3.15, 2.30),
        arrowprops={"arrowstyle": "->", "color": PURPLE},
        color=PURPLE,
        ha="center",
        weight="bold",
    )
    ax.annotate(
        "Kear–Wilsdorf lock\n（不動化した区間）",
        xy=(5.25, 2.75),
        xytext=(2.85, 3.55),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        ha="center",
        weight="bold",
    )
    ax.text(1.80, 1.12, "規則格子転位のねじ成分", color=RED, ha="center")
    ax.add_patch(
        FancyArrowPatch(
            (1.00, 4.18),
            (3.30, 4.18),
            arrowstyle="-|>",
            mutation_scale=18,
            color=ORANGE,
            lw=2.5,
        )
    )
    ax.text(2.15, 4.32, "温度上昇：交差すべり確率が増加", color=ORANGE, ha="center", weight="bold")
    ax.set_title(r"$\{111\}\rightarrow\{100\}$ の交差すべり", fontsize=13, weight="bold")
    ax.set(xlim=(0, 7.25), ylim=(0, 4.55), aspect="equal")
    ax.axis("off")

    # 降伏強度の逆温度依存と、高温側の軟化。
    ax = axes[1]
    temperature = np.array([0.0, 0.14, 0.30, 0.48, 0.63, 0.74, 0.86, 1.0])
    strength = np.array([0.30, 0.34, 0.46, 0.67, 0.88, 0.91, 0.69, 0.36])
    tt = np.linspace(0, 1, 400)
    ss = PchipInterpolator(temperature, strength)(tt)
    ax.fill_between(tt[tt <= 0.74], 0, ss[tt <= 0.74], color=GOLD, alpha=0.22)
    ax.fill_between(tt[tt >= 0.74], 0, ss[tt >= 0.74], color=BLUE, alpha=0.12)
    ax.plot(tt, ss, color=NAVY, lw=3.2)
    ax.axvline(0.74, color=GRAY, lw=1.4, ls=":")
    ax.scatter([0.74], [0.91], s=55, color=RED, zorder=5)
    ax.annotate(
        "K–W lockが増える\n→ 温度とともに強度上昇",
        xy=(0.52, 0.70),
        xytext=(0.29, 0.88),
        arrowprops={"arrowstyle": "->", "color": ORANGE},
        color=ORANGE,
        ha="center",
        weight="bold",
    )
    ax.annotate(
        "さらに高温：lock解除・上昇運動・拡散\n→ 通常の熱軟化",
        xy=(0.88, 0.63),
        xytext=(0.69, 0.30),
        arrowprops={"arrowstyle": "->", "color": BLUE},
        color=BLUE,
        ha="center",
    )
    ax.text(0.13, 0.22, r"$\{111\}$上のすべり", ha="center", color=GRAY)
    ax.set(
        xlim=(0, 1.04),
        ylim=(0, 1.02),
        xlabel="温度  →",
        ylabel="降伏強度  →",
    )
    ax.set_title("逆温度依存性は有限の温度域で現れる", fontsize=13, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.18, color=GRID)

    fig.suptitle("Kear–Wilsdorf機構：昇温が転位を動きにくくする", fontsize=15, weight="bold")
    fig.text(
        0.5,
        0.012,
        "教育用模式図：面の角度、転位芯、強度―温度曲線は定量データではない。",
        ha="center",
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.91), w_pad=3.0)
    finish(fig, "kear-wilsdorf.svg")


def main() -> None:
    orowan_mechanism()
    cu_ni_fe_microstructures()
    cu_as_bi_microstructures()
    l12_apb()
    kear_wilsdorf()


if __name__ == "__main__":
    main()
