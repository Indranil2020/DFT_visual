# Open-source Python packages for DFT and TDDFT computational chemistry

**Over 80 actively maintained Python packages** provide interfaces to density functional theory (DFT) and time-dependent DFT codes, spanning universal I/O libraries, code-specific wrappers, workflow tools, and specialized analysis packages. The ecosystem centers on three foundational libraries—**ASE**, **pymatgen**, and **cclib**—that together support 50+ electronic structure codes, while specialized tools like **litesoph**, **TheoDORE**, and **doped** address TDDFT simulations and advanced analysis workflows often overlooked in mainstream discussions.

---

## Universal I/O libraries form the ecosystem foundation

These packages work across multiple DFT/TDDFT codes through unified Python APIs, abstracting away code-specific input/output formats.

### ASE (Atomic Simulation Environment)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://gitlab.com/ase/ase |
| **PyPI** | `ase` |
| **Version** | 3.26.0 (August 2025) |
| **License** | LGPL |

ASE provides the **Calculator abstraction**, a unified interface where any DFT code becomes interchangeable. Input files are generated automatically when calculations run, and outputs are parsed into standardized Python objects.

**Supported codes (30+):** VASP, Quantum ESPRESSO, GPAW, ABINIT, NWChem, Gaussian, SIESTA, CP2K, FHI-aims, CASTEP, ORCA, Psi4, Q-Chem, TURBOMOLE, CRYSTAL, FLEUR, Elk, exciting, Octopus, GAMESS-US, DFTB+, MOPAC, DMol3, GULP, LAMMPS, OpenMX, ONETEP

**Input generation API:**
```python
from ase import Atoms
from ase.calculators.vasp import Vasp

atoms = Atoms('H2O', positions=[[0,0,0], [1,0,0], [0,1,0]])
atoms.calc = Vasp(xc='PBE', encut=400, kpts=(4,4,4))
atoms.calc.write_input(atoms)  # Write without running
```

**Output parsing:** The `ase.io` module reads 50+ formats including OUTCAR, vasprun.xml, Gaussian logs, cube files, CIF, and trajectory formats. Parsed data includes energies, forces, stress, eigenvalues, and magnetic moments via `atoms.get_potential_energy()`, `atoms.get_forces()`.

---

### pymatgen (Python Materials Genomics)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/materialsproject/pymatgen |
| **PyPI** | `pymatgen` |
| **Version** | 2025.6.14 |
| **License** | MIT |

Pymatgen powers the **Materials Project** and offers the most comprehensive VASP support in the ecosystem. Its `InputSet` classes generate standardized inputs following Materials Project conventions.

**Full I/O modules:** VASP (most extensive), ABINIT, Q-Chem, CP2K, Gaussian, FEFF, LAMMPS, Lobster, NWChem, JDFTx, EXCITING, ADF, PWmat, XTB

**Input generation (VASP example):**
```python
from pymatgen.core import Structure
from pymatgen.io.vasp.sets import MPRelaxSet

structure = Structure.from_file("POSCAR")
input_set = MPRelaxSet(structure)
input_set.write_input("./calc_dir")  # Writes INCAR, POSCAR, KPOINTS, POTCAR
```

**Output parsing extracts:** energies (all ionic steps), DOS, band structures, dielectric tensors, elastic constants, Born effective charges, magnetization, and projected orbital data via `Vasprun` and `Outcar` classes.

---

### cclib (Computational Chemistry Library)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/cclib/cclib |
| **PyPI** | `cclib` |
| **Version** | 1.8.1 (v2.0 in development) |
| **License** | BSD-3 |

cclib specializes in **output parsing only**—it does not generate inputs. Its strength lies in extracting **TD-DFT excited state data** and molecular orbital information across molecular codes.

**Supported codes:** Gaussian (09/16), ORCA (4.x/5.0), Q-Chem (5.x/6.0), NWChem, Turbomole, ADF, DALTON, Firefly, GAMESS, Jaguar, Molcas, Molpro, MOPAC, NBO, Psi4

**Parsed data for TDDFT:**
```python
import cclib
data = cclib.io.ccread("calculation.log")

# TDDFT-specific attributes
data.etenergies   # Excitation energies (cm⁻¹)
data.etoscs       # Oscillator strengths
data.etsecs       # Transition configurations
data.etsyms       # Excited state symmetries
```

**Additional extracted data:** MO energies/coefficients, atomic charges (Mulliken/Löwdin), vibrational frequencies, thermochemistry, dipole moments, and geometry optimization trajectories.

---

### AiiDA (Automated Interactive Infrastructure)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/aiidateam/aiida-core |
| **PyPI** | `aiida-core` |
| **Version** | 2.7.0 |
| **License** | MIT |

