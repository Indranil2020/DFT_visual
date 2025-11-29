#!/bin/bash
# Psi4 MCP Server - Create All Placeholder Files
# Creates all 380+ files from psi4_mcp_complete_tree.txt
# Version: 1.0
# Date: 2025-11-27

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="psi4-mcp-server"

echo "=========================================="
echo "Creating All Placeholder Files"
echo "=========================================="
echo ""

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: $PROJECT_ROOT directory not found!"
    echo "Run ./setup_structure.sh first"
    exit 1
fi

cd "$PROJECT_ROOT"
echo -e "${BLUE}Working in: $(pwd)${NC}"
echo ""

# Counter
FILE_COUNT=0

# Function to create file with header comment
create_file() {
    local filepath=$1
    local filetype=$2

    if [ ! -f "$filepath" ]; then
        case "$filetype" in
            py)
                cat > "$filepath" << 'EOF'
"""
Psi4 MCP Server - Placeholder Module

This file is part of the Psi4 MCP Server implementation.
TODO: Implement according to psi4_mcp_comprehensive_plan.md
"""

# TODO: Add implementation
pass
EOF
                ;;
            md)
                cat > "$filepath" << 'EOF'
# Placeholder Documentation

TODO: Add documentation content

## Overview

This document is part of the Psi4 MCP Server documentation.

## Content

To be added during implementation.
EOF
                ;;
            yaml|yml)
                cat > "$filepath" << 'EOF'
# Psi4 MCP Server Configuration
# TODO: Add configuration settings
EOF
                ;;
            toml)
                cat > "$filepath" << 'EOF'
# Psi4 MCP Server Configuration
# TODO: Add TOML configuration
EOF
                ;;
            txt)
                echo "# Placeholder file - TODO: Add content" > "$filepath"
                ;;
            sh)
                cat > "$filepath" << 'EOF'
#!/bin/bash
# Psi4 MCP Server Script
# TODO: Implement script functionality

echo "TODO: Implement this script"
EOF
                chmod +x "$filepath"
                ;;
            *)
                touch "$filepath"
                ;;
        esac
        ((FILE_COUNT++))
    fi
}

echo -e "${BLUE}Creating top-level files...${NC}"

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
create_file "Dockerfile" "txt"
create_file "docker-compose.yml" "yaml"
create_file ".gitattributes" "txt"

echo -e "${BLUE}Creating GitHub workflow files...${NC}"

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

echo -e "${BLUE}Creating config files...${NC}"

# Config files
create_file "config/default.yaml" "yaml"
create_file "config/development.yaml" "yaml"
create_file "config/production.yaml" "yaml"
create_file "config/testing.yaml" "yaml"
create_file "config/logging.yaml" "yaml"

echo -e "${BLUE}Creating scripts...${NC}"

# Scripts
create_file "scripts/build_docker.sh" "sh"
create_file "scripts/cleanup.sh" "sh"
create_file "scripts/deploy.sh" "sh"
create_file "scripts/generate_docs.sh" "sh"
create_file "scripts/install.sh" "sh"
create_file "scripts/run_tests.sh" "sh"
create_file "scripts/setup_conda.sh" "sh"

echo -e "${GREEN}✓ Top-level files created${NC}"
echo ""
echo "Files created so far: $FILE_COUNT"
echo ""
echo -e "${YELLOW}Continuing with source code files...${NC}"
echo "This will create 280+ Python files. Please wait..."
echo ""

# ============================================
# SOURCE CODE FILES (src/psi4_mcp/)
# ============================================

echo -e "${BLUE}Creating core source files...${NC}"

# Core files
create_file "src/psi4_mcp/__version__.py" "py"
create_file "src/psi4_mcp/config.py" "py"
create_file "src/psi4_mcp/server.py" "py"

# CLI files
create_file "src/psi4_mcp/cli/main.py" "py"
create_file "src/psi4_mcp/cli/utils.py" "py"
create_file "src/psi4_mcp/cli/commands/convert.py" "py"
create_file "src/psi4_mcp/cli/commands/start.py" "py"
create_file "src/psi4_mcp/cli/commands/test.py" "py"
create_file "src/psi4_mcp/cli/commands/validate.py" "py"

# Database files
create_file "src/psi4_mcp/database/manager.py" "py"
create_file "src/psi4_mcp/database/queries.py" "py"
create_file "src/psi4_mcp/database/schema.py" "py"
create_file "src/psi4_mcp/database/migrations/v001_initial.py" "py"

# Integration files
create_file "src/psi4_mcp/integrations/ase.py" "py"
create_file "src/psi4_mcp/integrations/cclib.py" "py"
create_file "src/psi4_mcp/integrations/molssi.py" "py"
create_file "src/psi4_mcp/integrations/openbabel.py" "py"
create_file "src/psi4_mcp/integrations/qcschema.py" "py"
create_file "src/psi4_mcp/integrations/rdkit.py" "py"

