
"""Contoh end-to-end: parse output QE untuk Si lalu plot band + DOS."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from dftwf.parsers import (
    get_fermi_energy,
    get_total_energy,
    is_converged,
    is_job_done,
)
from dftwf.plotting import plot_band_dos

HERE = Path(__file__).resolve().parent
scf = str(HERE / "scf.out")

print("Total energy :", get_total_energy(scf), "Ry")
print("Fermi energy :", get_fermi_energy(scf), "eV")
print("SCF converged:", is_converged(scf))
print("Job completed:", is_job_done(scf))

plot_band_dos(
    bands_file=str(HERE / "bands.dat.gnu"),
    dos_file=str(HERE / "dos.dat"),
    fermi_energy=get_fermi_energy(scf),
    kpath_output=str(HERE / "band.out"),
    kpath_input=str(HERE / "bands.in"),
    output=str(HERE / "silicon_bands_dos.png"),
    energy_range=(-12, 10),
    title="Electronic Properties of Silicon (Si)",
)
