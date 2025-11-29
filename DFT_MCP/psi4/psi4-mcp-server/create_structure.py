#!/usr/bin/env python3
"""
Psi4 MCP Server - Create All Files and Folders
Creates the complete 380+ file structure from psi4_mcp_complete_tree.txt
Version: 3.0 - Python Version (FASTER & MORE RELIABLE)
Date: 2025-11-29
"""

import os
import sys
from pathlib import Path

# Template content for different file types
TEMPLATES = {
    "py": '''"""
Psi4 MCP Server - Placeholder Module

This file is part of the Psi4 MCP Server implementation.
TODO: Implement according to psi4_mcp_comprehensive_plan.md
"""

# TODO: Add implementation
pass
''',
    "md": '''# Placeholder Documentation

TODO: Add documentation content

## Overview

This document is part of the Psi4 MCP Server documentation.

## Content

To be added during implementation.
''',
    "yaml": '''# Psi4 MCP Server Configuration
# TODO: Add configuration settings
''',
    "toml": '''# Psi4 MCP Server Configuration
# TODO: Add TOML configuration
''',
    "txt": "# Placeholder file - TODO: Add content\n",
    "sh": '''#!/bin/bash
# Psi4 MCP Server Script
# TODO: Implement script functionality

echo "TODO: Implement this script"
''',
    "json": "{}",
    "bib": "% Placeholder bibliography file\n",
    "conf": "# Supervisor configuration placeholder\n",
    "service": "[Unit]\n# Systemd service placeholder\n",
    "ipynb": '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}',
}

def create_file(filepath, filetype="txt"):
    """Create a file with appropriate template content."""
    path = Path(filepath)
    
    # Create parent directories
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Only create if doesn't exist
    if path.exists():
        return False
    
    # Get template or use empty
    content = TEMPLATES.get(filetype, "")
    
    # Write file
    path.write_text(content)
    
    # Make shell scripts executable
    if filetype == "sh":
        path.chmod(0o755)
    
    return True

