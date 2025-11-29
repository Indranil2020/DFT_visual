#!/bin/bash
# Psi4 MCP Server - Create All Files and Folders
# Creates the complete 380+ file structure from psi4_mcp_complete_tree.txt
# Version: 2.0 - FIXED VERSION
# Date: 2025-11-29
# Fixed: Now creates ALL directories first, then all files

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="${1:-.}"

echo "=========================================="
echo "Creating All Placeholder Files (FIXED)"
echo "=========================================="
echo ""

# If the current directory is already psi4-mcp-server, use current dir
if [ -d "psi4-mcp-server" ]; then
    PROJECT_ROOT="psi4-mcp-server"
    cd "$PROJECT_ROOT"
elif [ "$(basename "$(pwd)")" = "psi4-mcp-server" ]; then
    # Already in psi4-mcp-server directory
    :
else
    echo -e "${RED}Error: Must run from test directory containing psi4-mcp-server or from within psi4-mcp-server${NC}"
    exit 1
fi
echo -e "${BLUE}Working in: $(pwd)${NC}"
echo ""

# Counter
DIR_COUNT=0
FILE_COUNT=0

# Function to create directory safely
create_dir() {
    local dirpath=$1
    if [ ! -d "$dirpath" ]; then
        mkdir -p "$dirpath"
        ((DIR_COUNT++))
    fi
}

# Function to create file with header comment
create_file() {
    local filepath=$1
    local filetype=$2

    # Ensure directory exists
    local dirpath=$(dirname "$filepath")
    create_dir "$dirpath"

    if [ ! -f "$filepath" ]; then
        case "$filetype" in
            py)
                cat > "$filepath" << 'PYEOF'
"""
Psi4 MCP Server - Placeholder Module

This file is part of the Psi4 MCP Server implementation.
TODO: Implement according to psi4_mcp_comprehensive_plan.md
"""

# TODO: Add implementation
pass
PYEOF
                ;;
            md)
                cat > "$filepath" << 'MDEOF'
# Placeholder Documentation

TODO: Add documentation content

## Overview

This document is part of the Psi4 MCP Server documentation.

## Content

To be added during implementation.
MDEOF
                ;;
            yaml|yml)
                cat > "$filepath" << 'YAMLEOF'
# Psi4 MCP Server Configuration
# TODO: Add configuration settings
YAMLEOF
                ;;
            toml)
                cat > "$filepath" << 'TOMLEOF'
# Psi4 MCP Server Configuration
# TODO: Add TOML configuration
TOMLEOF
                ;;
            txt)
                echo "# Placeholder file - TODO: Add content" > "$filepath"
                ;;
            sh)
                cat > "$filepath" << 'SHEOF'
#!/bin/bash
# Psi4 MCP Server Script
# TODO: Implement script functionality

echo "TODO: Implement this script"
SHEOF
                chmod +x "$filepath"
                ;;
            cif|pdb|xyz|gbs|json|bib|conf|service|dat|ipynb)
                # Data files - create as empty or minimal
                case "$filetype" in
                    json)
                        echo '{}' > "$filepath"
                        ;;
                    ipynb)
                        echo '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}' > "$filepath"
                        ;;
                    *)
                        touch "$filepath"
                        ;;
                esac
                ;;
            *)
                touch "$filepath"
                ;;
        esac
        ((FILE_COUNT++))
    fi
}

# ============================================
# CREATE ALL DIRECTORIES FIRST
# ============================================

echo -e "${BLUE}Creating directory structure...${NC}"

# GitHub directories
create_dir ".github/ISSUE_TEMPLATE"
create_dir ".github/workflows"

# Benchmarks directories
create_dir "benchmarks/accuracy"
create_dir "benchmarks/performance"
create_dir "benchmarks/results"

# Config directory
create_dir "config"

# Data directories
create_dir "data/basis_sets/dunning"
create_dir "data/basis_sets/karlsruhe"
create_dir "data/basis_sets/pople"
create_dir "data/basis_sets/sto"
create_dir "data/literature"
create_dir "data/molecules/benchmarks"
create_dir "data/molecules/common"
create_dir "data/molecules/test_set"
create_dir "data/parameters"
create_dir "data/reference_data"

# Deployment directories
create_dir "deployment/helm/psi4-mcp/templates"
create_dir "deployment/kubernetes"
create_dir "deployment/supervisor"
create_dir "deployment/systemd"

# Docs directories
create_dir "docs/assets/screenshots"
create_dir "docs/api-reference"
create_dir "docs/developer-guide"
create_dir "docs/examples"
create_dir "docs/getting-started"
create_dir "docs/theory"
create_dir "docs/user-guide"

# Examples directories
create_dir "examples/molecules/cif"
create_dir "examples/molecules/pdb"
create_dir "examples/molecules/xyz"
create_dir "examples/notebooks"
create_dir "examples/python/advanced"
create_dir "examples/python/basic"
create_dir "examples/python/intermediate"
create_dir "examples/python/workflows"

# Notebooks directories
create_dir "notebooks/development"
create_dir "notebooks/exploration"
create_dir "notebooks/presentations"

# Scripts directory
create_dir "scripts"

# Source code directories
create_dir "src/psi4_mcp/cli/commands"
create_dir "src/psi4_mcp/database/migrations"
create_dir "src/psi4_mcp/integrations"
create_dir "src/psi4_mcp/models/calculations"
create_dir "src/psi4_mcp/models/enums"
create_dir "src/psi4_mcp/models/outputs"
create_dir "src/psi4_mcp/prompts"
create_dir "src/psi4_mcp/resources"
create_dir "src/psi4_mcp/scripts"