# Model files
create_file "src/psi4_mcp/models/base.py" "py"
create_file "src/psi4_mcp/models/errors.py" "py"
create_file "src/psi4_mcp/models/molecules.py" "py"
create_file "src/psi4_mcp/models/options.py" "py"
create_file "src/psi4_mcp/models/resources.py" "py"

# Model calculations
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
create_file "src/psi4_mcp/models/enums/basis_sets.py" "py"
create_file "src/psi4_mcp/models/enums/methods.py" "py"
create_file "src/psi4_mcp/models/enums/properties.py" "py"
create_file "src/psi4_mcp/models/enums/references.py" "py"

# Model outputs
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
create_file "src/psi4_mcp/prompts/education.py" "py"
create_file "src/psi4_mcp/prompts/methods.py" "py"
create_file "src/psi4_mcp/prompts/troubleshooting.py" "py"
create_file "src/psi4_mcp/prompts/workflows.py" "py"

# Resource files
create_file "src/psi4_mcp/resources/basis_sets.py" "py"
create_file "src/psi4_mcp/resources/benchmarks.py" "py"
create_file "src/psi4_mcp/resources/functionals.py" "py"
create_file "src/psi4_mcp/resources/literature.py" "py"
create_file "src/psi4_mcp/resources/methods.py" "py"
create_file "src/psi4_mcp/resources/molecules.py" "py"
create_file "src/psi4_mcp/resources/tutorials.py" "py"

# Script files
create_file "src/psi4_mcp/scripts/benchmark.py" "py"
create_file "src/psi4_mcp/scripts/generate_docs.py" "py"
create_file "src/psi4_mcp/scripts/install_deps.py" "py"
create_file "src/psi4_mcp/scripts/setup_env.py" "py"

echo -e "${GREEN}✓ Core source files created${NC}"
echo "Files created so far: $FILE_COUNT"
echo ""

# ============================================
# TOOLS FILES (110+ files)
# ============================================

echo -e "${BLUE}Creating tools files (this may take a moment)...${NC}"

# Core tools
create_file "src/psi4_mcp/tools/core/energy.py" "py"
create_file "src/psi4_mcp/tools/core/gradient.py" "py"
create_file "src/psi4_mcp/tools/core/hessian.py" "py"
create_file "src/psi4_mcp/tools/core/optimization.py" "py"

# Vibrational tools
create_file "src/psi4_mcp/tools/vibrational/anharmonic.py" "py"
create_file "src/psi4_mcp/tools/vibrational/frequencies.py" "py"
create_file "src/psi4_mcp/tools/vibrational/thermochemistry.py" "py"
create_file "src/psi4_mcp/tools/vibrational/vcd.py" "py"

# Properties tools
create_file "src/psi4_mcp/tools/properties/bonds.py" "py"
create_file "src/psi4_mcp/tools/properties/electric_moments.py" "py"
create_file "src/psi4_mcp/tools/properties/electrostatic.py" "py"
create_file "src/psi4_mcp/tools/properties/optical_rotation.py" "py"
create_file "src/psi4_mcp/tools/properties/orbitals.py" "py"
create_file "src/psi4_mcp/tools/properties/polarizability.py" "py"
create_file "src/psi4_mcp/tools/properties/spin_properties.py" "py"

# Properties - bonds
create_file "src/psi4_mcp/tools/properties/bonds/mayer.py" "py"
create_file "src/psi4_mcp/tools/properties/bonds/wiberg.py" "py"

# Properties - charges
create_file "src/psi4_mcp/tools/properties/charges/esp.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/hirshfeld.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/lowdin.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/mulliken.py" "py"
create_file "src/psi4_mcp/tools/properties/charges/npa.py" "py"

# Spectroscopy tools
create_file "src/psi4_mcp/tools/spectroscopy/ecd.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/ir_raman.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/ord.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/uv_vis.py" "py"

# Spectroscopy - EPR
create_file "src/psi4_mcp/tools/spectroscopy/epr/g_tensor.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/hyperfine.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/epr/zero_field.py" "py"

# Spectroscopy - NMR
create_file "src/psi4_mcp/tools/spectroscopy/nmr/coupling.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/shielding.py" "py"
create_file "src/psi4_mcp/tools/spectroscopy/nmr/spectra.py" "py"

# Excited states tools
create_file "src/psi4_mcp/tools/excited_states/adc.py" "py"
create_file "src/psi4_mcp/tools/excited_states/cis.py" "py"
create_file "src/psi4_mcp/tools/excited_states/eom_cc.py" "py"
create_file "src/psi4_mcp/tools/excited_states/excited_opt.py" "py"
create_file "src/psi4_mcp/tools/excited_states/tda.py" "py"
create_file "src/psi4_mcp/tools/excited_states/tddft.py" "py"
create_file "src/psi4_mcp/tools/excited_states/transition_properties.py" "py"

