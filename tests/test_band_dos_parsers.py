import pytest
from pathlib import Path
from dftwf.parsers import read_bands_gnu, read_dos

EX = Path(__file__).resolve().parent.parent / "examples" / "si"

def test_read_bands_shape():
    bands = read_bands_gnu(EX / "bands.dat.gnu")
    assert isinstance(bands, list)
    assert all(b.ndim == 2 for b in bands)
    assert all(b.shape[1] == 2 for b in bands)

def test_read_dos_shape_and_range():
    energies, dos = read_dos(EX / "dos.dat")
    assert energies.ndim == 1
    assert dos.ndim == 1
    assert len(energies) == len(dos)
    assert energies.min() < energies.max()

def test_read_bands_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_bands_gnu("no_such_file.gnu")

def test_read_dos_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_dos("no_such_file.dat")
