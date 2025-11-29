#!/bin/bash
# Psi4 MCP Server - Complete Directory Structure Setup Script
# This script creates ALL directories and __init__.py files for the project
# DESIGNED FOR: Subfolder within existing git repository (DFT_visual/DFT_MCP/psi4/)
# Version: 3.0
# Date: 2025-11-27

set -e  # Exit on error

echo "=========================================="
echo "Psi4 MCP Server - Structure Setup"
echo "=========================================="
echo ""
echo "This script will create the psi4-mcp-server"
echo "project structure in the current directory."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Determine the project root directory
# Since this is a subfolder in an existing git repo, create project in current dir
PROJECT_ROOT="psi4-mcp-server"

# Check if project directory already exists
if [ -d "$PROJECT_ROOT" ]; then
    echo -e "${YELLOW}Warning: Directory '$PROJECT_ROOT' already exists.${NC}"
    echo -e "${YELLOW}This will add/update files in the existing directory.${NC}"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Setup cancelled.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Creating new project directory: $PROJECT_ROOT${NC}"
    mkdir -p "$PROJECT_ROOT"
fi

cd "$PROJECT_ROOT"
echo -e "${BLUE}Working directory: $(pwd)${NC}"
echo ""

echo -e "${BLUE}Creating complete directory structure...${NC}"

# ============================================
# DIRECTORY CREATION (Complete Structure)
# ============================================

# Top-level directories
echo -e "${BLUE}  → Creating top-level directories...${NC}"
mkdir -p .github/{ISSUE_TEMPLATE,workflows}
mkdir -p benchmarks/{accuracy,performance,results}
mkdir -p config
mkdir -p data
mkdir -p deployment
mkdir -p docs
mkdir -p examples
mkdir -p notebooks
mkdir -p scripts
mkdir -p src
mkdir -p tests

# Data directories
echo -e "${BLUE}  → Creating data directories...${NC}"
mkdir -p data/basis_sets/{dunning,karlsruhe,pople,sto}
mkdir -p data/literature
mkdir -p data/molecules/{benchmarks,common,test_set}
mkdir -p data/parameters
mkdir -p data/reference_data

# Deployment directories
echo -e "${BLUE}  → Creating deployment directories...${NC}"
mkdir -p deployment/helm/psi4-mcp/templates
mkdir -p deployment/kubernetes
mkdir -p deployment/supervisor
mkdir -p deployment/systemd

# Documentation directories
echo -e "${BLUE}  → Creating documentation directories...${NC}"
mkdir -p docs/assets/screenshots
mkdir -p docs/api-reference
mkdir -p docs/developer-guide
mkdir -p docs/examples
mkdir -p docs/getting-started
mkdir -p docs/theory
mkdir -p docs/user-guide

# Examples directories
echo -e "${BLUE}  → Creating examples directories...${NC}"
mkdir -p examples/molecules/{cif,pdb,xyz}
mkdir -p examples/notebooks
mkdir -p examples/python/{advanced,basic,intermediate,workflows}

# Notebooks directories
echo -p "${BLUE}  → Creating notebooks directories...${NC}"
mkdir -p notebooks/{development,exploration,presentations}

# Scripts directory
echo -e "${BLUE}  → Creating scripts directory...${NC}"
mkdir -p scripts

# ============================================
# SOURCE CODE STRUCTURE (src/psi4_mcp/)
# ============================================

echo -e "${BLUE}  → Creating source code structure...${NC}"

# Main package
mkdir -p src/psi4_mcp

# CLI
mkdir -p src/psi4_mcp/cli/commands

# Database
mkdir -p src/psi4_mcp/database/migrations

# Integrations
mkdir -p src/psi4_mcp/integrations

# Models (with all subdirectories)
mkdir -p src/psi4_mcp/models/{calculations,enums,outputs}

# Prompts
mkdir -p src/psi4_mcp/prompts

# Resources
mkdir -p src/psi4_mcp/resources

# Scripts
mkdir -p src/psi4_mcp/scripts