# Coupled cluster tools
create_file "src/psi4_mcp/tools/coupled_cluster/brueckner.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/cc2.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/cc3.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsd.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsd_t.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/ccsdt.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/eom_ccsd.py" "py"
create_file "src/psi4_mcp/tools/coupled_cluster/lr_ccsd.py" "py"

# Perturbation theory tools
create_file "src/psi4_mcp/tools/perturbation_theory/df_mp2.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp2.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp2_5.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp3.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/mp4.py" "py"
create_file "src/psi4_mcp/tools/perturbation_theory/scs_mp2.py" "py"

# Configuration interaction tools
create_file "src/psi4_mcp/tools/configuration_interaction/cisd.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/cisdt.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/detci.py" "py"
create_file "src/psi4_mcp/tools/configuration_interaction/fci.py" "py"

# MCSCF tools
create_file "src/psi4_mcp/tools/mcscf/casscf.py" "py"
create_file "src/psi4_mcp/tools/mcscf/mcscf_gradients.py" "py"
create_file "src/psi4_mcp/tools/mcscf/rasscf.py" "py"

# SAPT tools
create_file "src/psi4_mcp/tools/sapt/analysis.py" "py"
create_file "src/psi4_mcp/tools/sapt/fisapt.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt0.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2_plus.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt2_plus_3.py" "py"
create_file "src/psi4_mcp/tools/sapt/sapt_dft.py" "py"

# Solvation tools
create_file "src/psi4_mcp/tools/solvation/cpcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/ddcosmo.py" "py"
create_file "src/psi4_mcp/tools/solvation/iefpcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/pcm.py" "py"
create_file "src/psi4_mcp/tools/solvation/smd.py" "py"

# DFT tools
create_file "src/psi4_mcp/tools/dft/dispersion.py" "py"
create_file "src/psi4_mcp/tools/dft/functional_scan.py" "py"
create_file "src/psi4_mcp/tools/dft/grid_quality.py" "py"
create_file "src/psi4_mcp/tools/dft/range_separated.py" "py"

# Basis sets tools
create_file "src/psi4_mcp/tools/basis_sets/basis_info.py" "py"
create_file "src/psi4_mcp/tools/basis_sets/composite.py" "py"
create_file "src/psi4_mcp/tools/basis_sets/extrapolation.py" "py"

# Analysis tools
create_file "src/psi4_mcp/tools/analysis/cube_files.py" "py"
create_file "src/psi4_mcp/tools/analysis/fragment_analysis.py" "py"
create_file "src/psi4_mcp/tools/analysis/localization.py" "py"
create_file "src/psi4_mcp/tools/analysis/natural_orbitals.py" "py"
create_file "src/psi4_mcp/tools/analysis/population.py" "py"
create_file "src/psi4_mcp/tools/analysis/wavefunction.py" "py"

# Composite tools
create_file "src/psi4_mcp/tools/composite/cbs_qb3.py" "py"
create_file "src/psi4_mcp/tools/composite/g1.py" "py"
create_file "src/psi4_mcp/tools/composite/g2.py" "py"
create_file "src/psi4_mcp/tools/composite/g3.py" "py"
create_file "src/psi4_mcp/tools/composite/g4.py" "py"
create_file "src/psi4_mcp/tools/composite/w1.py" "py"

# Advanced tools
create_file "src/psi4_mcp/tools/advanced/constrained.py" "py"
create_file "src/psi4_mcp/tools/advanced/efp.py" "py"
create_file "src/psi4_mcp/tools/advanced/oniom.py" "py"
create_file "src/psi4_mcp/tools/advanced/qmmm.py" "py"
create_file "src/psi4_mcp/tools/advanced/scan.py" "py"
create_file "src/psi4_mcp/tools/advanced/symmetry.py" "py"

# Utilities tools
create_file "src/psi4_mcp/tools/utilities/batch_runner.py" "py"
create_file "src/psi4_mcp/tools/utilities/format_converter.py" "py"
create_file "src/psi4_mcp/tools/utilities/structure_builder.py" "py"
create_file "src/psi4_mcp/tools/utilities/workflow_manager.py" "py"

echo -e "${GREEN}✓ All tools files created (110+ files)${NC}"
echo "Files created so far: $FILE_COUNT"
echo ""

# ============================================
# UTILS FILES (60+ files)
# ============================================

echo -e "${BLUE}Creating utils files...${NC}"

# Basis utils
create_file "src/psi4_mcp/utils/basis/generator.py" "py"
create_file "src/psi4_mcp/utils/basis/library.py" "py"
create_file "src/psi4_mcp/utils/basis/optimizer.py" "py"
create_file "src/psi4_mcp/utils/basis/parser.py" "py"

# Caching utils
create_file "src/psi4_mcp/utils/caching/cache_manager.py" "py"
create_file "src/psi4_mcp/utils/caching/molecular.py" "py"
create_file "src/psi4_mcp/utils/caching/results.py" "py"