# Tools directories
create_dir "src/psi4_mcp/tools/advanced"
create_dir "src/psi4_mcp/tools/analysis"
create_dir "src/psi4_mcp/tools/basis_sets"
create_dir "src/psi4_mcp/tools/composite"
create_dir "src/psi4_mcp/tools/configuration_interaction"
create_dir "src/psi4_mcp/tools/core"
create_dir "src/psi4_mcp/tools/coupled_cluster"
create_dir "src/psi4_mcp/tools/dft"
create_dir "src/psi4_mcp/tools/excited_states"
create_dir "src/psi4_mcp/tools/mcscf"
create_dir "src/psi4_mcp/tools/perturbation_theory"
create_dir "src/psi4_mcp/tools/properties/bonds"
create_dir "src/psi4_mcp/tools/properties/charges"
create_dir "src/psi4_mcp/tools/sapt"
create_dir "src/psi4_mcp/tools/solvation"
create_dir "src/psi4_mcp/tools/spectroscopy/epr"
create_dir "src/psi4_mcp/tools/spectroscopy/nmr"
create_dir "src/psi4_mcp/tools/utilities"
create_dir "src/psi4_mcp/tools/vibrational"

# Utilities directories
create_dir "src/psi4_mcp/utils/basis"
create_dir "src/psi4_mcp/utils/caching"
create_dir "src/psi4_mcp/utils/convergence"
create_dir "src/psi4_mcp/utils/conversion"
create_dir "src/psi4_mcp/utils/error_handling"
create_dir "src/psi4_mcp/utils/geometry"
create_dir "src/psi4_mcp/utils/helpers"
create_dir "src/psi4_mcp/utils/logging"
create_dir "src/psi4_mcp/utils/memory"
create_dir "src/psi4_mcp/utils/molecular"
create_dir "src/psi4_mcp/utils/parallel"
create_dir "src/psi4_mcp/utils/parsing"
create_dir "src/psi4_mcp/utils/validation"
create_dir "src/psi4_mcp/utils/visualization"

# Test directories
create_dir "tests/fixtures/test_files"
create_dir "tests/integration"
create_dir "tests/performance"
create_dir "tests/regression"
create_dir "tests/unit/tools"
create_dir "tests/unit/utils"

echo -e "${GREEN}✓ Created $DIR_COUNT directories${NC}"
echo ""

# ============================================
# CREATE ALL FILES
# ============================================

echo -e "${BLUE}Creating placeholder files...${NC}"
echo ""

echo -e "${BLUE}Top-level files...${NC}"

# Top-level configuration files
create_file "pyproject.toml" "toml"
create_file "setup.py" "py"
create_file "requirements.txt" "txt"
create_file "requirements-dev.txt" "txt"
create_file "requirements-optional.txt" "txt"
create_file "CHANGELOG.md" "md"
create_file "CODE_OF_CONDUCT.md" "md"
create_file "CONTRIBUTING.md" "md"
create_file "LICENSE" "txt"
create_file "README.md" "md"
create_file "Dockerfile" "txt"
create_file "docker-compose.yml" "yaml"
create_file ".gitattributes" "txt"
create_file ".gitignore" "txt"
create_file ".env.example" "txt"

echo -e "${BLUE}GitHub templates...${NC}"

# GitHub templates and workflows
create_file ".github/PULL_REQUEST_TEMPLATE.md" "md"
create_file ".github/ISSUE_TEMPLATE/bug_report.md" "md"
create_file ".github/ISSUE_TEMPLATE/feature_request.md" "md"
create_file ".github/ISSUE_TEMPLATE/question.md" "md"
create_file ".github/workflows/build.yml" "yaml"
create_file ".github/workflows/docs.yml" "yaml"
create_file ".github/workflows/lint.yml" "yaml"
create_file ".github/workflows/publish.yml" "yaml"
create_file ".github/workflows/test.yml" "yaml"

echo -e "${BLUE}Config files...${NC}"

# Config files
create_file "config/default.yaml" "yaml"
create_file "config/development.yaml" "yaml"
create_file "config/production.yaml" "yaml"
create_file "config/testing.yaml" "yaml"
create_file "config/logging.yaml" "yaml"

echo -e "${BLUE}Scripts...${NC}"

# Scripts
create_file "scripts/build_docker.sh" "sh"
create_file "scripts/cleanup.sh" "sh"
create_file "scripts/deploy.sh" "sh"
create_file "scripts/generate_docs.sh" "sh"
create_file "scripts/install.sh" "sh"
create_file "scripts/run_tests.sh" "sh"
create_file "scripts/setup_conda.sh" "sh"

echo -e "${BLUE}Core source files...${NC}"

# Core source files
create_file "src/psi4_mcp/__init__.py" "py"
create_file "src/psi4_mcp/__version__.py" "py"
create_file "src/psi4_mcp/config.py" "py"
create_file "src/psi4_mcp/server.py" "py"

# CLI files
create_file "src/psi4_mcp/cli/__init__.py" "py"
create_file "src/psi4_mcp/cli/main.py" "py"
create_file "src/psi4_mcp/cli/utils.py" "py"
create_file "src/psi4_mcp/cli/commands/__init__.py" "py"
create_file "src/psi4_mcp/cli/commands/convert.py" "py"
create_file "src/psi4_mcp/cli/commands/start.py" "py"
create_file "src/psi4_mcp/cli/commands/test.py" "py"
create_file "src/psi4_mcp/cli/commands/validate.py" "py"

# Database files
create_file "src/psi4_mcp/database/__init__.py" "py"
create_file "src/psi4_mcp/database/manager.py" "py"
create_file "src/psi4_mcp/database/queries.py" "py"
create_file "src/psi4_mcp/database/schema.py" "py"
create_file "src/psi4_mcp/database/migrations/__init__.py" "py"
create_file "src/psi4_mcp/database/migrations/v001_initial.py" "py"