def main():
    # Ensure we're in psi4-mcp-server directory
    if not os.path.basename(os.getcwd()).endswith("psi4-mcp-server"):
        print("Error: Must run from psi4-mcp-server directory")
        sys.exit(1)
    
    print("=" * 50)
    print("Creating All Files and Folders")
    print("=" * 50)
    print()
    
    file_count = 0
    
    # All directories to create
    directories = [
        ".github/ISSUE_TEMPLATE",
        ".github/workflows",
        "benchmarks/accuracy",
        "benchmarks/performance",
        "benchmarks/results",
        "config",
        "data/basis_sets/dunning",
        "data/basis_sets/karlsruhe",
        "data/basis_sets/pople",
        "data/basis_sets/sto",
        "data/literature",
        "data/molecules/benchmarks",
        "data/molecules/common",
        "data/molecules/test_set",
        "data/parameters",
        "data/reference_data",
        "deployment/helm/psi4-mcp/templates",
        "deployment/kubernetes",
        "deployment/supervisor",
        "deployment/systemd",
        "docs/assets/screenshots",
        "docs/api-reference",
        "docs/developer-guide",
        "docs/examples",
        "docs/getting-started",
        "docs/theory",
        "docs/user-guide",
        "examples/molecules/cif",
        "examples/molecules/pdb",
        "examples/molecules/xyz",
        "examples/notebooks",
        "examples/python/advanced",
        "examples/python/basic",
        "examples/python/intermediate",
        "examples/python/workflows",
        "notebooks/development",
        "notebooks/exploration",
        "notebooks/presentations",
        "scripts",
        "src/psi4_mcp/cli/commands",
        "src/psi4_mcp/database/migrations",
        "src/psi4_mcp/integrations",
        "src/psi4_mcp/models/calculations",
        "src/psi4_mcp/models/enums",
        "src/psi4_mcp/models/outputs",
        "src/psi4_mcp/prompts",
        "src/psi4_mcp/resources",
        "src/psi4_mcp/scripts",
        "src/psi4_mcp/tools/advanced",
        "src/psi4_mcp/tools/analysis",
        "src/psi4_mcp/tools/basis_sets",
        "src/psi4_mcp/tools/composite",
        "src/psi4_mcp/tools/configuration_interaction",
        "src/psi4_mcp/tools/core",
        "src/psi4_mcp/tools/coupled_cluster",
        "src/psi4_mcp/tools/dft",
        "src/psi4_mcp/tools/excited_states",
        "src/psi4_mcp/tools/mcscf",
        "src/psi4_mcp/tools/perturbation_theory",
        "src/psi4_mcp/tools/properties/bonds",
        "src/psi4_mcp/tools/properties/charges",
        "src/psi4_mcp/tools/sapt",
        "src/psi4_mcp/tools/solvation",
        "src/psi4_mcp/tools/spectroscopy/epr",
        "src/psi4_mcp/tools/spectroscopy/nmr",
        "src/psi4_mcp/tools/utilities",
        "src/psi4_mcp/tools/vibrational",
        "src/psi4_mcp/utils/basis",
        "src/psi4_mcp/utils/caching",
        "src/psi4_mcp/utils/convergence",
        "src/psi4_mcp/utils/conversion",
        "src/psi4_mcp/utils/error_handling",
        "src/psi4_mcp/utils/geometry",
        "src/psi4_mcp/utils/helpers",
        "src/psi4_mcp/utils/logging",
        "src/psi4_mcp/utils/memory",
        "src/psi4_mcp/utils/molecular",
        "src/psi4_mcp/utils/parallel",
        "src/psi4_mcp/utils/parsing",
        "src/psi4_mcp/utils/validation",
        "src/psi4_mcp/utils/visualization",
        "tests/fixtures/test_files",
        "tests/integration",
        "tests/performance",
        "tests/regression",
        "tests/unit/tools",
        "tests/unit/utils",
    ]
    
    print(f"Creating {len(directories)} directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"✓ All directories created\n")
    
    # All files to create - organized by category
    files_to_create = [
        # Top-level files
        ("pyproject.toml", "toml"),
        ("setup.py", "py"),
        ("requirements.txt", "txt"),
        ("requirements-dev.txt", "txt"),
        ("requirements-optional.txt", "txt"),
        ("CHANGELOG.md", "md"),
        ("CODE_OF_CONDUCT.md", "md"),
        ("CONTRIBUTING.md", "md"),
        ("LICENSE", "txt"),
        ("README.md", "md"),
        ("Dockerfile", "txt"),
        ("docker-compose.yml", "yaml"),
        (".gitattributes", "txt"),
        (".gitignore", "txt"),
        (".env.example", "txt"),
        
        # GitHub
        (".github/PULL_REQUEST_TEMPLATE.md", "md"),
        (".github/ISSUE_TEMPLATE/bug_report.md", "md"),
        (".github/ISSUE_TEMPLATE/feature_request.md", "md"),
        (".github/ISSUE_TEMPLATE/question.md", "md"),
        (".github/workflows/build.yml", "yaml"),
        (".github/workflows/docs.yml", "yaml"),
        (".github/workflows/lint.yml", "yaml"),
        (".github/workflows/publish.yml", "yaml"),
        (".github/workflows/test.yml", "yaml"),
        
        # Config
        ("config/default.yaml", "yaml"),
        ("config/development.yaml", "yaml"),
        ("config/production.yaml", "yaml"),
        ("config/testing.yaml", "yaml"),
        ("config/logging.yaml", "yaml"),
        
        # Scripts
        ("scripts/build_docker.sh", "sh"),
        ("scripts/cleanup.sh", "sh"),
        ("scripts/deploy.sh", "sh"),
        ("scripts/generate_docs.sh", "sh"),
        ("scripts/install.sh", "sh"),
        ("scripts/run_tests.sh", "sh"),
        ("scripts/setup_conda.sh", "sh"),
    ]
    
    # Add src/psi4_mcp core files
    files_to_create.extend([
        ("src/psi4_mcp/__init__.py", "py"),
        ("src/psi4_mcp/__version__.py", "py"),
        ("src/psi4_mcp/config.py", "py"),
        ("src/psi4_mcp/server.py", "py"),
        ("src/psi4_mcp/cli/__init__.py", "py"),
        ("src/psi4_mcp/cli/main.py", "py"),
        ("src/psi4_mcp/cli/utils.py", "py"),
        ("src/psi4_mcp/cli/commands/__init__.py", "py"),
        ("src/psi4_mcp/cli/commands/convert.py", "py"),
        ("src/psi4_mcp/cli/commands/start.py", "py"),
        ("src/psi4_mcp/cli/commands/test.py", "py"),
        ("src/psi4_mcp/cli/commands/validate.py", "py"),
        ("src/psi4_mcp/database/__init__.py", "py"),
        ("src/psi4_mcp/database/manager.py", "py"),
        ("src/psi4_mcp/database/queries.py", "py"),
        ("src/psi4_mcp/database/schema.py", "py"),
        ("src/psi4_mcp/database/migrations/__init__.py", "py"),
        ("src/psi4_mcp/database/migrations/v001_initial.py", "py"),
        ("src/psi4_mcp/integrations/__init__.py", "py"),
        ("src/psi4_mcp/integrations/ase.py", "py"),
        ("src/psi4_mcp/integrations/cclib.py", "py"),
        ("src/psi4_mcp/integrations/molssi.py", "py"),
        ("src/psi4_mcp/integrations/openbabel.py", "py"),
        ("src/psi4_mcp/integrations/qcschema.py", "py"),
        ("src/psi4_mcp/integrations/rdkit.py", "py"),
        ("src/psi4_mcp/models/__init__.py", "py"),
        ("src/psi4_mcp/models/base.py", "py"),
        ("src/psi4_mcp/models/errors.py", "py"),
        ("src/psi4_mcp/models/molecules.py", "py"),
        ("src/psi4_mcp/models/options.py", "py"),
        ("src/psi4_mcp/models/resources.py", "py"),
        ("src/psi4_mcp/models/calculations/__init__.py", "py"),
        ("src/psi4_mcp/models/calculations/configuration_interaction.py", "py"),
        ("src/psi4_mcp/models/calculations/coupled_cluster.py", "py"),
        ("src/psi4_mcp/models/calculations/energy.py", "py"),
        ("src/psi4_mcp/models/calculations/frequencies.py", "py"),
        ("src/psi4_mcp/models/calculations/mcscf.py", "py"),
        ("src/psi4_mcp/models/calculations/optimization.py", "py"),
        ("src/psi4_mcp/models/calculations/properties.py", "py"),
        ("src/psi4_mcp/models/calculations/response.py", "py"),
        ("src/psi4_mcp/models/calculations/sapt.py", "py"),
        ("src/psi4_mcp/models/calculations/solvation.py", "py"),
        ("src/psi4_mcp/models/calculations/tddft.py", "py"),
        ("src/psi4_mcp/models/enums/__init__.py", "py"),
        ("src/psi4_mcp/models/enums/basis_sets.py", "py"),
        ("src/psi4_mcp/models/enums/methods.py", "py"),
        ("src/psi4_mcp/models/enums/properties.py", "py"),
        ("src/psi4_mcp/models/enums/references.py", "py"),
        ("src/psi4_mcp/models/outputs/__init__.py", "py"),
        ("src/psi4_mcp/models/outputs/analysis.py", "py"),
        ("src/psi4_mcp/models/outputs/coupled_cluster.py", "py"),
        ("src/psi4_mcp/models/outputs/energy.py", "py"),
        ("src/psi4_mcp/models/outputs/frequencies.py", "py"),
        ("src/psi4_mcp/models/outputs/optimization.py", "py"),
        ("src/psi4_mcp/models/outputs/orbitals.py", "py"),
        ("src/psi4_mcp/models/outputs/properties.py", "py"),
        ("src/psi4_mcp/models/outputs/sapt.py", "py"),
        ("src/psi4_mcp/models/outputs/spectrum.py", "py"),
        ("src/psi4_mcp/models/outputs/tddft.py", "py"),
        ("src/psi4_mcp/prompts/__init__.py", "py"),
        ("src/psi4_mcp/prompts/education.py", "py"),
        ("src/psi4_mcp/prompts/methods.py", "py"),
        ("src/psi4_mcp/prompts/troubleshooting.py", "py"),
        ("src/psi4_mcp/prompts/workflows.py", "py"),
        ("src/psi4_mcp/resources/__init__.py", "py"),
        ("src/psi4_mcp/resources/basis_sets.py", "py"),
        ("src/psi4_mcp/resources/benchmarks.py", "py"),
        ("src/psi4_mcp/resources/functionals.py", "py"),
        ("src/psi4_mcp/resources/literature.py", "py"),
        ("src/psi4_mcp/resources/methods.py", "py"),
        ("src/psi4_mcp/resources/molecules.py", "py"),
        ("src/psi4_mcp/resources/tutorials.py", "py"),
        ("src/psi4_mcp/scripts/__init__.py", "py"),
        ("src/psi4_mcp/scripts/benchmark.py", "py"),
        ("src/psi4_mcp/scripts/generate_docs.py", "py"),
        ("src/psi4_mcp/scripts/install_deps.py", "py"),
        ("src/psi4_mcp/scripts/setup_env.py", "py"),
    ])
    
    # Tools files
    tools_core = [
        ("src/psi4_mcp/tools/__init__.py", "py"),
        ("src/psi4_mcp/tools/core/__init__.py", "py"),
        ("src/psi4_mcp/tools/core/energy.py", "py"),
        ("src/psi4_mcp/tools/core/gradient.py", "py"),
        ("src/psi4_mcp/tools/core/hessian.py", "py"),
        ("src/psi4_mcp/tools/core/optimization.py", "py"),
    ]
    files_to_create.extend(tools_core)
    
    # Add all tool categories
    tool_categories = [
        ("vibrational", ["anharmonic", "frequencies", "thermochemistry", "vcd"]),
        ("properties", ["bonds", "electric_moments", "electrostatic", "optical_rotation", "orbitals", "polarizability", "spin_properties"]),
        ("spectroscopy", ["ecd", "ir_raman", "ord", "uv_vis"]),
        ("excited_states", ["adc", "cis", "eom_cc", "excited_opt", "tda", "tddft", "transition_properties"]),
        ("coupled_cluster", ["brueckner", "cc2", "cc3", "ccsd", "ccsd_t", "ccsdt", "eom_ccsd", "lr_ccsd"]),
        ("perturbation_theory", ["df_mp2", "mp2", "mp2_5", "mp3", "mp4", "scs_mp2"]),
        ("configuration_interaction", ["cisd", "cisdt", "detci", "fci"]),
        ("mcscf", ["casscf", "mcscf_gradients", "rasscf"]),
        ("sapt", ["analysis", "fisapt", "sapt0", "sapt2", "sapt2_plus", "sapt2_plus_3", "sapt_dft"]),
        ("solvation", ["cpcm", "ddcosmo", "iefpcm", "pcm", "smd"]),
        ("dft", ["dispersion", "functional_scan", "grid_quality", "range_separated"]),
        ("basis_sets", ["basis_info", "composite", "extrapolation"]),
        ("analysis", ["cube_files", "fragment_analysis", "localization", "natural_orbitals", "population", "wavefunction"]),
        ("composite", ["cbs_qb3", "g1", "g2", "g3", "g4", "w1"]),
        ("advanced", ["constrained", "efp", "oniom", "qmmm", "scan", "symmetry"]),
        ("utilities", ["batch_runner", "format_converter", "structure_builder", "workflow_manager"]),
    ]
    
    for category, files in tool_categories:
        files_to_create.append((f"src/psi4_mcp/tools/{category}/__init__.py", "py"))
        for fname in files:
            files_to_create.append((f"src/psi4_mcp/tools/{category}/{fname}.py", "py"))
    
    # Sub-categories
    files_to_create.extend([
        ("src/psi4_mcp/tools/properties/bonds/__init__.py", "py"),
        ("src/psi4_mcp/tools/properties/bonds/mayer.py", "py"),
        ("src/psi4_mcp/tools/properties/bonds/wiberg.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/__init__.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/esp.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/hirshfeld.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/lowdin.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/mulliken.py", "py"),
        ("src/psi4_mcp/tools/properties/charges/npa.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/epr/__init__.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/epr/g_tensor.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/epr/hyperfine.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/epr/zero_field.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/nmr/__init__.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/nmr/coupling.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/nmr/shielding.py", "py"),
        ("src/psi4_mcp/tools/spectroscopy/nmr/spectra.py", "py"),
    ])
    
    # Utils files
    util_categories = [
        ("basis", ["generator", "library", "optimizer", "parser"]),
        ("caching", ["cache_manager", "molecular", "results"]),
        ("convergence", ["optimization", "scf", "strategies", "tddft"]),
        ("conversion", ["basis_sets", "geometry", "output", "units"]),
        ("error_handling", ["categorization", "detection", "logging", "recovery", "suggestions"]),
        ("geometry", ["alignment", "analysis", "builders", "symmetry", "transformations"]),
        ("helpers", ["constants", "math_utils", "string_utils", "units"]),
        ("logging", ["formatters", "handlers", "logger"]),
        ("memory", ["estimator", "manager", "optimizer"]),
        ("molecular", ["database", "descriptors", "fingerprints", "similarity"]),
        ("parallel", ["mpi_interface", "task_queue", "thread_manager"]),
        ("parsing", ["energy", "frequencies", "generic", "optimization", "orbitals", "properties", "wavefunction"]),
        ("validation", ["basis_sets", "constraints", "geometry", "methods", "options"]),
        ("visualization", ["molecular", "orbitals", "spectra", "surfaces"]),
    ]
    
    files_to_create.append(("src/psi4_mcp/utils/__init__.py", "py"))
    for category, utils in util_categories:
        files_to_create.append((f"src/psi4_mcp/utils/{category}/__init__.py", "py"))
        for util in utils:
            files_to_create.append((f"src/psi4_mcp/utils/{category}/{util}.py", "py"))
    
    # Data files
    data_files = [
        ("data/basis_sets/dunning/cc-pVDZ.gbs", "gbs"),
        ("data/basis_sets/dunning/cc-pVQZ.gbs", "gbs"),
        ("data/basis_sets/dunning/cc-pVTZ.gbs", "gbs"),
        ("data/basis_sets/dunning/cc-pV5Z.gbs", "gbs"),
        ("data/basis_sets/karlsruhe/def2-SVP.gbs", "gbs"),
        ("data/basis_sets/karlsruhe/def2-TZVP.gbs", "gbs"),
        ("data/basis_sets/karlsruhe/def2-QZVP.gbs", "gbs"),
        ("data/basis_sets/pople/3-21G.gbs", "gbs"),
        ("data/basis_sets/pople/6-31G.gbs", "gbs"),
        ("data/basis_sets/pople/6-311G.gbs", "gbs"),
        ("data/basis_sets/pople/6-311++G.gbs", "gbs"),
        ("data/basis_sets/sto/STO-3G.gbs", "gbs"),
        ("data/literature/benchmarks.json", "json"),
        ("data/literature/citations.bib", "bib"),
        ("data/molecules/benchmarks/g2_set.xyz", "txt"),
        ("data/molecules/benchmarks/s22_set.xyz", "txt"),
        ("data/molecules/benchmarks/s66_set.xyz", "txt"),
        ("data/molecules/common/benzene.xyz", "txt"),
        ("data/molecules/common/ethane.xyz", "txt"),
        ("data/molecules/common/methane.xyz", "txt"),
        ("data/molecules/common/water.xyz", "txt"),
        ("data/molecules/common/ammonia.xyz", "txt"),
        ("data/molecules/test_set/test_molecule_1.xyz", "txt"),
        ("data/molecules/test_set/test_molecule_2.xyz", "txt"),
        ("data/molecules/test_set/test_molecule_3.xyz", "txt"),
        ("data/parameters/dispersion_parameters.json", "json"),
        ("data/parameters/functional_parameters.json", "json"),
        ("data/parameters/solvation_parameters.json", "json"),
        ("data/reference_data/energies.json", "json"),
        ("data/reference_data/frequencies.json", "json"),
        ("data/reference_data/geometries.json", "json"),
        ("data/reference_data/properties.json", "json"),
    ]
    files_to_create.extend(data_files)
    
    # Benchmarks
    files_to_create.extend([
        ("benchmarks/__init__.py", "py"),
        ("benchmarks/accuracy/__init__.py", "py"),
        ("benchmarks/accuracy/energies.py", "py"),
        ("benchmarks/accuracy/geometries.py", "py"),
        ("benchmarks/accuracy/properties.py", "py"),
        ("benchmarks/performance/__init__.py", "py"),
        ("benchmarks/performance/execution_time.py", "py"),
        ("benchmarks/performance/memory_usage.py", "py"),
        ("benchmarks/performance/parallel_scaling.py", "py"),
        ("benchmarks/results/.gitkeep", "txt"),
        ("benchmarks/results/accuracy_results.json", "json"),
        ("benchmarks/results/performance_results.json", "json"),
    ])
    
    # Examples
    examples_files = [
        ("examples/molecules/cif/nacl.cif", "txt"),
        ("examples/molecules/cif/quartz.cif", "txt"),
        ("examples/molecules/pdb/1abc.pdb", "txt"),
        ("examples/molecules/pdb/protein.pdb", "txt"),
        ("examples/molecules/xyz/benzene.xyz", "txt"),
        ("examples/molecules/xyz/ethane.xyz", "txt"),
        ("examples/molecules/xyz/water.xyz", "txt"),
        ("examples/notebooks/tutorial_1_basics.ipynb", "ipynb"),
        ("examples/notebooks/tutorial_2_properties.ipynb", "ipynb"),
        ("examples/notebooks/tutorial_3_advanced.ipynb", "ipynb"),
        ("examples/python/basic/01_water_energy.py", "py"),
        ("examples/python/basic/02_methane_opt.py", "py"),
        ("examples/python/basic/03_co2_frequencies.py", "py"),
        ("examples/python/basic/04_benzene_properties.py", "py"),
        ("examples/python/intermediate/05_uv_vis_spectrum.py", "py"),
        ("examples/python/intermediate/06_hydrogen_bond_sapt.py", "py"),
        ("examples/python/intermediate/07_reaction_energy.py", "py"),
        ("examples/python/intermediate/08_conformation_scan.py", "py"),
        ("examples/python/advanced/09_excited_state_opt.py", "py"),
        ("examples/python/advanced/10_nmr_shielding.py", "py"),
        ("examples/python/advanced/11_pcm_solvation.py", "py"),
        ("examples/python/advanced/12_multi_reference.py", "py"),
        ("examples/python/workflows/complete_characterization.py", "py"),
        ("examples/python/workflows/high_throughput.py", "py"),
        ("examples/python/workflows/reaction_pathway.py", "py"),
    ]
    files_to_create.extend(examples_files)
    
    # Notebooks
    notebooks_files = [
        ("notebooks/development/error_analysis.ipynb", "ipynb"),
        ("notebooks/development/performance_profiling.ipynb", "ipynb"),
        ("notebooks/development/validation_testing.ipynb", "ipynb"),
        ("notebooks/exploration/basis_set_comparison.ipynb", "ipynb"),
        ("notebooks/exploration/functional_benchmarking.ipynb", "ipynb"),
        ("notebooks/exploration/method_accuracy.ipynb", "ipynb"),
        ("notebooks/presentations/demo.ipynb", "ipynb"),
        ("notebooks/presentations/tutorial.ipynb", "ipynb"),
    ]
    files_to_create.extend(notebooks_files)
    
    # Deployment
    deployment_files = [
        ("deployment/helm/psi4-mcp/Chart.yaml", "yaml"),
        ("deployment/helm/psi4-mcp/values.yaml", "yaml"),
        ("deployment/helm/psi4-mcp/templates/deployment.yaml", "yaml"),
        ("deployment/helm/psi4-mcp/templates/service.yaml", "yaml"),
        ("deployment/helm/psi4-mcp/templates/configmap.yaml", "yaml"),
        ("deployment/kubernetes/configmap.yaml", "yaml"),
        ("deployment/kubernetes/deployment.yaml", "yaml"),
        ("deployment/kubernetes/service.yaml", "yaml"),
        ("deployment/supervisor/psi4-mcp.conf", "conf"),
        ("deployment/systemd/psi4-mcp.service", "service"),
    ]
    files_to_create.extend(deployment_files)
    
    # Documentation
    docs_files = [
        ("docs/index.md", "md"),
        ("docs/assets/.gitkeep", "txt"),
        ("docs/assets/architecture_diagram.png", "txt"),
        ("docs/assets/logo.png", "txt"),
        ("docs/assets/screenshots/.gitkeep", "txt"),
        ("docs/api-reference/models.md", "md"),
        ("docs/api-reference/resources.md", "md"),
        ("docs/api-reference/tools.md", "md"),
        ("docs/api-reference/utilities.md", "md"),
        ("docs/developer-guide/adding-tools.md", "md"),
        ("docs/developer-guide/architecture.md", "md"),
        ("docs/developer-guide/debugging.md", "md"),
        ("docs/developer-guide/testing.md", "md"),
        ("docs/examples/01_basic_energy.md", "md"),
        ("docs/examples/02_geometry_opt.md", "md"),
        ("docs/examples/03_frequencies.md", "md"),
        ("docs/examples/04_tddft.md", "md"),
        ("docs/examples/05_sapt.md", "md"),
        ("docs/examples/06_properties.md", "md"),
        ("docs/examples/07_coupled_cluster.md", "md"),
        ("docs/examples/08_solvation.md", "md"),
        ("docs/examples/09_advanced_workflows.md", "md"),
        ("docs/getting-started/configuration.md", "md"),
        ("docs/getting-started/installation.md", "md"),
        ("docs/getting-started/quick-start.md", "md"),
        ("docs/getting-started/troubleshooting.md", "md"),
        ("docs/theory/basis-sets.md", "md"),
        ("docs/theory/convergence.md", "md"),
        ("docs/theory/methods.md", "md"),
        ("docs/user-guide/advanced-topics.md", "md"),
        ("docs/user-guide/basic-calculations.md", "md"),
        ("docs/user-guide/excited-states.md", "md"),
        ("docs/user-guide/frequencies.md", "md"),
        ("docs/user-guide/intermolecular.md", "md"),
        ("docs/user-guide/optimization.md", "md"),
        ("docs/user-guide/properties.md", "md"),
    ]
    files_to_create.extend(docs_files)
    
    # Tests
    test_files = [
        ("tests/__init__.py", "py"),
        ("tests/conftest.py", "py"),
        ("tests/fixtures/__init__.py", "py"),
        ("tests/fixtures/mock_context.py", "py"),
        ("tests/fixtures/molecules.py", "py"),
        ("tests/fixtures/reference_data.py", "py"),
        ("tests/fixtures/test_files/.gitkeep", "txt"),
        ("tests/fixtures/test_files/sample_input_1.dat", "dat"),
        ("tests/fixtures/test_files/sample_input_2.dat", "dat"),
        ("tests/fixtures/test_files/sample_output_1.dat", "dat"),
        ("tests/fixtures/test_files/sample_output_2.dat", "dat"),
        ("tests/integration/__init__.py", "py"),
        ("tests/integration/test_error_recovery.py", "py"),
        ("tests/integration/test_mcp_protocol.py", "py"),
        ("tests/integration/test_psi4_interface.py", "py"),
        ("tests/integration/test_workflows.py", "py"),
        ("tests/performance/__init__.py", "py"),
        ("tests/performance/benchmark_suite.py", "py"),
        ("tests/performance/test_memory.py", "py"),
        ("tests/performance/test_speed.py", "py"),
        ("tests/regression/__init__.py", "py"),
        ("tests/regression/test_reference_values.py", "py"),
        ("tests/unit/__init__.py", "py"),
        ("tests/unit/test_converters.py", "py"),
        ("tests/unit/test_error_handlers.py", "py"),
        ("tests/unit/test_models.py", "py"),
        ("tests/unit/test_parsers.py", "py"),
        ("tests/unit/test_validation.py", "py"),
        ("tests/unit/tools/__init__.py", "py"),
        ("tests/unit/utils/__init__.py", "py"),
    ]
    files_to_create.extend(test_files)
    
    # Add tool test files
    tool_tests = [
        "adc", "anharmonic", "basis_extrapolation", "brueckner", "casscf", "cc2", "cc3", "ccsd",
        "ccsd_t", "ccsdt", "charges", "ci", "cisd", "cis", "composite", "constrained", "cpcm",
        "cube_files", "ddcosmo", "detci", "df_mp2", "dispersion", "ecd", "efp", "electric_moments",
        "energy", "eom_cc", "epr", "excited_opt", "fci", "fisapt", "fragment_analysis", "frequencies",
        "functional_scan", "g_tensor", "gradient", "grid_quality", "hessian", "hirshfeld", "hyperfine",
        "iefpcm", "ir_raman", "localization", "lowdin", "lr_ccsd", "mayer", "mcscf", "mcscf_gradients",
        "mp2", "mp2_5", "mp3", "mp4", "mulliken", "natural_orbitals", "nmr", "nmr_coupling",
        "nmr_shielding", "npa", "oniom", "optical_rotation", "optimization", "orbitals", "ord",
        "pcm", "polarizability", "population", "properties", "qmmm", "range_separated", "rasscf",
        "sapt", "sapt0", "sapt2", "sapt2_plus", "sapt_dft", "scan", "scs_mp2", "smd", "solvation",
        "spin_properties", "symmetry", "tda", "tddft", "thermochemistry", "transition_properties",
        "uv_vis", "vcd", "wavefunction", "wiberg", "zero_field"
    ]
    
    for test in tool_tests:
        files_to_create.append((f"tests/unit/tools/test_{test}.py", "py"))
    
    # Add util test files
    util_tests = [
        "basis_utils", "cache_manager", "constants", "convergence_helpers", "format_conversion",
        "geometry_utils", "math_utils", "memory_estimator", "molecular_descriptors", "parallel_utils",
        "symmetry_utils", "unit_conversion", "visualization"
    ]
    
    for test in util_tests:
        files_to_create.append((f"tests/unit/utils/test_{test}.py", "py"))
    
    print(f"Creating {len(files_to_create)} files...")
    for filepath, filetype in files_to_create:
        if create_file(filepath, filetype):
            file_count += 1
            if file_count % 50 == 0:
                print(f"  Created {file_count} files...")
    
    print(f"✓ All files created\n")
    
    # Final statistics
    total_dirs = len(list(Path(".").rglob("*"))) - len(list(Path(".").rglob("*.py"))) - len(list(Path(".").rglob("*.md"))) - len(list(Path(".").rglob("*.yaml"))) - len(list(Path(".").rglob("*.txt")))
    all_files = len(list(Path(".").rglob("*")))
    py_files = len(list(Path(".").rglob("*.py")))
    md_files = len(list(Path(".").rglob("*.md")))
    yaml_files = len(list(Path(".").rglob("*.y*ml")))
    
    print("=" * 50)
    print("📊 Final Statistics")
    print("=" * 50)
    print(f"Files created by script: {file_count}")
    print(f"Total Python files: {py_files}")
    print(f"Total Markdown files: {md_files}")
    print(f"Total YAML files: {yaml_files}")
    print(f"Total all files and dirs: {all_files}")
    print()
    print("✅ Complete project structure created!")
    print("🚀 Ready for implementation!")

if __name__ == "__main__":
    main()
