# qe-workflow-tools

[![tests](https://github.com/otnielxs/qe-workflow-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/otnielxs/qe-workflow-tools/actions/workflows/tests.yml)

Python tools for Quantum ESPRESSO (QE) workflows: parse `pw.x`
outputs, read band structure and DOS data, and make publication-ready plots.
Dependencies are kept minimal (`numpy`, `matplotlib`).


## Features

- Parse `pw.x` output: total energy (Ry), Fermi energy (eV), SCF convergence status, job completion marker
- Read band structure (`bands.dat.gnu`) and DOS data
- Read high-symmetry k-points and labels from `crystal_b` k-path inputs
- Combined band structure + DOS plot with `plot_band_dos`
- Cutoff-energy convergence analysis (CSV table, plot, `dftwf converge` command)
- Unit tests built on real QE outputs

## Installation

````bash
git clone https://github.com/otnielxs/qe-workflow-tools.git
cd qe-workflow-tools
python -m pip install -e ".[dev]"
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

## Convergence test (cutoff energy)

Run `pw.x` for several `ecutwfc` values, put the outputs in one folder, then:

```bash
dftwf converge examples/si/convergence --threshold 0.1 \
    --csv convergence.csv --plot convergence.png
```
file                  ecutwfc (Ry)            E (Ry)   dE (meV/atom)  status
scf_40.out                      40      -93.41380748               -  ok
scf_50.out                      50      -93.41390154          0.6399  ok
scf_60.out                      60      -93.41392143          0.1353  ok
scf_70.out                      70      -93.41393301          0.0788  ok
scf_80.out                      80      -93.41394229          0.0631  ok

Converged at ecutwfc = 70 Ry (threshold 0.1 meV/atom).

or from Python:

```python
from dftwf.convergence import analyze_ecut

points, converged = analyze_ecut(
    "examples/si/convergence",
    threshold_mev=0.1,
    csv_path="convergence.csv",
    plot_path="convergence.png",
)
print("Converged at ecutwfc =", converged, "Ry")
```

A cutoff counts as converged when every energy step from that point onward is
below the threshold (in meV/atom). Runs that did not finish or did not converge
are flagged as invalid and excluded from the analysis. The silicon data in `examples/si/` is for demonstration only; its smearing settings are not recommended production parameters.

## Units

Total energies are returned in Rydberg (Ry) and Fermi energies in electronvolt (eV),
exactly as printed by QE.

## Project structure

````
src/dftwf/      parsers.py, kpath.py, plotting.py, convergence.py, cli.py
tests/          unit tests and fixtures
examples/si/    silicon example (QE inputs/outputs, script, notebook)
````

## Tests

````bash
pytest -v
````
## Limitations

- Parsers are tested on Quantum ESPRESSO `pw.x` output (non-spin-polarized Si examples); other QE versions or output formats may need adjustments.
- Convergence analysis currently covers `ecutwfc` only (k-point convergence is on the roadmap).