# Integration files
create_file "src/psi4_mcp/integrations/__init__.py" "py"
create_file "src/psi4_mcp/integrations/ase.py" "py"
create_file "src/psi4_mcp/integrations/cclib.py" "py"
create_file "src/psi4_mcp/integrations/molssi.py" "py"
create_file "src/psi4_mcp/integrations/openbabel.py" "py"
create_file "src/psi4_mcp/integrations/qcschema.py" "py"
create_file "src/psi4_mcp/integrations/rdkit.py" "py"

# Model files
create_file "src/psi4_mcp/models/__init__.py" "py"
create_file "src/psi4_mcp/models/base.py" "py"
create_file "src/psi4_mcp/models/errors.py" "py"
create_file "src/psi4_mcp/models/molecules.py" "py"
create_file "src/psi4_mcp/models/options.py" "py"
create_file "src/psi4_mcp/models/resources.py" "py"

# Model calculations
create_file "src/psi4_mcp/models/calculations/__init__.py" "py"
create_file "src/psi4_mcp/models/calculations/configuration_interaction.py" "py"
create_file "src/psi4_mcp/models/calculations/coupled_cluster.py" "py"
create_file "src/psi4_mcp/models/calculations/energy.py" "py"
create_file "src/psi4_mcp/models/calculations/frequencies.py" "py"
create_file "src/psi4_mcp/models/calculations/mcscf.py" "py"
create_file "src/psi4_mcp/models/calculations/optimization.py" "py"
create_file "src/psi4_mcp/models/calculations/properties.py" "py"
create_file "src/psi4_mcp/models/calculations/response.py" "py"
create_file "src/psi4_mcp/models/calculations/sapt.py" "py"
create_file "src/psi4_mcp/models/calculations/solvation.py" "py"
create_file "src/psi4_mcp/models/calculations/tddft.py" "py"

# Model enums
create_file "src/psi4_mcp/models/enums/__init__.py" "py"
create_file "src/psi4_mcp/models/enums/basis_sets.py" "py"
create_file "src/psi4_mcp/models/enums/methods.py" "py"
create_file "src/psi4_mcp/models/enums/properties.py" "py"
create_file "src/psi4_mcp/models/enums/references.py" "py"

# Model outputs
create_file "src/psi4_mcp/models/outputs/__init__.py" "py"
create_file "src/psi4_mcp/models/outputs/analysis.py" "py"
create_file "src/psi4_mcp/models/outputs/coupled_cluster.py" "py"
create_file "src/psi4_mcp/models/outputs/energy.py" "py"
create_file "src/psi4_mcp/models/outputs/frequencies.py" "py"
create_file "src/psi4_mcp/models/outputs/optimization.py" "py"
create_file "src/psi4_mcp/models/outputs/orbitals.py" "py"
create_file "src/psi4_mcp/models/outputs/properties.py" "py"
create_file "src/psi4_mcp/models/outputs/sapt.py" "py"
create_file "src/psi4_mcp/models/outputs/spectrum.py" "py"
create_file "src/psi4_mcp/models/outputs/tddft.py" "py"

# Prompt files
create_file "src/psi4_mcp/prompts/__init__.py" "py"
create_file "src/psi4_mcp/prompts/education.py" "py"
create_file "src/psi4_mcp/prompts/methods.py" "py"
create_file "src/psi4_mcp/prompts/troubleshooting.py" "py"
create_file "src/psi4_mcp/prompts/workflows.py" "py"

# Resource files
create_file "src/psi4_mcp/resources/__init__.py" "py"
create_file "src/psi4_mcp/resources/basis_sets.py" "py"
create_file "src/psi4_mcp/resources/benchmarks.py" "py"
create_file "src/psi4_mcp/resources/functionals.py" "py"
create_file "src/psi4_mcp/resources/literature.py" "py"
create_file "src/psi4_mcp/resources/methods.py" "py"
create_file "src/psi4_mcp/resources/molecules.py" "py"
create_file "src/psi4_mcp/resources/tutorials.py" "py"

# Scripts files
create_file "src/psi4_mcp/scripts/__init__.py" "py"
create_file "src/psi4_mcp/scripts/benchmark.py" "py"
create_file "src/psi4_mcp/scripts/generate_docs.py" "py"
create_file "src/psi4_mcp/scripts/install_deps.py" "py"
create_file "src/psi4_mcp/scripts/setup_env.py" "py"

echo -e "${BLUE}Tools - Core...${NC}"

# Tools - Core
create_file "src/psi4_mcp/tools/__init__.py" "py"
create_file "src/psi4_mcp/tools/core/__init__.py" "py"
create_file "src/psi4_mcp/tools/core/energy.py" "py"
create_file "src/psi4_mcp/tools/core/gradient.py" "py"
create_file "src/psi4_mcp/tools/core/hessian.py" "py"
create_file "src/psi4_mcp/tools/core/optimization.py" "py"

echo -e "${BLUE}Tools - Vibrational...${NC}"

# Tools - Vibrational
create_file "src/psi4_mcp/tools/vibrational/__init__.py" "py"
create_file "src/psi4_mcp/tools/vibrational/anharmonic.py" "py"
create_file "src/psi4_mcp/tools/vibrational/frequencies.py" "py"
create_file "src/psi4_mcp/tools/vibrational/thermochemistry.py" "py"
create_file "src/psi4_mcp/tools/vibrational/vcd.py" "py"

echo -e "${BLUE}Tools - Properties...${NC}"