# Convergence utils
create_file "src/psi4_mcp/utils/convergence/optimization.py" "py"
create_file "src/psi4_mcp/utils/convergence/scf.py" "py"
create_file "src/psi4_mcp/utils/convergence/strategies.py" "py"
create_file "src/psi4_mcp/utils/convergence/tddft.py" "py"

# Conversion utils
create_file "src/psi4_mcp/utils/conversion/basis_sets.py" "py"
create_file "src/psi4_mcp/utils/conversion/geometry.py" "py"
create_file "src/psi4_mcp/utils/conversion/output.py" "py"
create_file "src/psi4_mcp/utils/conversion/units.py" "py"

# Error handling utils
create_file "src/psi4_mcp/utils/error_handling/categorization.py" "py"
create_file "src/psi4_mcp/utils/error_handling/detection.py" "py"
create_file "src/psi4_mcp/utils/error_handling/logging.py" "py"
create_file "src/psi4_mcp/utils/error_handling/recovery.py" "py"
create_file "src/psi4_mcp/utils/error_handling/suggestions.py" "py"

# Geometry utils
create_file "src/psi4_mcp/utils/geometry/alignment.py" "py"
create_file "src/psi4_mcp/utils/geometry/analysis.py" "py"
create_file "src/psi4_mcp/utils/geometry/builders.py" "py"
create_file "src/psi4_mcp/utils/geometry/symmetry.py" "py"
create_file "src/psi4_mcp/utils/geometry/transformations.py" "py"

# Helper utils
create_file "src/psi4_mcp/utils/helpers/constants.py" "py"
create_file "src/psi4_mcp/utils/helpers/math_utils.py" "py"
create_file "src/psi4_mcp/utils/helpers/string_utils.py" "py"
create_file "src/psi4_mcp/utils/helpers/units.py" "py"

# Logging utils
create_file "src/psi4_mcp/utils/logging/formatters.py" "py"
create_file "src/psi4_mcp/utils/logging/handlers.py" "py"
create_file "src/psi4_mcp/utils/logging/logger.py" "py"

# Memory utils
create_file "src/psi4_mcp/utils/memory/estimator.py" "py"
create_file "src/psi4_mcp/utils/memory/manager.py" "py"
create_file "src/psi4_mcp/utils/memory/optimizer.py" "py"

# Molecular utils
create_file "src/psi4_mcp/utils/molecular/database.py" "py"
create_file "src/psi4_mcp/utils/molecular/descriptors.py" "py"
create_file "src/psi4_mcp/utils/molecular/fingerprints.py" "py"
create_file "src/psi4_mcp/utils/molecular/similarity.py" "py"

# Parallel utils
create_file "src/psi4_mcp/utils/parallel/mpi_interface.py" "py"
create_file "src/psi4_mcp/utils/parallel/task_queue.py" "py"
create_file "src/psi4_mcp/utils/parallel/thread_manager.py" "py"

# Parsing utils
create_file "src/psi4_mcp/utils/parsing/energy.py" "py"
create_file "src/psi4_mcp/utils/parsing/frequencies.py" "py"
create_file "src/psi4_mcp/utils/parsing/generic.py" "py"
create_file "src/psi4_mcp/utils/parsing/optimization.py" "py"
create_file "src/psi4_mcp/utils/parsing/orbitals.py" "py"
create_file "src/psi4_mcp/utils/parsing/properties.py" "py"
create_file "src/psi4_mcp/utils/parsing/wavefunction.py" "py"

# Validation utils
create_file "src/psi4_mcp/utils/validation/basis_sets.py" "py"
create_file "src/psi4_mcp/utils/validation/constraints.py" "py"
create_file "src/psi4_mcp/utils/validation/geometry.py" "py"
create_file "src/psi4_mcp/utils/validation/methods.py" "py"
create_file "src/psi4_mcp/utils/validation/options.py" "py"

# Visualization utils
create_file "src/psi4_mcp/utils/visualization/molecular.py" "py"
create_file "src/psi4_mcp/utils/visualization/orbitals.py" "py"
create_file "src/psi4_mcp/utils/visualization/spectra.py" "py"
create_file "src/psi4_mcp/utils/visualization/surfaces.py" "py"

echo -e "${GREEN}✓ All utils files created (60+ files)${NC}"
echo "Files created so far: $FILE_COUNT"
echo ""

# ============================================
# TEST FILES (95+ files)
# ============================================

echo -e "${BLUE}Creating test files...${NC}"

# Test root files
create_file "tests/conftest.py" "py"

