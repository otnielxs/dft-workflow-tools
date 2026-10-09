from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from dftwf.convergence import (
    analyze_ecut,
    collect_ecut_results,
    find_converged,
)
from dftwf.parsers import get_ecutwfc, get_number_of_atoms

ROOT = Path(__file__).resolve().parent.parent
CONV = ROOT / "examples" / "si" / "convergence"


def test_parse_ecut_and_atoms():
    out = str(CONV / "scf_si_40.out")
    assert get_ecutwfc(out) == pytest.approx(40.0)
    assert get_number_of_atoms(out) == 2


def test_collect_sorted_valid_and_deltas():
    points = collect_ecut_results(CONV)
    assert [p.ecutwfc for p in points] == [40.0, 50.0, 60.0, 70.0, 80.0]
    assert all(p.valid for p in points)
    assert points[0].delta_mev_per_atom is None
    expected = [0.6399, 0.1353, 0.0788, 0.0631]
    for point, value in zip(points[1:], expected):
        assert point.delta_mev_per_atom == pytest.approx(value, abs=1e-3)


@pytest.mark.parametrize(
    "threshold, expected",
    [(1.0, 50.0), (0.1, 70.0), (0.01, None)],
)
def test_find_converged(threshold, expected):
    points = collect_ecut_results(CONV)
    assert find_converged(points, threshold_mev=threshold) == expected


def test_unfinished_job_is_invalid(tmp_path):
    for src in CONV.glob("scf_si_*.out"):
        text = src.read_text()
        if src.name == "scf_si_80.out":
            text = "\n".join(
                line for line in text.splitlines() if "JOB DONE" not in line
            )
        (tmp_path / src.name).write_text(text)

    points = collect_ecut_results(tmp_path)
    invalid = [p for p in points if not p.valid]
    assert [p.file for p in invalid] == ["scf_si_80.out"]
    assert find_converged(points, threshold_mev=0.1) == 70.0


def test_empty_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        collect_ecut_results(tmp_path)


def test_analyze_writes_csv_and_plot(tmp_path):
    csv_path = tmp_path / "conv.csv"
    png_path = tmp_path / "conv.png"
    points, converged = analyze_ecut(
        CONV, threshold_mev=0.1, csv_path=csv_path, plot_path=png_path
    )
    assert converged == 70.0
    assert png_path.exists() and png_path.stat().st_size > 0
    assert len(csv_path.read_text().strip().splitlines()) == 6  # header + 5 titik
