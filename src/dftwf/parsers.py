
"""Parsers for Quantum ESPRESSO output files."""

import re
from pathlib import Path


def _read_output(filepath: str | Path) -> str:
    """Read a Quantum ESPRESSO output file."""
    return Path(filepath).read_text(encoding="utf-8", errors="replace")


def get_total_energy(filepath: str | Path) -> float | None:
    """Return the last reported total energy in Ry.

    Returns None if no total energy is found.
    """
    text = _read_output(filepath)

    matches = re.findall(
        r"!\s+total energy\s*=\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)"
        r"(?:[EeDd][-+]?\d+)?)\s+Ry",
        text,
        flags=re.IGNORECASE,
    )

    if not matches:
        return None

    return float(matches[-1].replace("D", "E").replace("d", "e"))


def get_fermi_energy(filepath: str | Path) -> float | None:
    """Return the reported Fermi energy in eV, if available.

    Returns None if the output does not report a Fermi energy.
    """
    text = _read_output(filepath)

    matches = re.findall(
        r"the Fermi energy is\s+"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)"
        r"(?:[EeDd][-+]?\d+)?)\s+ev",
        text,
        flags=re.IGNORECASE,
    )

    if not matches:
        return None

    return float(matches[-1].replace("D", "E").replace("d", "e"))


def is_converged(filepath: str | Path) -> bool:
    """Check whether SCF convergence was achieved."""
    text = _read_output(filepath)

    achieved = re.search(
        r"convergence has been achieved",
        text,
        flags=re.IGNORECASE,
    )

    not_achieved = re.search(
        r"convergence NOT achieved",
        text,
        flags=re.IGNORECASE,
    )

    return bool(achieved) and not bool(not_achieved)


def is_job_done(filepath: str | Path) -> bool:
    """Check whether the output contains the normal completion marker."""
    text = _read_output(filepath)

    return bool(
        re.search(r"^\s*JOB DONE\.", text, flags=re.MULTILINE)
    )


import numpy as np

def read_bands_gnu(filepath):
    """Read band energies from a bands.x .gnu file.
    Returns a list of arrays with columns [k, energy].
    """
    bands = []
    current_band = []
    from pathlib import Path
    with Path(filepath).open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                if current_band:
                    bands.append(np.asarray(current_band, dtype=float))
                    current_band = []
                continue
            if line.startswith("#"):
                continue
            values = [float(value) for value in line.split()]
            if len(values) >= 2:
                current_band.append(values[:2])
    if current_band:
        bands.append(np.asarray(current_band, dtype=float))
    if not bands:
        raise ValueError(f"No band data found in {filepath}")
    return bands

def read_dos(filepath):
    """Read energy, DOS and integrated DOS from a dos.x output file."""
    data = np.loadtxt(filepath, comments="#", ndmin=2)
    if data.shape[1] < 2:
        raise ValueError(f"DOS file must have at least 2 columns: {filepath}")
    return data[:, 0], data[:, 1]