# Test fixtures
create_file "tests/fixtures/mock_context.py" "py"
create_file "tests/fixtures/molecules.py" "py"
create_file "tests/fixtures/reference_data.py" "py"
create_file "tests/fixtures/test_files/sample_input_1.dat" "txt"
create_file "tests/fixtures/test_files/sample_input_2.dat" "txt"
create_file "tests/fixtures/test_files/sample_output_1.dat" "txt"
create_file "tests/fixtures/test_files/sample_output_2.dat" "txt"

# Integration tests
create_file "tests/integration/test_error_recovery.py" "py"
create_file "tests/integration/test_mcp_protocol.py" "py"
create_file "tests/integration/test_psi4_interface.py" "py"
create_file "tests/integration/test_workflows.py" "py"

# Performance tests
create_file "tests/performance/benchmark_suite.py" "py"
create_file "tests/performance/test_memory.py" "py"
create_file "tests/performance/test_speed.py" "py"

# Regression tests
create_file "tests/regression/test_reference_values.py" "py"

# Unit tests - root level
create_file "tests/unit/test_converters.py" "py"
create_file "tests/unit/test_error_handlers.py" "py"
create_file "tests/unit/test_models.py" "py"
create_file "tests/unit/test_parsers.py" "py"
create_file "tests/unit/test_validation.py" "py"

echo -e "${BLUE}Creating unit test files for tools (95+ files)...${NC}"

# Unit tests for tools (matching each tool file)
create_file "tests/unit/tools/test_adc.py" "py"
create_file "tests/unit/tools/test_anharmonic.py" "py"
create_file "tests/unit/tools/test_basis_extrapolation.py" "py"
create_file "tests/unit/tools/test_brueckner.py" "py"
create_file "tests/unit/tools/test_casscf.py" "py"
create_file "tests/unit/tools/test_cc2.py" "py"
create_file "tests/unit/tools/test_cc3.py" "py"
create_file "tests/unit/tools/test_ccsd.py" "py"
create_file "tests/unit/tools/test_ccsd_t.py" "py"
create_file "tests/unit/tools/test_ccsdt.py" "py"
create_file "tests/unit/tools/test_charges.py" "py"
create_file "tests/unit/tools/test_ci.py" "py"
create_file "tests/unit/tools/test_cisd.py" "py"
create_file "tests/unit/tools/test_cis.py" "py"
create_file "tests/unit/tools/test_composite.py" "py"
create_file "tests/unit/tools/test_constrained.py" "py"
create_file "tests/unit/tools/test_cpcm.py" "py"
create_file "tests/unit/tools/test_cube_files.py" "py"
create_file "tests/unit/tools/test_ddcosmo.py" "py"
create_file "tests/unit/tools/test_detci.py" "py"
create_file "tests/unit/tools/test_df_mp2.py" "py"
create_file "tests/unit/tools/test_dispersion.py" "py"
create_file "tests/unit/tools/test_ecd.py" "py"
create_file "tests/unit/tools/test_efp.py" "py"
create_file "tests/unit/tools/test_electric_moments.py" "py"
create_file "tests/unit/tools/test_energy.py" "py"
create_file "tests/unit/tools/test_eom_cc.py" "py"
create_file "tests/unit/tools/test_epr.py" "py"
create_file "tests/unit/tools/test_excited_opt.py" "py"
create_file "tests/unit/tools/test_fci.py" "py"
create_file "tests/unit/tools/test_fisapt.py" "py"
create_file "tests/unit/tools/test_fragment_analysis.py" "py"
create_file "tests/unit/tools/test_frequencies.py" "py"
create_file "tests/unit/tools/test_functional_scan.py" "py"
create_file "tests/unit/tools/test_g_tensor.py" "py"
create_file "tests/unit/tools/test_gradient.py" "py"
create_file "tests/unit/tools/test_grid_quality.py" "py"
create_file "tests/unit/tools/test_hessian.py" "py"
create_file "tests/unit/tools/test_hirshfeld.py" "py"
create_file "tests/unit/tools/test_hyperfine.py" "py"
create_file "tests/unit/tools/test_iefpcm.py" "py"
create_file "tests/unit/tools/test_ir_raman.py" "py"
create_file "tests/unit/tools/test_localization.py" "py"
create_file "tests/unit/tools/test_lowdin.py" "py"
create_file "tests/unit/tools/test_lr_ccsd.py" "py"
create_file "tests/unit/tools/test_mayer.py" "py"
create_file "tests/unit/tools/test_mcscf.py" "py"
create_file "tests/unit/tools/test_mcscf_gradients.py" "py"
create_file "tests/unit/tools/test_mp2.py" "py"
create_file "tests/unit/tools/test_mp2_5.py" "py"
create_file "tests/unit/tools/test_mp3.py" "py"
create_file "tests/unit/tools/test_mp4.py" "py"
create_file "tests/unit/tools/test_mulliken.py" "py"
create_file "tests/unit/tools/test_natural_orbitals.py" "py"
create_file "tests/unit/tools/test_nmr.py" "py"
create_file "tests/unit/tools/test_nmr_coupling.py" "py"
create_file "tests/unit/tools/test_nmr_shielding.py" "py"
create_file "tests/unit/tools/test_npa.py" "py"
create_file "tests/unit/tools/test_oniom.py" "py"
create_file "tests/unit/tools/test_optical_rotation.py" "py"
create_file "tests/unit/tools/test_optimization.py" "py"
create_file "tests/unit/tools/test_orbitals.py" "py"
create_file "tests/unit/tools/test_ord.py" "py"
create_file "tests/unit/tools/test_pcm.py" "py"
create_file "tests/unit/tools/test_polarizability.py" "py"
create_file "tests/unit/tools/test_population.py" "py"
create_file "tests/unit/tools/test_properties.py" "py"
create_file "tests/unit/tools/test_qmmm.py" "py"
create_file "tests/unit/tools/test_range_separated.py" "py"
create_file "tests/unit/tools/test_rasscf.py" "py"
create_file "tests/unit/tools/test_sapt.py" "py"
create_file "tests/unit/tools/test_sapt0.py" "py"
create_file "tests/unit/tools/test_sapt2.py" "py"
create_file "tests/unit/tools/test_sapt2_plus.py" "py"
create_file "tests/unit/tools/test_sapt_dft.py" "py"
create_file "tests/unit/tools/test_scan.py" "py"
create_file "tests/unit/tools/test_scs_mp2.py" "py"
create_file "tests/unit/tools/test_smd.py" "py"
create_file "tests/unit/tools/test_solvation.py" "py"
create_file "tests/unit/tools/test_spin_properties.py" "py"
create_file "tests/unit/tools/test_symmetry.py" "py"
create_file "tests/unit/tools/test_tda.py" "py"
create_file "tests/unit/tools/test_tddft.py" "py"
create_file "tests/unit/tools/test_thermochemistry.py" "py"
create_file "tests/unit/tools/test_transition_properties.py" "py"
create_file "tests/unit/tools/test_uv_vis.py" "py"
create_file "tests/unit/tools/test_vcd.py" "py"
create_file "tests/unit/tools/test_wavefunction.py" "py"
create_file "tests/unit/tools/test_wiberg.py" "py"
create_file "tests/unit/tools/test_zero_field.py" "py"

