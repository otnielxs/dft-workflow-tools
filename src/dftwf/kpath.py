
"""Utilities for reading high-symmetry k-points from QE output."""

import re
from pathlib import Path


_POINT_PATTERN = re.compile(
    r"high-symmetry point:\s*"
    r"([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)"
    r"\s+x coordinate\s+([-+\d.Ee]+)",
    re.IGNORECASE,
)


def _read_input_labels(input_file):
    """Read optional point labels from comments in a QE k-point card."""
    if input_file is None:
        return []

    lines = Path(input_file).read_text(
        encoding="utf-8", errors="replace"
    ).splitlines()

    for index, line in enumerate(lines):
        if re.match(r"\s*K_POINTS\b", line, re.IGNORECASE):
            card = line.split("!", 1)[0].lower()

            # The simple label reader currently supports crystal_b paths.
            if "crystal_b" not in card:
                return []

            points = []
            cursor = index + 1

            # Skip blank lines and comments before the number of points.
            while cursor < len(lines):
                candidate = lines[cursor].split("!", 1)[0].strip()
                cursor += 1
                if candidate:
                    break
            else:
                return []

            try:
                number_of_points = int(candidate.split()[0])
            except (ValueError, IndexError):
                return []

            for point_line in lines[cursor:]:
                if len(points) >= number_of_points:
                    break

                label = ""
                if "!" in point_line:
                    label = point_line.split("!", 1)[1].strip()

                data = point_line.split("!", 1)[0].strip()
                if data:
                    points.append(label)

            return points

    return []


def read_high_symmetry_points(output_file, input_file=None):
    """Read high-symmetry point positions from a QE output file.

    Returns a list of dictionaries containing:
    - coordinates: the three coordinates printed by QE
    - x: the cumulative path coordinate printed by QE
    - label: the matching input comment, or the coordinates if
      no label is available

    Input labels are matched to output points by their order.
    """
    text = Path(output_file).read_text(
        encoding="utf-8", errors="replace"
    )

    matches = _POINT_PATTERN.findall(text)
    if not matches:
        raise ValueError(
            f"No high-symmetry points found in {output_file}"
        )

    labels = _read_input_labels(input_file)
    points = []

    for index, match in enumerate(matches):
        coordinates = tuple(float(value) for value in match[:3])
        x_position = float(match[3])

        label = labels[index] if index < len(labels) else ""
        if not label:
            label = "(" + ", ".join(f"{v:g}" for v in coordinates) + ")"

        if label.lower() in {"gamma", "g"}:
            label = r"$\Gamma$"

        points.append(
            {
                "coordinates": coordinates,
                "x": x_position,
                "label": label,
            }
        )

    return points


def get_kpath_ticks(output_file, input_file=None):
    """Return (x-position, label) pairs suitable for matplotlib."""
    points = read_high_symmetry_points(output_file, input_file)
    return [(point["x"], point["label"]) for point in points]
