
from dftwf.parsers import (
    get_total_energy,
    get_fermi_energy,
    is_converged,
    is_job_done,
)


def test_parse_total_energy(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text(
        """
!    total energy              =   -100.12345678 Ry
!    total energy              =   -100.23456789 Ry
        """
    )

    assert get_total_energy(output) == -100.23456789


def test_parse_fermi_energy(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text("the Fermi energy is    5.4321 ev\n")

    assert get_fermi_energy(output) == 5.4321


def test_missing_fermi_energy(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text("No Fermi energy reported\n")

    assert get_fermi_energy(output) is None


def test_scf_converged(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text("convergence has been achieved\n")

    assert is_converged(output) is True


def test_scf_not_converged(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text("convergence NOT achieved\n")

    assert is_converged(output) is False


def test_job_done(tmp_path):
    output = tmp_path / "scf.out"
    output.write_text("Some output\n   JOB DONE.\n")

    assert is_job_done(output) is True