AiiDA is a **workflow framework** with automatic provenance tracking rather than a direct I/O library. All calculations are stored in a PostgreSQL database with complete lineage.

**Plugin ecosystem (70+ plugins):** Quantum ESPRESSO, SIESTA, FLEUR, CP2K, BigDFT, Yambo (official); VASP, Gaussian, ORCA, NWChem, FHI-aims, CRYSTAL, CASTEP, Wannier90, GPAW, ABINIT (community)

**I/O paradigm:**
```python
from aiida import orm
from aiida.plugins import CalculationFactory

PwCalculation = CalculationFactory('quantumespresso.pw')
builder = PwCalculation.get_builder()
builder.parameters = orm.Dict(dict={
    'CONTROL': {'calculation': 'scf'},
    'SYSTEM': {'ecutwfc': 30}
})
```

---

## Code-specific Python interfaces for major DFT engines

These packages target individual codes with deeper integration than universal libraries provide.

### VASP interfaces

| Package | Repository | Purpose | Input Gen | Output Parse |
|---------|-----------|---------|-----------|--------------|
| **pymatgen.io.vasp** | github.com/materialsproject/pymatgen | Complete I/O | ✓ Full | ✓ Full |
| **py4vasp** | github.com/vasp-dev/py4vasp | Official HDF5 interface | Limited | ✓ HDF5 |
| **custodian** | github.com/materialsproject/custodian | Error handling | Modifies | Monitors |
| **VASProcar** | PyPI: vasprocar | Post-processing | — | ✓ PROCAR |
| **ipyvasp** | PyPI: ipyvasp | Jupyter integration | ✓ | ✓ |
| **vasp-manager** | PyPI: vasp-manager | HT management | ✓ | ✓ |

**py4vasp** (official VASP interface) reads the new HDF5 output format in VASP 6+:
```python
from py4vasp import Calculation
calc = Calculation.from_path("/path/to/calculation")
calc.dos.plot()
calc.energy.read()  # Returns pandas DataFrame
```

---

### Quantum ESPRESSO interfaces

| Package | Repository | Purpose |
|---------|-----------|---------|
| **QEpy** | gitlab.com/shaoxc/qepy | Embeds QE as Python library |
| **qe-tools** | github.com/aiidateam/qe-tools | Input validation/parsing |
| **aiida-quantumespresso** | github.com/aiidateam | AiiDA plugin (most mature) |
| **aseqe** | PyPI: aseqe | ASE calculator wrapper |

**QEpy** turns Quantum ESPRESSO into a Python-callable DFT engine:
```python
from qepy.calculator import QEpyCalculator
calc = QEpyCalculator(inputfile='pw.in')
calc.scf()  # Run SCF directly from Python
```

---

### Other code-specific packages

| Code | Package | Repository | Key Features |
|------|---------|-----------|--------------|
| **GPAW** | Built-in | gitlab.com/gpaw/gpaw | Native Python; ASE calculator |
| **CP2K** | cp2k-input-tools | github.com/cp2k/cp2k-input-tools | XML schema validation |
| **SIESTA** | sisl | github.com/zerothi/sisl | Hamiltonians, NEGF, TBtrans |
| **ABINIT** | abipy | github.com/abinit/abipy | Complete workflow + analysis |
| **ORCA** | OPI | github.com/faccts/opi | Official Python interface (6.1+) |
| **FHI-aims** | aimstools | github.com/romankempt/aimstools | Band structure analysis |

**sisl** deserves special mention for SIESTA users—it reads Hamiltonians directly and performs transport calculations:
```python
import sisl
H = sisl.get_sile('RUN.fdf').read_hamiltonian()
mp = sisl.MonkhorstPack(H, [13, 13, 13])
DOS = mp.apply.average.DOS(E)
```

---

## TDDFT-specific tools span simulation and analysis

### LITESOPH (Layer Integrated Toolkit for Simulations of Photo-induced Phenomena)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/AITGCODES/litesoph |
| **Purpose** | GUI-based RT-TDDFT workflows |
| **Codes** | GPAW, NWChem, Octopus |

LITESOPH provides a **graphical workflow interface** for real-time TDDFT calculations, including ground-state DFT → RT-TDDFT → spectrum generation pipelines. Key analysis features include Kohn-Sham Decomposition (KSD), Transition Contribution Maps (TCM), and MO population tracking.

---

### Native TDDFT modules in DFT codes