# Unit tests for utils
create_file "tests/unit/utils/test_basis_utils.py" "py"
create_file "tests/unit/utils/test_cache_manager.py" "py"
create_file "tests/unit/utils/test_constants.py" "py"
create_file "tests/unit/utils/test_convergence_helpers.py" "py"
create_file "tests/unit/utils/test_format_conversion.py" "py"
create_file "tests/unit/utils/test_geometry_utils.py" "py"
create_file "tests/unit/utils/test_math_utils.py" "py"
create_file "tests/unit/utils/test_memory_estimator.py" "py"
create_file "tests/unit/utils/test_molecular_descriptors.py" "py"
create_file "tests/unit/utils/test_parallel_utils.py" "py"
create_file "tests/unit/utils/test_symmetry_utils.py" "py"
create_file "tests/unit/utils/test_unit_conversion.py" "py"
create_file "tests/unit/utils/test_visualization.py" "py"

echo -e "${GREEN}✓ All test files created (95+ files)${NC}"
echo "Files created so far: $FILE_COUNT"
echo ""

# ============================================
# DOCUMENTATION FILES (35+ files)
# ============================================

echo -e "${BLUE}Creating documentation files...${NC}"

# Docs root
create_file "docs/index.md" "md"

# Assets
create_file "docs/assets/architecture_diagram.png" "txt"
create_file "docs/assets/logo.png" "txt"

# API Reference
create_file "docs/api-reference/models.md" "md"
create_file "docs/api-reference/resources.md" "md"
create_file "docs/api-reference/tools.md" "md"
create_file "docs/api-reference/utilities.md" "md"

# Developer Guide
create_file "docs/developer-guide/adding-tools.md" "md"
create_file "docs/developer-guide/architecture.md" "md"
create_file "docs/developer-guide/debugging.md" "md"
create_file "docs/developer-guide/testing.md" "md"

# Examples
create_file "docs/examples/01_basic_energy.md" "md"
create_file "docs/examples/02_geometry_opt.md" "md"
create_file "docs/examples/03_frequencies.md" "md"
create_file "docs/examples/04_tddft.md" "md"
create_file "docs/examples/05_sapt.md" "md"
create_file "docs/examples/06_properties.md" "md"
create_file "docs/examples/07_coupled_cluster.md" "md"
create_file "docs/examples/08_solvation.md" "md"
create_file "docs/examples/09_advanced_workflows.md" "md"

# Getting Started
create_file "docs/getting-started/configuration.md" "md"
create_file "docs/getting-started/installation.md" "md"
create_file "docs/getting-started/quick-start.md" "md"
create_file "docs/getting-started/troubleshooting.md" "md"