# Tools - Properties
create_file "src/psi4_mcp/tools/properties/__init__.py" "py"
create_file "src/psi4_mcp/tools/properties/bonds.py" "py"
create_file "src/psi4_mcp/tools/properties/electric_moments.py" "py"
create_file "src/psi4_mcp/tools/properties/electrostatic.py" "py"
create_file "src/psi4_mcp/tools/properties/optical_rotation.py" "py"
create_file "src/psi4_mcp/tools/properties/orbitals.py" "py"
create_file "src/psi4_mcp/tools/properties/polarizability.py" "py"
create_file "src/psi4_mcp/tools/properties/spin_properties.py" "py"
create_file "src/psi4_mcp/tools/properties/bonds/__init__.py" "py"
create_file "src/psi4_mcp/tools/properties/bonds/mayer.py" "py"
create_file "src/psi4_mcp/tools/properties/bonds/wiberg.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/__init__.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/esp.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/hirshfeld.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/lowdin.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/mulliken.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/npa.py" "py"

echo -e "${BLUE}Tools - Spectroscopy...${NC}"

# Tools - Spectroscopy
create_file "src/psi4_mcp/tools/spectroscopy/__init__.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/ecd.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/ir_raman.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/ord.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/uv_vis.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/__init__.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/g_tensor.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/hyperfine.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/zero_field.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/__init__.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/coupling.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/shielding.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/spectra.py" "py"

echo -e "${BLUE}Tools - Excited States...${NC}"

# Tools - Excited States
create_file "src/psi4_mcp/tools/excited_states/__init__.py" "py"
create_file "src/psi4_mcp/tools/excited_states/adc.py" "py"
create_file "src/psi4_mcp/tools/excited_states/cis.py" "py"
create_file "src/psi4_mcp/tools/excited_states/eom_cc.py" "py"
create_file "src/psi4_mcp/tools/excited_states/excited_opt.py" "py"
create_file "src/psi4_mcp/tools/excited_states/tda.py" "py"
create_file "src/psi4_mcp/tools/excited_states/tddft.py" "py"
create_file "src/psi4_mcp/tools/excited_states/transition_properties.py" "py"

echo -e "${BLUE}Tools - Coupled Cluster...${NC}"

# Tools - Coupled Cluster
create_file "src/psi4_mcp/tools/coupled_cluster/__init__.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/brueckner.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/cc2.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/cc3.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsd.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsd_t.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsdt.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/eom_ccsd.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/lr_ccsd.py" "py"

echo -e "${BLUE}Tools - Perturbation Theory...${NC}"

# Tools - Perturbation Theory
create_file "src/psi4_mcp/tools/perturbation_theory/__init__.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/df_mp2.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp2.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp2_5.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp3.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp4.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/scs_mp2.py" "py"

echo -e "${BLUE}Tools - Configuration Interaction...${NC}"

# Tools - Configuration Interaction
create_file "src/psi4_mcp/tools/configuration_interaction/__init__.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/cisd.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/cisdt.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/detci.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/fci.py" "py"

echo -e "${BLUE}Tools - MCSCF...${NC}"

# Tools - MCSCF
create_file "src/psi4_mcp/tools/mcscf/__init__.py" "py"
create_file "src/psi4_mcp/tools/mcscf/casscf.py" "py"
create_file "src/psi4_mcp/tools/mcscf/mcscf_gradients.py" "py"
create_file "src/psi4_mcp/tools/mcscf/rasscf.py" "py"

echo -e "${BLUE}Tools - SAPT...${NC}"

# Tools - SAPT
create_file "src/psi4_mcp/tools/sapt/__init__.py" "py"
create_file "src/psi4_mcp/tools/sapt/analysis.py" "py"
create_file "src/psi4_mcp/tools/sapt/fisapt.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt0.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2_plus.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2_plus_3.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt_dft.py" "py"

echo -e "${BLUE}Tools - Solvation...${NC}"

# Tools - Solvation
create_file "src/psi4_mcp/tools/solvation/__init__.py" "py"
create_file "src/psi4_mcp/tools/solvation/cpcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/ddcosmo.py" "py"
create_file "src/psi4_mcp/tools/solvation/iefpcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/pcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/smd.py" "py"

echo -e "${BLUE}Tools - DFT...${NC}"

# Tools - DFT
create_file "src/psi4_mcp/tools/dft/__init__.py" "py"
create_file "src/psi4_mcp/tools/dft/dispersion.py" "py"
create_file "src/psi4_mcp/tools/dft/functional_scan.py" "py"
create_file "src/psi4_mcp/tools/dft/grid_quality.py" "py"
create_file "src/psi4_mcp/tools/dft/range_separated.py" "py"

echo -e "${BLUE}Tools - Basis Sets...${NC}"

# Tools - Basis Sets
create_file "src/psi4_mcp/tools/basis_sets/__init__.py" "py"
create_file "src/psi4_mcp/tools/basis_sets/basis_info.py" "py"
create_file "src/psi4_mcp/tools/basis_sets/composite.py" "py"
create_file "src/psi4_mcp/tools/basis_sets/extrapolation.py" "py"

echo -e "${BLUE}Tools - Analysis...${NC}"

# Tools - Analysis
create_file "src/psi4_mcp/tools/analysis/__init__.py" "py"
create_file "src/psi4_mcp/tools/analysis/cube_files.py" "py"
create_file "src/psi4_mcp/tools/analysis/fragment_analysis.py" "py"
create_file "src/psi4_mcp/tools/analysis/localization.py" "py"
create_file "src/psi4_mcp/tools/analysis/natural_orbitals.py" "py"
create_file "src/psi4_mcp/tools/analysis/population.py" "py"
create_file "src/psi4_mcp/tools/analysis/wavefunction.py" "py"