| Code | Capability | Python Access |
|------|------------|---------------|
| **GPAW** | RT-TDDFT, LR-TDDFT, BSE | `gpaw.tddft.TDDFT`, `gpaw.tddft.spectrum` |
| **PySCF** | LR-TDDFT, TDA, RT-TDDFT (periodic) | `pyscf.tddft.TDDFT`, NTO analysis |
| **Octopus** | RT-TDDFT, LR-TDDFT | ASE calculator, octopy wrapper |
| **NWChem** | RT-TDDFT, LR-TDDFT | Built-in Python, `nw_spectrum.py` |

**GPAW TDDFT example:**
```python
from gpaw.tddft import TDDFT
from gpaw.tddft.spectrum import photoabsorption_spectrum

td_calc = TDDFT('ground_state.gpw')
td_calc.absorption_kick(kick_strength=[1e-3, 0, 0])
td_calc.propagate(time_step=10, iterations=2000, dipole_moment_file='dm.dat')
photoabsorption_spectrum('dm.dat', 'spectrum.dat')
```

**PySCF TDDFT with NTO analysis:**
```python
from pyscf import gto, dft, tddft
mf = dft.RKS(mol).run()
mytd = tddft.TDDFT(mf)
mytd.nstates = 10
mytd.kernel()
weights, nto = mytd.get_nto(state=1)  # Natural Transition Orbitals
```

---

### Excited-state analysis packages

| Package | Repository | Purpose | Codes Supported |
|---------|-----------|---------|-----------------|
| **TheoDORE** | github.com/felixplasser/theodore-qc | Fragment analysis, NTOs, CT numbers | Columbus, Turbomole, Q-Chem, Gaussian, ORCA, Molcas, Molpro, ADF, DFTB+, MRCC |
| **cclib** | github.com/cclib/cclib | Parse excited states | Gaussian, ORCA, Q-Chem, NWChem, Turbomole |
| **rhodent** | New (2025) | RT-TDDFT post-processing | GPAW |
| **TDDFT-ris** | github.com/John-zzh/pyscf_TDDFT_ris | Fast semiempirical TDDFT | PySCF backend |
| **PySOC** | github.com/gaox-qd/pysoc | Spin-orbit coupling | Gaussian, DFTB+ |

**TheoDORE** provides automated excited-state characterization:
```bash
theodore analyze_tden  # Transition density analysis
theodore plot_omfrag   # Fragment charge-transfer visualization
```

---

## Post-processing and analysis tools handle specialized workflows

### Defect calculations

| Package | Repository | Codes | Key Features |
|---------|-----------|-------|--------------|
| **doped** | github.com/SMTG-Bham/doped | VASP, FHI-aims, CP2K, QE, CASTEP | Supercell generation, finite-size corrections, formation energies |
| **ShakeNBreak** | PyPI: shakenbreak | Same as doped | Bond-distortion structure searching |
| **pydefect** | PyPI: pydefect | VASP | Point defect eigenvalue analysis |

**doped workflow:**
```python
from doped.generation import DefectsGenerator
from pymatgen.core import Structure

host = Structure.from_file("POSCAR")
defect_gen = DefectsGenerator(host)
defect_gen.generate()  # Creates all symmetry-inequivalent defects
```

---

### Electronic structure analysis

| Package | Purpose | Key Methods |
|---------|---------|-------------|
| **sisl** | Tight-binding, NEGF transport | Hamiltonian extraction, DOS, transmission |
| **Lobster (pymatgen.io.lobster)** | Chemical bonding analysis | COHP, COOP, Mulliken charges |
| **BoltzTraP2** | Transport properties | Seebeck, conductivity from band structure |
| **wannier90 interfaces** | Wannier functions | MLWFs, band interpolation |

---

## Workflow and automation frameworks manage high-throughput calculations

### Materials Project ecosystem stack

The Materials Project tools form an integrated stack:

```
pymatgen (I/O) → custodian (error handling) → jobflow (workflow definition) 
    → FireWorks (execution) → atomate2 (pre-built workflows) → MongoDB
```

| Package | Repository | Role | Status |
|---------|-----------|------|--------|
| **atomate2** | github.com/materialsproject/atomate2 | Pre-built workflows | Very active (v0.0.21) |
| **jobflow** | github.com/materialsproject/jobflow | Lightweight workflow library | Active (v0.2.0) |
| **FireWorks** | github.com/materialsproject/fireworks | Workflow execution engine | Stable (v2.0.4) |
| **custodian** | github.com/materialsproject/custodian | Error detection/correction | Active |

**atomate2 example:**
```python
from atomate2.vasp.jobs.core import RelaxMaker
from jobflow import run_locally

relax_job = RelaxMaker().make(structure)
run_locally(relax_job)
```