# Theory
create_file "docs/theory/basis-sets.md" "md"
create_file "docs/theory/convergence.md" "md"
create_file "docs/theory/methods.md" "md"

# User Guide
create_file "docs/user-guide/advanced-topics.md" "md"
create_file "docs/user-guide/basic-calculations.md" "md"
create_file "docs/user-guide/excited-states.md" "md"
create_file "docs/user-guide/frequencies.md" "md"
create_file "docs/user-guide/intermolecular.md" "md"
create_file "docs/user-guide/optimization.md" "md"
create_file "docs/user-guide/properties.md" "md"

echo -e "${GREEN}✓ Documentation files created${NC}"
echo ""

# ============================================
# BENCHMARK FILES
# ============================================

echo -e "${BLUE}Creating benchmark files...${NC}"

# Accuracy benchmarks
create_file "benchmarks/accuracy/energies.py" "py"
create_file "benchmarks/accuracy/geometries.py" "py"
create_file "benchmarks/accuracy/properties.py" "py"

# Performance benchmarks
create_file "benchmarks/performance/execution_time.py" "py"
create_file "benchmarks/performance/memory_usage.py" "py"
create_file "benchmarks/performance/parallel_scaling.py" "py"

# Results
create_file "benchmarks/results/accuracy_results.json" "txt"
create_file "benchmarks/results/performance_results.json" "txt"

echo -e "${GREEN}✓ Benchmark files created${NC}"
echo ""

# ============================================
# DATA FILES
# ============================================

echo -e "${BLUE}Creating data files...${NC}"

# Basis sets (placeholder files)
create_file "data/basis_sets/dunning/cc-pVDZ.gbs" "txt"
create_file "data/basis_sets/dunning/cc-pVTZ.gbs" "txt"
create_file "data/basis_sets/dunning/cc-pVQZ.gbs" "txt"
create_file "data/basis_sets/dunning/cc-pV5Z.gbs" "txt"
create_file "data/basis_sets/karlsruhe/def2-SVP.gbs" "txt"
create_file "data/basis_sets/karlsruhe/def2-TZVP.gbs" "txt"
create_file "data/basis_sets/karlsruhe/def2-QZVP.gbs" "txt"
create_file "data/basis_sets/pople/3-21G.gbs" "txt"
create_file "data/basis_sets/pople/6-31G.gbs" "txt"
create_file "data/basis_sets/pople/6-311G.gbs" "txt"
create_file "data/basis_sets/pople/6-311++G.gbs" "txt"
create_file "data/basis_sets/sto/STO-3G.gbs" "txt"

# Literature
create_file "data/literature/benchmarks.json" "txt"
create_file "data/literature/citations.bib" "txt"

# Molecules
create_file "data/molecules/benchmarks/g2_set.xyz" "txt"
create_file "data/molecules/benchmarks/s22_set.xyz" "txt"
create_file "data/molecules/benchmarks/s66_set.xyz" "txt"
create_file "data/molecules/common/benzene.xyz" "txt"
create_file "data/molecules/common/ethane.xyz" "txt"
create_file "data/molecules/common/methane.xyz" "txt"
create_file "data/molecules/common/water.xyz" "txt"
create_file "data/molecules/common/ammonia.xyz" "txt"
create_file "data/molecules/test_set/test_molecule_1.xyz" "txt"
create_file "data/molecules/test_set/test_molecule_2.xyz" "txt"
create_file "data/molecules/test_set/test_molecule_3.xyz" "txt"

# Parameters
create_file "data/parameters/dispersion_parameters.json" "txt"
create_file "data/parameters/functional_parameters.json" "txt"
create_file "data/parameters/solvation_parameters.json" "txt"

# Reference data
create_file "data/reference_data/energies.json" "txt"
create_file "data/reference_data/frequencies.json" "txt"
create_file "data/reference_data/geometries.json" "txt"
create_file "data/reference_data/properties.json" "txt"

echo -e "${GREEN}✓ Data files created${NC}"
echo ""

# ============================================
# DEPLOYMENT FILES
# ============================================

echo -e "${BLUE}Creating deployment files...${NC}"

# Helm charts
create_file "deployment/helm/psi4-mcp/Chart.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/values.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/deployment.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/service.yaml" "yaml"
create_file "deployment/helm/psi4-mcp/templates/configmap.yaml" "yaml"

# Kubernetes
create_file "deployment/kubernetes/deployment.yaml" "yaml"
create_file "deployment/kubernetes/service.yaml" "yaml"
create_file "deployment/kubernetes/configmap.yaml" "yaml"

# Supervisor
create_file "deployment/supervisor/psi4_mcp.conf" "txt"

# Systemd
create_file "deployment/systemd/psi4-mcp.service" "txt"

echo -e "${GREEN}✓ Deployment files created${NC}"
echo ""

# ============================================
# EXAMPLE FILES
# ============================================