echo -e "${BLUE}Tools - Composite...${NC}"

# Tools - Composite
create_file "src/psi4_mcp/tools/composite/__init__.py" "py"
create_file "src/psi4_mcp/tools/composite/cbs_qb3.py" "py"
create_file "src/psi4_mcp/tools/composite/g1.py" "py"
create_file "src/psi4_mcp/tools/composite/g2.py" "py"
create_file "src/psi4_mcp/tools/composite/g3.py" "py"
create_file "src/psi4_mcp/tools/composite/g4.py" "py"
create_file "src/psi4_mcp/tools/composite/w1.py" "py"

echo -e "${BLUE}Tools - Advanced...${NC}"

# Tools - Advanced
create_file "src/psi4_mcp/tools/advanced/__init__.py" "py"
create_file "src/psi4_mcp/tools/advanced/constrained.py" "py"
create_file "src/psi4_mcp/tools/advanced/efp.py" "py"
create_file "src/psi4_mcp/tools/advanced/oniom.py" "py"
create_file "src/psi4_mcp/tools/advanced/qmmm.py" "py"
create_file "src/psi4_mcp/tools/advanced/scan.py" "py"
create_file "src/psi4_mcp/tools/advanced/symmetry.py" "py"

echo -e "${BLUE}Tools - Utilities...${NC}"

# Tools - Utilities
create_file "src/psi4_mcp/tools/utilities/__init__.py" "py"
create_file "src/psi4_mcp/tools/utilities/batch_runner.py" "py"
create_file "src/psi4_mcp/tools/utilities/format_converter.py" "py"
create_file "src/psi4_mcp/tools/utilities/structure_builder.py" "py"
create_file "src/psi4_mcp/tools/utilities/workflow_manager.py" "py"

echo -e "${BLUE}Utils - Basis...${NC}"

# Utils - Basis
create_file "src/psi4_mcp/utils/__init__.py" "py"
create_file "src/psi4_mcp/utils/basis/__init__.py" "py"
create_file "src/psi4_mcp/utils/basis/generator.py" "py"
create_file "src/psi4_mcp/utils/basis/library.py" "py"
create_file "src/psi4_mcp/utils/basis/optimizer.py" "py"
create_file "src/psi4_mcp/utils/basis/parser.py" "py"

echo -e "${BLUE}Utils - Caching...${NC}"

# Utils - Caching
create_file "src/psi4_mcp/utils/caching/__init__.py" "py"
create_file "src/psi4_mcp/utils/caching/cache_manager.py" "py"
create_file "src/psi4_mcp/utils/caching/molecular.py" "py"
create_file "src/psi4_mcp/utils/caching/results.py" "py"

echo -e "${BLUE}Utils - Convergence...${NC}"

# Utils - Convergence
create_file "src/psi4_mcp/utils/convergence/__init__.py" "py"
create_file "src/psi4_mcp/utils/convergence/optimization.py" "py"
create_file "src/psi4_mcp/utils/convergence/scf.py" "py"
create_file "src/psi4_mcp/utils/convergence/strategies.py" "py"
create_file "src/psi4_mcp/utils/convergence/tddft.py" "py"

echo -e "${BLUE}Utils - Conversion...${NC}"

# Utils - Conversion
create_file "src/psi4_mcp/utils/conversion/__init__.py" "py"
create_file "src/psi4_mcp/utils/conversion/basis_sets.py" "py"
create_file "src/psi4_mcp/utils/conversion/geometry.py" "py"
create_file "src/psi4_mcp/utils/conversion/output.py" "py"
create_file "src/psi4_mcp/utils/conversion/units.py" "py"

echo -e "${BLUE}Utils - Error Handling...${NC}"

# Utils - Error Handling
create_file "src/psi4_mcp/utils/error_handling/__init__.py" "py"
create_file "src/psi4_mcp/utils/error_handling/categorization.py" "py"
create_file "src/psi4_mcp/utils/error_handling/detection.py" "py"
create_file "src/psi4_mcp/utils/error_handling/logging.py" "py"
create_file "src/psi4_mcp/utils/error_handling/recovery.py" "py"
create_file "src/psi4_mcp/utils/error_handling/suggestions.py" "py"

echo -e "${BLUE}Utils - Geometry...${NC}"

# Utils - Geometry
create_file "src/psi4_mcp/utils/geometry/__init__.py" "py"
create_file "src/psi4_mcp/utils/geometry/alignment.py" "py"
create_file "src/psi4_mcp/utils/geometry/analysis.py" "py"
create_file "src/psi4_mcp/utils/geometry/builders.py" "py"
create_file "src/psi4_mcp/utils/geometry/symmetry.py" "py"
create_file "src/psi4_mcp/utils/geometry/transformations.py" "py"

echo -e "${BLUE}Utils - Helpers...${NC}"

# Utils - Helpers
create_file "src/psi4_mcp/utils/helpers/__init__.py" "py"
create_file "src/psi4_mcp/utils/helpers/constants.py" "py"
create_file "src/psi4_mcp/utils/helpers/math_utils.py" "py"
create_file "src/psi4_mcp/utils/helpers/string_utils.py" "py"
create_file "src/psi4_mcp/utils/helpers/units.py" "py"

echo -e "${BLUE}Utils - Logging...${NC}"

# Utils - Logging
create_file "src/psi4_mcp/utils/logging/__init__.py" "py"
create_file "src/psi4_mcp/utils/logging/formatters.py" "py"
create_file "src/psi4_mcp/utils/logging/handlers.py" "py"
create_file "src/psi4_mcp/utils/logging/logger.py" "py"

echo -e "${BLUE}Utils - Memory...${NC}"