# ============================================
# TOOLS - ALL 17 CATEGORIES
# ============================================

echo -e "${BLUE}  → Creating tools directories (17 categories)...${NC}"

mkdir -p src/psi4_mcp/tools/advanced
mkdir -p src/psi4_mcp/tools/analysis
mkdir -p src/psi4_mcp/tools/basis_sets
mkdir -p src/psi4_mcp/tools/composite
mkdir -p src/psi4_mcp/tools/configuration_interaction
mkdir -p src/psi4_mcp/tools/core
mkdir -p src/psi4_mcp/tools/coupled_cluster
mkdir -p src/psi4_mcp/tools/dft
mkdir -p src/psi4_mcp/tools/excited_states
mkdir -p src/psi4_mcp/tools/mcscf
mkdir -p src/psi4_mcp/tools/perturbation_theory
mkdir -p src/psi4_mcp/tools/properties/{bonds,charges}
mkdir -p src/psi4_mcp/tools/sapt
mkdir -p src/psi4_mcp/tools/solvation
mkdir -p src/psi4_mcp/tools/spectroscopy/{epr,nmr}
mkdir -p src/psi4_mcp/tools/utilities
mkdir -p src/psi4_mcp/tools/vibrational

# ============================================
# UTILS - ALL 14 CATEGORIES
# ============================================

echo -e "${BLUE}  → Creating utils directories (14 categories)...${NC}"

mkdir -p src/psi4_mcp/utils/basis
mkdir -p src/psi4_mcp/utils/caching
mkdir -p src/psi4_mcp/utils/convergence
mkdir -p src/psi4_mcp/utils/conversion
mkdir -p src/psi4_mcp/utils/error_handling
mkdir -p src/psi4_mcp/utils/geometry
mkdir -p src/psi4_mcp/utils/helpers
mkdir -p src/psi4_mcp/utils/logging
mkdir -p src/psi4_mcp/utils/memory
mkdir -p src/psi4_mcp/utils/molecular
mkdir -p src/psi4_mcp/utils/parallel
mkdir -p src/psi4_mcp/utils/parsing
mkdir -p src/psi4_mcp/utils/validation
mkdir -p src/psi4_mcp/utils/visualization

# ============================================
# TESTS STRUCTURE
# ============================================

echo -e "${BLUE}  → Creating tests directories...${NC}"

mkdir -p tests/fixtures/test_files
mkdir -p tests/integration
mkdir -p tests/performance
mkdir -p tests/regression
mkdir -p tests/unit/{tools,utils}

echo -e "${GREEN}✓ All directories created (95 directories)${NC}"
echo ""

# ============================================
# CREATE __init__.py FILES
# ============================================

echo -e "${BLUE}Creating __init__.py files...${NC}"

# Function to create __init__.py in a directory and all subdirectories
create_init_files() {
    local dir=$1
    if [ -d "$dir" ]; then
        find "$dir" -type d -exec touch {}/__init__.py \;
        echo -e "${GREEN}  ✓ Created __init__.py files in $dir${NC}"
    fi
}

# Create __init__.py in all Python package directories
create_init_files "src/psi4_mcp"
create_init_files "tests"
create_init_files "benchmarks"

echo -e "${GREEN}✓ All __init__.py files created${NC}"
echo ""

# ============================================
# CREATE ESSENTIAL PLACEHOLDER FILES
# ============================================

echo -e "${BLUE}Creating essential placeholder files...${NC}"

# Create .gitkeep files in empty directories that need to be tracked
touch benchmarks/results/.gitkeep
touch docs/assets/screenshots/.gitkeep
touch tests/fixtures/test_files/.gitkeep
touch data/molecules/benchmarks/.gitkeep
touch data/molecules/common/.gitkeep
touch data/molecules/test_set/.gitkeep
touch data/basis_sets/dunning/.gitkeep
touch data/basis_sets/karlsruhe/.gitkeep
touch data/basis_sets/pople/.gitkeep
touch data/basis_sets/sto/.gitkeep

