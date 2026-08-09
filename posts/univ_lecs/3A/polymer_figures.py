"""高分子材料学の記事で使う共重合組成曲線を再生成する。"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT = Path(__file__).parent / "images" / "copolymer-composition-curves.png"


def instantaneous_composition(f1: np.ndarray, r1: float, r2: float) -> np.ndarray:
    """Mayo--Lewis 式から瞬間共重合組成 F1 を返す。"""
    f2 = 1.0 - f1
    numerator = r1 * f1**2 + f1 * f2
    denominator = numerator + f1 * f2 + r2 * f2**2
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator != 0,
    )


def main() -> None:
    systems = [
        ("Styrene / maleic anhydride", 0.04, 0.0, "-"),
        ("Styrene / methyl methacrylate", 0.52, 0.46, "--"),
        ("Styrene / butadiene", 0.78, 1.3, "-."),
        ("Vinyl acetate / acrylonitrile", 0.1, 9.0, ":"),
    ]
    f1 = np.linspace(0.0, 1.0, 501)

    fig, ax = plt.subplots(figsize=(8.0, 6.4), constrained_layout=True)
    for label, r1, r2, linestyle in systems:
        f_polymer = instantaneous_composition(f1, r1, r2)
        f_polymer[-1] = 1.0
        ax.plot(
            f1,
            f_polymer,
            linewidth=2.4,
            linestyle=linestyle,
            label=f"{label}  ($r_1={r1:g}, r_2={r2:g}$)",
        )

    ax.plot(f1, f1, color="0.55", linewidth=1.2, label="$F_1=f_1$")
    ax.set(
        xlabel="Mole fraction of monomer 1 in feed, $f_1$",
        ylabel="Mole fraction of monomer 1 in copolymer, $F_1$",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="0.88")
    ax.legend(fontsize=8.5, loc="best")
    fig.savefig(OUTPUT, dpi=220)


if __name__ == "__main__":
    main()