# Utils - Memory
create_file "src/psi4_mcp/utils/memory/__init__.py" "py"
create_file "src/psi4_mcp/utils/memory/estimator.py" "py"
create_file "src/psi4_mcp/utils/memory/manager.py" "py"
create_file "src/psi4_mcp/utils/memory/optimizer.py" "py"

echo -e "${BLUE}Utils - Molecular...${NC}"

# Utils - Molecular
create_file "src/psi4_mcp/utils/molecular/__init__.py" "py"
create_file "src/psi4_mcp/utils/molecular/database.py" "py"
create_file "src/psi4_mcp/utils/molecular/descriptors.py" "py"
create_file "src/psi4_mcp/utils/molecular/fingerprints.py" "py"
create_file "src/psi4_mcp/utils/molecular/similarity.py" "py"

echo -e "${BLUE}Utils - Parallel...${NC}"

# Utils - Parallel
create_file "src/psi4_mcp/utils/parallel/__init__.py" "py"
create_file "src/psi4_mcp/utils/parallel/mpi_interface.py" "py"
create_file "src/psi4_mcp/utils/parallel/task_queue.py" "py"
create_file "src/psi4_mcp/utils/parallel/thread_manager.py" "py"

echo -e "${BLUE}Utils - Parsing...${NC}"

# Utils - Parsing
create_file "src/psi4_mcp/utils/parsing/__init__.py" "py"
create_file "src/psi4_mcp/utils/parsing/energy.py" "py"
create_file "src/psi4_mcp/utils/parsing/frequencies.py" "py"
create_file "src/psi4_mcp/utils/parsing/generic.py" "py"
create_file "src/psi4_mcp/utils/parsing/optimization.py" "py"
create_file "src/psi4_mcp/utils/parsing/orbitals.py" "py"
create_file "src/psi4_mcp/utils/parsing/properties.py" "py"
create_file "src/psi4_mcp/utils/parsing/wavefunction.py" "py"

echo -e "${BLUE}Utils - Validation...${NC}"

# Utils - Validation
create_file "src/psi4_mcp/utils/validation/__init__.py" "py"
create_file "src/psi4_mcp/utils/validation/basis_sets.py" "py"
create_file "src/psi4_mcp/utils/validation/constraints.py" "py"
create_file "src/psi4_mcp/utils/validation/geometry.py" "py"
create_file "src/psi4_mcp/utils/validation/methods.py" "py"
create_file "src/psi4_mcp/utils/validation/options.py" "py"

echo -e "${BLUE}Utils - Visualization...${NC}"

# Utils - Visualization
create_file "src/psi4_mcp/utils/visualization/__init__.py" "py"
create_file "src/psi4_mcp/utils/visualization/molecular.py" "py"
create_file "src/psi4_mcp/utils/visualization/orbitals.py" "py"
create_file "src/psi4_mcp/utils/visualization/spectra.py" "py"
create_file "src/psi4_mcp/utils/visualization/surfaces.py" "py"

echo -e "${BLUE}Data files...${NC}"

# Data files - basis sets
create_file "data/basis_sets/dunning/cc-pVDZ.gbs" "gbs"
create_file "data/basis_sets/dunning/cc-pVQZ.gbs" "gbs"
create_file "data/basis_sets/dunning/cc-pVTZ.gbs" "gbs"
create_file "data/basis_sets/dunning/cc-pV5Z.gbs" "gbs"
create_file "data/basis_sets/karlsruhe/def2-SVP.gbs" "gbs"
create_file "data/basis_sets/karlsruhe/def2-TZVP.gbs" "gbs"
create_file "data/basis_sets/karlsruhe/def2-QZVP.gbs" "gbs"
create_file "data/basis_sets/pople/3-21G.gbs" "gbs"
create_file "data/basis_sets/pople/6-31G.gbs" "gbs"
create_file "data/basis_sets/pople/6-311G.gbs" "gbs"
create_file "data/basis_sets/pople/6-311++G.gbs" "gbs"
create_file "data/basis_sets/sto/STO-3G.gbs" "gbs"

# Data files - literature
create_file "data/literature/benchmarks.json" "json"
create_file "data/literature/citations.bib" "bib"

# Data files - molecules
create_file "data/molecules/benchmarks/g2_set.xyz" "xyz"
create_file "data/molecules/benchmarks/s22_set.xyz" "xyz"
create_file "data/molecules/benchmarks/s66_set.xyz" "xyz"
create_file "data/molecules/common/benzene.xyz" "xyz"
create_file "data/molecules/common/ethane.xyz" "xyz"
create_file "data/molecules/common/methane.xyz" "xyz"
create_file "data/molecules/common/water.xyz" "xyz"
create_file "data/molecules/common/ammonia.xyz" "xyz"
create_file "data/molecules/test_set/test_molecule_1.xyz" "xyz"
create_file "data/molecules/test_set/test_molecule_2.xyz" "xyz"
create_file "data/molecules/test_set/test_molecule_3.xyz" "xyz"

# Data files - parameters
create_file "data/parameters/dispersion_parameters.json" "json"
create_file "data/parameters/functional_parameters.json" "json"
create_file "data/parameters/solvation_parameters.json" "json"

# Data files - reference data
create_file "data/reference_data/energies.json" "json"
create_file "data/reference_data/frequencies.json" "json"
create_file "data/reference_data/geometries.json" "json"
create_file "data/reference_data/properties.json" "json"

echo -e "${BLUE}Benchmarks...${NC}"

