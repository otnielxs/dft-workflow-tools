"""Contoh: analisis konvergensi ecutwfc untuk Si dari 5 output pw.x."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from dftwf.convergence import analyze_ecut

HERE = Path(__file__).resolve().parent

points, converged = analyze_ecut(
    HERE,
    threshold_mev=0.1,
    csv_path=HERE / "convergence.csv",
    plot_path=HERE / "convergence.png",
    title="Si: ecutwfc convergence (6x6x6 k-points)",
)

for p in points:
    print(p.file, p.ecutwfc, p.energy_ry, p.delta_mev_per_atom)
print("Converged at ecutwfc =", converged, "Ry")
