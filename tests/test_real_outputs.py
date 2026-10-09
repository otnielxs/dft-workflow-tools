from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from dftwf.parsers import (
    get_fermi_energy,
    get_total_energy,
    is_converged,
    is_job_done,
)
from dftwf.plotting import plot_band_dos

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "si"
FIX = Path(__file__).resolve().parent / "fixtures"


def test_real_scf_values():
    scf = str(EX / "scf.out")
    assert get_total_energy(scf) == pytest.approx(-93.41391454, abs=1e-8)
    assert get_fermi_energy(scf) == pytest.approx(6.1984, abs=1e-4)
    assert is_converged(scf) is True
    assert is_job_done(scf) is True


def test_real_scf_not_converged():
    assert is_converged(str(FIX / "scf_not_converged.out")) is False


def test_real_scf_unfinished():
    assert is_job_done(str(FIX / "scf_unfinished.out")) is False


def test_real_scf_without_fermi_energy():
    # Perilaku fungsi bisa None atau exception; keduanya dianggap "tidak ada nilai".
    try:
        value = get_fermi_energy(str(FIX / "scf_no_fermi.out"))
    except Exception:
        value = None
    assert value is None


def test_plot_band_dos_creates_png(tmp_path):
    out = tmp_path / "si_test.png"
    plot_band_dos(
        bands_file=str(EX / "bands.dat.gnu"),
        dos_file=str(EX / "dos.dat"),
        fermi_energy=6.1984,
        kpath_output=str(EX / "band.out"),
        kpath_input=str(EX / "bands.in"),
        output=str(out),
        energy_range=(-12, 10),
        title="Test",
    )
    assert out.exists() and out.stat().st_size > 0