echo -e "${BLUE}Creating example files...${NC}"

# Example molecules
create_file "examples/molecules/xyz/water.xyz" "txt"
create_file "examples/molecules/xyz/benzene.xyz" "txt"
create_file "examples/molecules/xyz/ethanol.xyz" "txt"
create_file "examples/molecules/pdb/protein_fragment.pdb" "txt"
create_file "examples/molecules/cif/crystal.cif" "txt"

# Example notebooks
create_file "examples/notebooks/01_basic_calculations.ipynb" "txt"
create_file "examples/notebooks/02_optimization.ipynb" "txt"
create_file "examples/notebooks/03_frequencies.ipynb" "txt"
create_file "examples/notebooks/04_excited_states.ipynb" "txt"
create_file "examples/notebooks/05_sapt_analysis.ipynb" "txt"

# Example Python scripts - basic
create_file "examples/python/basic/energy_calculation.py" "py"
create_file "examples/python/basic/geometry_optimization.py" "py"
create_file "examples/python/basic/frequency_analysis.py" "py"

# Example Python scripts - intermediate
create_file "examples/python/intermediate/basis_set_comparison.py" "py"
create_file "examples/python/intermediate/method_comparison.py" "py"
create_file "examples/python/intermediate/property_calculation.py" "py"
create_file "examples/python/intermediate/tddft_spectrum.py" "py"

# Example Python scripts - advanced
create_file "examples/python/advanced/coupled_cluster_benchmark.py" "py"
create_file "examples/python/advanced/custom_workflow.py" "py"
create_file "examples/python/advanced/parallel_calculations.py" "py"
create_file "examples/python/advanced/sapt_analysis.py" "py"

# Example Python scripts - workflows
create_file "examples/python/workflows/conformer_search.py" "py"
create_file "examples/python/workflows/reaction_pathway.py" "py"
create_file "examples/python/workflows/spectroscopy_workflow.py" "py"

echo -e "${GREEN}✓ Example files created${NC}"
echo ""

# ============================================
# NOTEBOOK FILES
# ============================================

echo -e "${BLUE}Creating notebook files...${NC}"

# Development notebooks
create_file "notebooks/development/01_tool_development.ipynb" "txt"
create_file "notebooks/development/02_testing_strategies.ipynb" "txt"
create_file "notebooks/development/03_performance_profiling.ipynb" "txt"

# Exploration notebooks
create_file "notebooks/exploration/basis_set_exploration.ipynb" "txt"
create_file "notebooks/exploration/method_exploration.ipynb" "txt"
create_file "notebooks/exploration/property_exploration.ipynb" "txt"

# Presentation notebooks
create_file "notebooks/presentations/demo_basic.ipynb" "txt"
create_file "notebooks/presentations/demo_advanced.ipynb" "txt"
create_file "notebooks/presentations/tutorial.ipynb" "txt"

echo -e "${GREEN}✓ Notebook files created${NC}"
echo ""

# ============================================
# FINAL STATISTICS AND COMPLETION
# ============================================

echo ""
echo "=========================================="
echo -e "${GREEN}✨ All Files Created! ✨${NC}"
echo "=========================================="
echo ""

# Count final statistics
TOTAL_DIRS=$(find . -type d 2>/dev/null | wc -l)
TOTAL_FILES=$(find . -type f 2>/dev/null | wc -l)
TOTAL_PY=$(find . -name "*.py" 2>/dev/null | wc -l)
TOTAL_MD=$(find . -name "*.md" 2>/dev/null | wc -l)
TOTAL_YAML=$(find . -name "*.y*ml" 2>/dev/null | wc -l)

echo "📊 Final Statistics:"
echo "  Total directories: $TOTAL_DIRS"
echo "  Total files: $TOTAL_FILES"
echo "  Python files (.py): $TOTAL_PY"
echo "  Markdown files (.md): $TOTAL_MD"
echo "  YAML files (.yml/.yaml): $TOTAL_YAML"
echo "  Files created by script: $FILE_COUNT"
echo ""

echo "📁 Project Structure:"
echo "  $(pwd)"
echo ""

echo "✅ Verification:"
echo "  Run: tree -L 2 src/"
echo "  Run: find . -name '*.py' | wc -l"
echo ""

echo "🚀 Next Steps:"
echo "  1. Review the structure: tree -L 3"
echo "  2. Create virtual environment: python -m venv venv"
echo "  3. Activate environment: source venv/bin/activate"
echo "  4. Install Psi4: conda install -c psi4 psi4"
echo "  5. Install dependencies: pip install mcp[cli] fastmcp ase numpy pydantic pytest"
echo "  6. Start implementing according to ../psi4_mcp_comprehensive_plan.md"
echo ""

echo -e "${GREEN}All placeholder files created successfully! 🎉${NC}"
echo ""
echo "Ready to start implementation!"
echo ""