# Benchmarks
create_file "benchmarks/__init__.py" "py"
create_file "benchmarks/accuracy/__init__.py" "py"
create_file "benchmarks/accuracy/energies.py" "py"
create_file "benchmarks/accuracy/geometries.py" "py"
create_file "benchmarks/accuracy/properties.py" "py"
create_file "benchmarks/performance/__init__.py" "py"
create_file "benchmarks/performance/execution_time.py" "py"
create_file "benchmarks/performance/memory_usage.py" "py"
create_file "benchmarks/performance/parallel_scaling.py" "py"
create_file "benchmarks/results/.gitkeep" "txt"
create_file "benchmarks/results/accuracy_results.json" "json"
create_file "benchmarks/results/performance_results.json" "json"

echo -e "${BLUE}Examples...${NC}"

# Examples
create_file "examples/molecules/cif/nacl.cif" "cif"
create_file "examples/molecules/cif/quartz.cif" "cif"
create_file "examples/molecules/pdb/1abc.pdb" "pdb"
create_file "examples/molecules/pdb/protein.pdb" "pdb"
create_file "examples/molecules/xyz/benzene.xyz" "xyz"
create_file "examples/molecules/xyz/ethane.xyz" "xyz"
create_file "examples/molecules/xyz/water.xyz" "xyz"

# Examples - notebooks
create_file "examples/notebooks/tutorial_1_basics.ipynb" "ipynb"
create_file "examples/notebooks/tutorial_2_properties.ipynb" "ipynb"
create_file "examples/notebooks/tutorial_3_advanced.ipynb" "ipynb"

# Examples - python basic
create_file "examples/python/basic/01_water_energy.py" "py"
create_file "examples/python/basic/02_methane_opt.py" "py"
create_file "examples/python/basic/03_co2_frequencies.py" "py"
create_file "examples/python/basic/04_benzene_properties.py" "py"

# Examples - python intermediate
create_file "examples/python/intermediate/05_uv_vis_spectrum.py" "py"
create_file "examples/python/intermediate/06_hydrogen_bond_sapt.py" "py"
create_file "examples/python/intermediate/07_reaction_energy.py" "py"
create_file "examples/python/intermediate/08_conformation_scan.py" "py"

# Examples - python advanced
create_file "examples/python/advanced/09_excited_state_opt.py" "py"
create_file "examples/python/advanced/10_nmr_shielding.py" "py"
create_file "examples/python/advanced/11_pcm_solvation.py" "py"
create_file "examples/python/advanced/12_multi_reference.py" "py"

# Examples - python workflows
create_file "examples/python/workflows/complete_characterization.py" "py"
create_file "examples/python/workflows/high_throughput.py" "py"
create_file "examples/python/workflows/reaction_pathway.py" "py"

echo -e "${BLUE}Notebooks...${NC}"

# Notebooks
create_file "notebooks/development/error_analysis.ipynb" "ipynb"
create_file "notebooks/development/performance_profiling.ipynb" "ipynb"
create_file "notebooks/development/validation_testing.ipynb" "ipynb"
create_file "notebooks/exploration/basis_set_comparison.ipynb" "ipynb"
create_file "notebooks/exploration/functional_benchmarking.ipynb" "ipynb"
create_file "notebooks/exploration/method_accuracy.ipynb" "ipynb"
create_file "notebooks/presentations/demo.ipynb" "ipynb"
create_file "notebooks/presentations/tutorial.ipynb" "ipynb"

echo -e "${BLUE}Deployment...${NC}"

# Deployment
create_file "deployment/helm/psi4-mcp/Chart.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/values.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/deployment.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/service.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/configmap.yaml" "yaml"
create_file "deployment/kubernetes/configmap.yaml" "yaml"
create_file "deployment/kubernetes/deployment.yaml" "yaml"
create_file "deployment/kubernetes/service.yaml" "yaml"
create_file "deployment/supervisor/psi4-mcp.conf" "conf"
create_file "deployment/systemd/psi4-mcp.service" "service"

echo -e "${BLUE}Documentation...${NC}"

# Docs
create_file "docs/index.md" "md"
create_file "docs/assets/.gitkeep" "txt"
create_file "docs/assets/architecture_diagram.png" "txt"
create_file "docs/assets/logo.png" "txt"
create_file "docs/assets/screenshots/.gitkeep" "txt"

# Docs - API reference
create_file "docs/api-reference/models.md" "md"
create_file "docs/api-reference/resources.md" "md"
create_file "docs/api-reference/tools.md" "md"
create_file "docs/api-reference/utilities.md" "md"

# Docs - Developer guide
create_file "docs/developer-guide/adding-tools.md" "md"
create_file "docs/developer-guide/architecture.md" "md"
create_file "docs/developer-guide/debugging.md" "md"
create_file "docs/developer-guide/testing.md" "md"

# Docs - Examples
create_file "docs/examples/01_basic_energy.md" "md"
create_file "docs/examples/02_geometry_opt.md" "md"
create_file "docs/examples/03_frequencies.md" "md"
create_file "docs/examples/04_tddft.md" "md"
create_file "docs/examples/05_sapt.md" "md"
create_file "docs/examples/06_properties.md" "md"
create_file "docs/examples/07_coupled_cluster.md" "md"
create_file "docs/examples/08_solvation.md" "md"
create_file "docs/examples/09_advanced_workflows.md" "md"

# Docs - Getting started
create_file "docs/getting-started/configuration.md" "md"
create_file "docs/getting-started/installation.md" "md"
create_file "docs/getting-started/quick-start.md" "md"
create_file "docs/getting-started/troubleshooting.md" "md"

# Docs - Theory
create_file "docs/theory/basis-sets.md" "md"
create_file "docs/theory/convergence.md" "md"
create_file "docs/theory/methods.md" "md"

