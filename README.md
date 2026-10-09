# qe-workflow-tools

[![tests](https://github.com/otnielxs/dft-workflow-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/otnielxs/dft-workflow-tools/actions/workflows/tests.yml)

Python tools for Quantum ESPRESSO (QE) workflows: parse `pw.x`
outputs, read band structure and DOS data, and make publication-ready plots.
Dependencies are kept minimal (`numpy`, `matplotlib`).


## Features

- Parse `pw.x` output: total energy (Ry), Fermi energy (eV), SCF convergence status, job completion marker
- Read band structure (`bands.dat.gnu`) and DOS data
- Read high-symmetry k-points and labels from `crystal_b` k-path inputs
- Combined band structure + DOS plot with `plot_band_dos`
- Unit tests built on real QE outputs

## Installation

````bash
git clone https://github.com/otnielxs/qe-workflow-tools.git
cd qe-workflow-tools
pip install -e ".[dev]"
````

Requires Python 3.10 or newer.

## Quick start

Everything below uses the silicon example in `examples/si/`.

````python
from dftwf.parsers import get_total_energy, get_fermi_energy, is_converged, is_job_done
from dftwf.plotting import plot_band_dos

scf = "examples/si/scf.out"
print(get_total_energy(scf), "Ry")
print(get_fermi_energy(scf), "eV")
print(is_converged(scf), is_job_done(scf))

plot_band_dos(
    bands_file="examples/si/bands.dat.gnu",
    dos_file="examples/si/dos.dat",
    fermi_energy=get_fermi_energy(scf),
    kpath_output="examples/si/band.out",
    kpath_input="examples/si/bands.in",
    output="silicon_bands_dos.png",
    energy_range=(-12, 10),
    title="Electronic Properties of Silicon (Si)",
)
````

Or run `python examples/si/run_example.py`, or open `examples/si/demo.ipynb`.

> The pseudopotential for Si is not included. Download it from the
> Quantum ESPRESSO pseudopotential library to rerun the calculations
> from the `.in` files.

## Units

Total energies are returned in Rydberg (Ry) and Fermi energies in electronvolt (eV),
exactly as printed by QE.

## Project structure

````
src/dftwf/      parsers.py, kpath.py, plotting.py
tests/          unit tests and fixtures
examples/si/    silicon example (QE inputs/outputs, script, notebook)
````

## Tests

````bash
pytest -v
````