echo -e "${GREEN}✓ Placeholder files created${NC}"
echo ""

# ============================================
# CREATE .gitignore
# ============================================

echo -e "${BLUE}Creating .gitignore...${NC}"

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Psi4 specific
psi4_output.dat
timer.dat
*.clean
*.180
*.dat.1
*.dat.2
*.32
*.wfn
*.molden
*.cube
*.fchk
*.checkpoint

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
*.bak
*.tmp

# Project specific
/tmp/
/scratch/
scratch_*/

# Documentation builds
docs/_build/
docs/_static/
docs/_templates/
site/

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb_checkpoints/

# Environment variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"
echo ""

# ============================================
# CREATE ESSENTIAL CONFIGURATION FILES
# ============================================

echo -e "${BLUE}Creating essential configuration files...${NC}"

# Create .env.example
cat > .env.example << 'EOF'
# Psi4 MCP Server Environment Variables
# Copy this file to .env and customize

# Psi4 Configuration
PSI_SCRATCH=/tmp/psi4_scratch
PSI4_MEMORY=2GB
PSI4_NUM_THREADS=4

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3000
MCP_LOG_LEVEL=INFO

# Optional: Database
# DATABASE_URL=sqlite:///psi4_mcp.db
EOF

# Create README.md
cat > README.md << 'EOF'
# Psi4 MCP Server

Model Context Protocol (MCP) server for Psi4 quantum chemistry calculations.

## Quick Start

See `docs/getting-started/quick-start.md` for installation and usage instructions.

## Documentation

- **Getting Started**: `docs/getting-started/`
- **User Guide**: `docs/user-guide/`
- **API Reference**: `docs/api-reference/`
- **Developer Guide**: `docs/developer-guide/`

## Project Structure

Created from comprehensive planning documents in `DFT_MCP/psi4/`.

## License

See LICENSE file.
EOF

echo -e "${GREEN}✓ Configuration files created${NC}"
echo ""

# ============================================
# STATISTICS AND COMPLETION
# ============================================

# Count what we created
DIR_COUNT=$(find . -type d 2>/dev/null | wc -l)
FILE_COUNT=$(find . -type f 2>/dev/null | wc -l)
INIT_COUNT=$(find . -name "__init__.py" 2>/dev/null | wc -l)

echo "=========================================="
echo -e "${GREEN}✨ Setup Complete! ✨${NC}"
echo "=========================================="
echo ""
echo "📊 Statistics:"
echo "  Directories created: $DIR_COUNT"
echo "  Files created: $FILE_COUNT"
echo "  __init__.py files: $INIT_COUNT"
echo ""
echo "📁 Project Location:"
echo "  $(pwd)"
echo ""
echo "🚀 Next Steps:"
echo "  1. Review the structure:"
echo "     tree -L 3 src/"
echo ""
echo "  2. Create virtual environment:"
echo "     python -m venv venv"
echo "     source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo ""
echo "  3. Install Psi4 and dependencies:"
echo "     conda install -c psi4 psi4"
echo "     pip install mcp[cli] fastmcp ase numpy pydantic pytest"
echo ""
echo "  4. Start implementing (see planning docs):"
echo "     ../psi4_mcp_executive_summary.md"
echo "     ../psi4_mcp_comprehensive_plan.md"
echo ""
echo "📚 Planning Documentation (in parent directory):"
echo "  • Executive Summary: ../psi4_mcp_executive_summary.md"
echo "  • Complete Plan: ../psi4_mcp_comprehensive_plan.md"
echo "  • Architecture: ../psi4_mcp_architecture.md"
echo "  • Technical Spec: ../psi4_mcp_technical_spec.md"
echo "  • Checklist: ../psi4_mcp_checklist.md"
echo "  • Complete Tree: ../psi4_mcp_complete_tree.txt"
echo ""
echo "✅ Verification:"
echo "  Run: tree -L 2 src/"
echo "  Expected: 95 directories, 380+ files (when fully implemented)"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