---

### Alternative workflow frameworks

| Package | Repository | Distinguishing Feature |
|---------|-----------|----------------------|
| **AiiDA** | github.com/aiidateam/aiida-core | Full provenance tracking, PostgreSQL |
| **pyiron** | github.com/pyiron/pyiron | IDE approach, Jupyter integration |
| **signac** | github.com/glotzerlab/signac-flow | Flexible parameter studies |
| **quacc** | github.com/Quantum-Accelerators/quacc | Multi-code, big-data focus |
| **DFTTK** | dfttk.org | Thermodynamic calculations |

**pyiron integrated environment:**
```python
from pyiron import Project
pr = Project("my_calculations")
job = pr.create_job(pr.job_type.Vasp, "relaxation")
job.structure = structure
job.run()
```

---

## Structure and crystal manipulation tools

### Symmetry and k-paths

| Package | Repository | Functionality |
|---------|-----------|---------------|
| **spglib** | github.com/spglib/spglib | Space group detection, primitive cells, irreducible k-mesh |
| **SeeK-path** | github.com/giovannipizzi/seekpath | High-symmetry k-paths for band structures |

**spglib symmetry analysis:**
```python
import spglib
spacegroup = spglib.get_spacegroup(cell, symprec=1e-5)
symmetry = spglib.get_symmetry_dataset(cell)
primitive = spglib.standardize_cell(cell, to_primitive=True)
```

---

### Structure generation and manipulation

| Package | Repository | Capabilities |
|---------|-----------|--------------|
| **phonopy** | github.com/phonopy/phonopy | Supercells with displacements for phonons |
| **PyXtal** | github.com/MaterSim/PyXtal | Random crystal generation with symmetry |
| **pymatgen** | Slab/surface generation | `SlabGenerator`, `DefectGenerator` |
| **JARVIS-tools** | github.com/usnistgov/jarvis | Database access (75k+ materials), heterostructures |

**PyXtal random structure generation:**
```python
from pyxtal import pyxtal
crystal = pyxtal()
crystal.from_random(3, 225, ['C'], [12])  # 3D, Fm-3m, carbon, 12 atoms
```

---

### Visualization and description

| Package | Repository | Purpose |
|---------|-----------|---------|
| **Crystal Toolkit** | github.com/materialsproject/crystaltoolkit | Web visualization (powers Materials Project) |
| **Robocrystallographer** | github.com/hackingmaterials/robocrystallographer | Auto-generated text descriptions |
| **ASE GUI** | Built into ASE | Interactive structure viewer |

---

## Lesser-known packages from research groups warrant attention

Several actively maintained packages from university groups address specialized needs:

| Package | Developer | Purpose | Repository |
|---------|-----------|---------|-----------|
| **DFTpy** | Rutgers (Pavanello) | Orbital-free DFT | gitlab.com/shaoxc/dftpy |
| **QEpy** | Rutgers/Sandia | QE as Python library | gitlab.com/shaoxc/qepy |
| **rhodent** | Chalmers (Erhart) | RT-TDDFT post-processing | 2025 publication |
| **doped/ShakeNBreak** | Birmingham (Scanlon) | Defect workflows | JOSS 2024 |
| **sisl** | DTU (Papior) | NEGF transport | github.com/zerothi/sisl |
| **eminus** | Active dev | Minimal plane-wave DFT | PyPI |
| **IoData** | theochem | Universal file parser | github.com/theochem/iodata |

**MolSSI ecosystem** provides infrastructure packages: QCEngine (executor), QCArchive (data infrastructure), basis_set_exchange (basis sets), and QCSchema (standardized format).

---

## Choosing packages by use case

**For multi-code workflows:** Start with ASE calculators + pymatgen I/O; add atomate2/jobflow for automation

**For VASP-centric work:** pymatgen.io.vasp (input sets) + py4vasp (HDF5 output) + custodian (error handling)

**For TDDFT simulations:** LITESOPH (GUI workflows) or native code modules (GPAW, PySCF); TheoDORE or cclib for analysis

**For parsing molecular calculations:** cclib provides the most complete excited-state data extraction

**For high-throughput with provenance:** AiiDA with appropriate plugins; PostgreSQL backend

**For defect calculations:** doped + ShakeNBreak ecosystem; integrates with multiple codes

**For transport properties:** sisl for SIESTA/TBtrans; BoltzTraP2 for thermoelectrics

All major packages listed support Python 3.8+ and are installable via pip or conda-forge. Most have been updated within the past year, with the Materials Project ecosystem (pymatgen, atomate2, jobflow) and AiiDA ecosystem seeing the most active development as of late 2025.