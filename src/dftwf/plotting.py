
"""Plotting utilities for Quantum ESPRESSO electronic structures."""

from pathlib import Path

from .kpath import get_kpath_ticks
import numpy as np
import matplotlib.pyplot as plt
from dftwf.parsers import read_bands_gnu, read_dos


def plot_band_dos(
    bands_file,
    dos_file,
    fermi_energy,
    output="bands_dos.png",
    energy_range=(-12.0, 10.0),
    title="Electronic Properties",
    k_ticks=None,
    kpath_output=None,
    kpath_input=None,
    show=False,
):
    """Plot band structure and DOS side by side.

    Parameters
    ----------
    bands_file : str or Path
        Output data from bands.x, usually a .gnu file.
    dos_file : str or Path
        Output data from dos.x.
    fermi_energy : float
        Fermi energy in eV, using the same energy reference
        as the band and DOS data.
    output : str or Path
        Filename for the saved figure.
    energy_range : tuple
        Minimum and maximum energy relative to the Fermi level.
    title : str
        Overall figure title.
    k_ticks : list of tuples, optional
        Explicit symmetry-point positions, e.g.
        [(0.0, r"$\\Gamma$"), (1.0, "X"), (2.0, "L")].
        Supply only positions verified from the k-point path.
    show : bool
        Whether to display the figure interactively.
    """
    bands = read_bands_gnu(bands_file)
    if kpath_output is not None:
        k_ticks = get_kpath_ticks(
           kpath_output,
           input_file=kpath_input,
        )

    energy_dos, dos_values = read_dos(dos_file)

    emin, emax = energy_range
    energy_dos = energy_dos - fermi_energy

    fig, (ax_band, ax_dos) = plt.subplots(
        1,
        2,
        figsize=(9, 6),
        sharey=True,
        gridspec_kw={"width_ratios": [3, 1], "wspace": 0.05},
        constrained_layout=True,
    )

    # Band structure
    for band in bands:
        k_path = band[:, 0]
        energy_band = band[:, 1] - fermi_energy
        ax_band.plot(k_path, energy_band, color="navy", lw=1.2)

    ax_band.axhline(
        0, color="red", linestyle="--", linewidth=1, label=r"$E_F$"
    )

    k_min = min(band[:, 0].min() for band in bands)
    k_max = max(band[:, 0].max() for band in bands)

    ax_band.set_xlim(k_min, k_max)

    if k_ticks is not None:
        positions, labels = zip(*k_ticks)
        ax_band.set_xticks(positions)
        ax_band.set_xticklabels(labels)

    ax_band.set_xlabel("Wave vector")
    ax_band.set_ylabel(r"$E - E_F$ (eV)")
    ax_band.set_title("Band Structure")
    ax_band.set_ylim(emin, emax)
    ax_band.grid(True, linestyle=":", alpha=0.5)

    # Density of states
    visible = (
        (energy_dos >= emin)
        & (energy_dos <= emax)
        & np.isfinite(dos_values)
    )

    if not np.any(visible):
        raise ValueError("No DOS data falls within the selected energy range.")

    ax_dos.plot(dos_values, energy_dos, color="crimson", lw=1.2)
    ax_dos.fill_betweenx(
        energy_dos,
        0,
        dos_values,
        where=visible,
        color="crimson",
        alpha=0.25,
    )
    ax_dos.axhline(0, color="red", linestyle="--", linewidth=1)
    ax_dos.set_xlabel("DOS (states/eV)")
    ax_dos.set_title("DOS")
    ax_dos.set_xlim(left=0)
    ax_dos.grid(False)

    fig.suptitle(title, fontsize=14, fontweight="bold")

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")

    print(f"Plot saved to: {output}")

    if show:
        plt.show()

    return fig, (ax_band, ax_dos)
