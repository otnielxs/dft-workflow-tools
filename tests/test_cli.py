from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from dftwf.cli import main

ROOT = Path(__file__).resolve().parent.parent
CONV = ROOT / "examples" / "si" / "convergence"


def test_cli_converge(tmp_path, capsys):
    csv_path = tmp_path / "c.csv"
    png_path = tmp_path / "c.png"
    code = main([
        "converge", str(CONV), "--threshold", "0.1",
        "--csv", str(csv_path), "--plot", str(png_path),
    ])
    out = capsys.readouterr().out
    assert code == 0
    assert "Converged at ecutwfc = 70 Ry" in out
    assert csv_path.exists() and png_path.exists()


def test_cli_empty_folder(tmp_path, capsys):
    code = main(["converge", str(tmp_path)])
    assert code == 1
    assert "Error" in capsys.readouterr().err
