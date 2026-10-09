
from dftwf.kpath import (
    read_high_symmetry_points,
    get_kpath_ticks,
)


def test_read_high_symmetry_points(tmp_path):
    output = tmp_path / "bands.out"
    output.write_text(
        """
high-symmetry point: 0.0000 0.0000 0.0000 x coordinate 0.0000
high-symmetry point: -1.0000 0.0000 0.0000 x coordinate 1.0000
high-symmetry point: -0.5000 0.5000 0.5000 x coordinate 1.8660
"""
    )

    points = read_high_symmetry_points(output)

    assert len(points) == 3
    assert points[0]["x"] == 0.0
    assert points[1]["x"] == 1.0
    assert points[2]["x"] == 1.8660
    assert points[0]["coordinates"] == (0.0, 0.0, 0.0)


def test_kpath_labels_from_crystal_b_input(tmp_path):
    output = tmp_path / "bands.out"
    output.write_text(
        """
high-symmetry point: 0.0000 0.0000 0.0000 x coordinate 0.0000
high-symmetry point: -1.0000 0.0000 0.0000 x coordinate 1.0000
high-symmetry point: -0.5000 0.5000 0.5000 x coordinate 1.8660
"""
    )

    qe_input = tmp_path / "bands.in"
    qe_input.write_text(
        """
K_POINTS (crystal_b)
3
0.00 0.00 0.00 20 ! Gamma
0.50 0.00 0.50 20 ! X
0.50 0.50 0.50 1  ! L
"""
    )

    ticks = get_kpath_ticks(output, qe_input)

    assert ticks == [
        (0.0, r"$\Gamma$"),
        (1.0, "X"),
        (1.8660, "L"),
    ]