# Docs - User guide
create_file "docs/user-guide/advanced-topics.md" "md"
create_file "docs/user-guide/basic-calculations.md" "md"
create_file "docs/user-guide/excited-states.md" "md"
create_file "docs/user-guide/frequencies.md" "md"
create_file "docs/user-guide/intermolecular.md" "md"
create_file "docs/user-guide/optimization.md" "md"
create_file "docs/user-guide/properties.md" "md"

echo -e "${BLUE}Tests...${NC}"

# Tests
create_file "tests/__init__.py" "py"
create_file "tests/conftest.py" "py"
create_file "tests/fixtures/__init__.py" "py"
create_file "tests/fixtures/mock_context.py" "py"
create_file "tests/fixtures/molecules.py" "py"
create_file "tests/fixtures/reference_data.py" "py"
create_file "tests/fixtures/test_files/.gitkeep" "txt"
create_file "tests/fixtures/test_files/sample_input_1.dat" "dat"
create_file "tests/fixtures/test_files/sample_input_2.dat" "dat"
create_file "tests/fixtures/test_files/sample_output_1.dat" "dat"
create_file "tests/fixtures/test_files/sample_output_2.dat" "dat"

# Tests - integration
create_file "tests/integration/__init__.py" "py"
create_file "tests/integration/test_error_recovery.py" "py"
create_file "tests/integration/test_mcp_protocol.py" "py"
create_file "tests/integration/test_psi4_interface.py" "py"
create_file "tests/integration/test_workflows.py" "py"

# Tests - performance
create_file "tests/performance/__init__.py" "py"
create_file "tests/performance/benchmark_suite.py" "py"
create_file "tests/performance/test_memory.py" "py"
create_file "tests/performance/test_speed.py" "py"

# Tests - regression
create_file "tests/regression/__init__.py" "py"
create_file "tests/regression/test_reference_values.py" "py"

# Tests - unit general
create_file "tests/unit/__init__.py" "py"
create_file "tests/unit/test_converters.py" "py"
create_file "tests/unit/test_error_handlers.py" "py"
create_file "tests/unit/test_models.py" "py"
create_file "tests/unit/test_parsers.py" "py"
create_file "tests/unit/test_validation.py" "py"

# Tests - unit tools (95 test files!)
echo "  Creating 95+ unit test files for tools..."
create_file "tests/unit/tools/__init__.py" "py"

for test_file in adc anharmonic basis_extrapolation brueckner casscf cc2 cc3 ccsd ccsd_t ccsdt charges ci cisd cis composite constrained cpcm cube_files ddcosmo detci df_mp2 dispersion ecd efp electric_moments energy eom_cc epr excited_opt fci fisapt fragment_analysis frequencies functional_scan g_tensor gradient grid_quality hessian hirshfeld hyperfine iefpcm ir_raman localization lowdin lr_ccsd mayer mcscf mcscf_gradients mp2 mp2_5 mp3 mp4 mulliken natural_orbitals nmr nmr_coupling nmr_shielding npa oniom optical_rotation optimization orbitals ord pcm polarizability population properties qmmm range_separated rasscf sapt sapt0 sapt2 sapt2_plus sapt_dft scan scs_mp2 smd solvation spin_properties symmetry tda tddft thermochemistry transition_properties uv_vis vcd wavefunction wiberg zero_field; do
    create_file "tests/unit/tools/test_$test_file.py" "py"
done

# Tests - unit utils
echo "  Creating 15+ unit test files for utils..."
create_file "tests/unit/utils/__init__.py" "py"

for test_file in basis_utils cache_manager constants convergence_helpers format_conversion geometry_utils math_utils memory_estimator molecular_descriptors parallel_utils symmetry_utils unit_conversion visualization; do
    create_file "tests/unit/utils/test_$test_file.py" "py"
done

echo ""

# ============================================
# FINAL STATISTICS
# ============================================

TOTAL_DIRS=$(find . -type d 2>/dev/null | wc -l)
TOTAL_FILES=$(find . -type f 2>/dev/null | wc -l)
TOTAL_PY=$(find . -name "*.py" 2>/dev/null | wc -l)
TOTAL_MD=$(find . -name "*.md" 2>/dev/null | wc -l)
TOTAL_YAML=$(find . -name "*.y*ml" 2>/dev/null | wc -l)

echo -e "${GREEN}✓ File creation complete!${NC}"
echo ""
echo "📊 Final Statistics:"
echo "  Total directories created: $DIR_COUNT"
echo "  Total files created: $FILE_COUNT"
echo ""
echo "📊 Full Project Statistics:"
echo "  Total directories: $TOTAL_DIRS"
echo "  Total files: $TOTAL_FILES"
echo "  Python files (.py): $TOTAL_PY"
echo "  Markdown files (.md): $TOTAL_MD"
echo "  YAML files (.yml/.yaml): $TOTAL_YAML"
echo ""

echo "📁 Project Structure:"
echo "  $(pwd)"
echo ""

echo "✅ Verification Commands:"
echo "  Run: tree -L 2 src/"
echo "  Run: find . -name '*.py' | wc -l"
echo "  Run: find . -type d | wc -l"
echo ""

echo "🚀 Next Steps:"
echo "  1. Review the structure: tree -L 3"
echo "  2. Create virtual environment: python -m venv venv"
echo "  3. Activate environment: source venv/bin/activate"
echo "  4. Install Psi4: conda install -c psi4 psi4"
echo "  5. Install dependencies: pip install mcp[cli] fastmcp ase numpy pydantic pytest"
echo "  6. Start implementing according to ../psi4_mcp_comprehensive_plan.md"
echo ""

echo -e "${GREEN}✅ All 380+ files created successfully! 🎉${NC}"
echo ""
echo "Ready to start implementation!"
echo ""
