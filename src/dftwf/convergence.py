"""Cutoff-energy convergence analysis for Quantum ESPRESSO pw.x outputs."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .parsers import (
    get_ecutwfc,
    get_number_of_atoms,
    get_total_energy,
    is_converged,
    is_job_done,
)

RY_TO_MEV = 13605.693122994  # 1 Ry in meV


@dataclass
class ConvergencePoint:
    """One pw.x run in a convergence series."""

    file: str
    ecutwfc: float | None
    n_atoms: int | None
    energy_ry: float | None
    valid: bool
    delta_mev_per_atom: float | None = None


def _safe(func, path):
    """Call a parser and return None if it raises."""
    try:
        return func(path)
    except Exception:
        return None


def _compute_deltas(valid_points):
    """Fill delta_mev_per_atom: |E_i - E_(i-1)| in meV/atom (points sorted by ecut)."""
    for prev, cur in zip(valid_points, valid_points[1:]):
        cur.delta_mev_per_atom = (
            abs(cur.energy_ry - prev.energy_ry) * RY_TO_MEV / cur.n_atoms
        )


def collect_ecut_results(folder, pattern="*.out"):
    """Read all pw.x outputs in a folder and return a list of ConvergencePoint.

    Valid points (job finished, SCF converged, all values found) come first,
    sorted by ecutwfc. Invalid points follow and are excluded from the analysis.
    """
    paths = sorted(Path(folder).glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files matching '{pattern}' in {folder}")

    points = []
    for path in paths:
        p = str(path)
        ecut = _safe(get_ecutwfc, p)
        n_atoms = _safe(get_number_of_atoms, p)
        energy = _safe(get_total_energy, p)
        ok = (
            bool(_safe(is_job_done, p))
            and bool(_safe(is_converged, p))
            and ecut is not None
            and n_atoms is not None
            and energy is not None
        )
        points.append(ConvergencePoint(path.name, ecut, n_atoms, energy, ok))

    valid = sorted((pt for pt in points if pt.valid), key=lambda pt: pt.ecutwfc)
    invalid = [pt for pt in points if not pt.valid]
    _compute_deltas(valid)
    return valid + invalid


def find_converged(points, threshold_mev=1.0):
    """Return the lowest ecutwfc after which every step is below the threshold.

    The step is |E(i) - E(i-1)| in meV/atom. Returns None if never reached.
    """
    valid = [pt for pt in points if pt.valid]
    deltas = [pt.delta_mev_per_atom for pt in valid]
    for i in range(1, len(valid)):
        if all(d < threshold_mev for d in deltas[i:]):
            return valid[i].ecutwfc
    return None


def write_csv(points, path):
    """Write the convergence table to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["file", "ecutwfc_ry", "n_atoms", "total_energy_ry",
             "delta_mev_per_atom", "valid"]
        )
        for pt in points:
            writer.writerow([
                pt.file,
                "" if pt.ecutwfc is None else pt.ecutwfc,
                "" if pt.n_atoms is None else pt.n_atoms,
                "" if pt.energy_ry is None else pt.energy_ry,
                "" if pt.delta_mev_per_atom is None else f"{pt.delta_mev_per_atom:.6f}",
                pt.valid,
            ])


def plot_convergence(points, output, threshold_mev=1.0, converged=None, title=None):
    """Plot E - E(last point) and the step size |dE| against ecutwfc."""
    import matplotlib.pyplot as plt

    valid = [pt for pt in points if pt.valid]
    if len(valid) < 2:
        raise ValueError("Need at least two valid points to plot convergence.")

    x = [pt.ecutwfc for pt in valid]
    ref = valid[-1]
    rel = [(pt.energy_ry - ref.energy_ry) * RY_TO_MEV / pt.n_atoms for pt in valid]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

    ax1.plot(x, rel, "o-")
    ax1.axhline(0.0, color="gray", linestyle=":", linewidth=1)
    ax1.set_xlabel("ecutwfc (Ry)")
    ax1.set_ylabel("E − E(last point) (meV/atom)")

    ax2.semilogy(x[1:], [pt.delta_mev_per_atom for pt in valid[1:]], "s-")
    ax2.axhline(
        threshold_mev, color="gray", linestyle="--",
        label=f"threshold = {threshold_mev:g} meV/atom",
    )
    if converged is not None:
        ax2.axvline(
            converged, color="tab:green", linestyle=":",
            label=f"converged at {converged:g} Ry",
        )
    ax2.set_xlabel("ecutwfc (Ry)")
    ax2.set_ylabel("|ΔE| between steps (meV/atom)")
    ax2.legend()

    if title:
        fig.suptitle(title)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def analyze_ecut(folder, threshold_mev=1.0, csv_path=None, plot_path=None,
                 pattern="*.out", title=None):
    """Collect results, find the converged cutoff, optionally write CSV and plot.

    Returns (points, converged_ecutwfc_or_None).
    """
    points = collect_ecut_results(folder, pattern=pattern)
    converged = find_converged(points, threshold_mev=threshold_mev)
    if csv_path:
        write_csv(points, csv_path)
    if plot_path:
        plot_convergence(points, plot_path, threshold_mev=threshold_mev,
                         converged=converged, title=title)
    return points, converged
