# Psi4 MCP Server - Setup Instructions

**Version:** 3.0  
**Date:** 2025-11-27  
**Location:** Subfolder within DFT_visual git repository

---

## 📋 Overview

The `setup_structure.sh` script has been **modified** to work within your existing git repository structure:

```
/home/niel/git/DFT_visual/          ← Main git repository
├── DFT_MCP/
│   └── psi4/                        ← Planning documents location
│       ├── setup_structure.sh       ← Modified setup script (v3.0)
│       ├── psi4_mcp_executive_summary.md
│       ├── psi4_mcp_comprehensive_plan.md
│       ├── psi4_mcp_architecture.md
│       ├── psi4_mcp_technical_spec.md
│       ├── psi4_mcp_checklist.md
│       ├── psi4_mcp_complete_tree.txt
│       └── psi4-mcp-server/         ← Will be created here
│           ├── src/
│           ├── tests/
│           ├── docs/
│           └── ... (complete structure)
```

---

## 🔄 What Changed from Original Script

### Version 2.0 → Version 3.0 Changes:

1. **Subfolder Awareness**
   - Creates `psi4-mcp-server/` directory in current location
   - Works within existing git repository (no new git init)
   - Preserves parent git structure

2. **Enhanced Safety**
   - Checks if directory exists before creating
   - Prompts for confirmation if directory exists
   - Better error handling with colored output

3. **Complete Structure**
   - All 95 directories from `psi4_mcp_complete_tree.txt`
   - All 17 tool categories
   - All 14 utility categories
   - Complete test structure

4. **Additional Files**
   - Enhanced `.gitignore` with Psi4-specific patterns
   - `.env.example` for environment configuration
   - `README.md` with quick start guide
   - More `.gitkeep` files for empty directories

5. **Better Documentation**
   - Colored progress output
   - Statistics at completion
   - Clear next steps
   - References to planning documents

---

## 🚀 How to Use

### Step 1: Navigate to Planning Directory

```bash
cd /home/niel/git/DFT_visual/DFT_MCP/psi4/
```

### Step 2: Make Script Executable (if not already)

```bash
chmod +x setup_structure.sh
```

### Step 3: Run the Setup Script

```bash
./setup_structure.sh
```

### Step 4: Review the Created Structure

```bash
cd psi4-mcp-server
tree -L 2 src/
```

---

## 📊 What Gets Created

### Directory Statistics:
- **Total Directories:** 95
- **Total Files:** 380+ (when fully implemented)
- **Python Packages:** All with `__init__.py`

### Main Components:

```
psi4-mcp-server/
├── src/psi4_mcp/           # Main source code (280+ files)
│   ├── tools/              # 17 categories, 110+ files
│   ├── utils/              # 14 categories, 60+ files
│   ├── models/             # 30 files
│   ├── resources/          # 7 files
│   ├── prompts/            # 4 files
│   ├── cli/                # 6 files
│   ├── database/           # 5 files
│   └── integrations/       # 6 files
├── tests/                  # 95+ test files
├── docs/                   # 35+ documentation files
├── examples/               # 25+ example files
├── data/                   # 25+ data files
├── config/                 # 5 configuration files
├── scripts/                # 7 build scripts
├── deployment/             # 10 deployment configs
└── benchmarks/             # 10 benchmark files
```

---

## ✅ Verification

After running the script, verify the structure:

```bash
# Count directories
find psi4-mcp-server -type d | wc -l
# Expected: ~95

# Count Python files (will grow as you implement)
find psi4-mcp-server -name "*.py" | wc -l
# Expected: Starts with __init__.py files, grows to 280+

# Check critical directories exist
ls -la psi4-mcp-server/src/psi4_mcp/tools/
ls -la psi4-mcp-server/src/psi4_mcp/utils/
ls -la psi4-mcp-server/tests/
```

---

## 🎯 Next Steps After Setup

### 1. Create Virtual Environment

```bash
cd psi4-mcp-server
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Install Psi4

```bash
# Using conda (recommended)
conda create -n psi4-mcp python=3.10
conda activate psi4-mcp
conda install -c psi4 psi4

# Set environment variable
export PSI_SCRATCH=/tmp/psi4_scratch
mkdir -p $PSI_SCRATCH
```

### 3. Install MCP and Dependencies

```bash
pip install mcp[cli] fastmcp ase numpy pydantic pytest pytest-asyncio
```

### 4. Start Implementation

Follow the comprehensive plan:
- **Week 1:** Phase 0 - Foundation (see `../psi4_mcp_comprehensive_plan.md`)
- **Week 2:** Phase 1 - Core Infrastructure
- **Weeks 3-4:** Phase 2 - Core Calculation Tools
- And so on...

---

## 📚 Planning Documents Reference

All planning documents are in the parent directory (`../`):

| Document | Purpose |
|----------|---------|
| `psi4_mcp_executive_summary.md` | Quick start, 13-week timeline |
| `psi4_mcp_comprehensive_plan.md` | Complete implementation plan (2281 lines) |
| `psi4_mcp_architecture.md` | System architecture & data flows |
| `psi4_mcp_technical_spec.md` | Technical specifications & models |
| `psi4_mcp_checklist.md` | Line-by-line implementation checklist |
| `psi4_mcp_complete_tree.txt` | Complete file/folder structure |
| `psi4_mcp_tree_statistics.md` | Structure statistics & breakdown |

---

## 🔍 Alignment with Complete Tree

The script creates **exactly** the structure defined in `psi4_mcp_complete_tree.txt`:

✅ All 17 tool categories  
✅ All 14 utility categories  
✅ All model subdirectories  
✅ All test directories  
✅ All documentation directories  
✅ All example directories  
✅ All data directories  
✅ All deployment configurations  

---

## 🛠️ Troubleshooting

### Issue: "Permission denied"
```bash
chmod +x setup_structure.sh
```

### Issue: "Directory already exists"
- The script will prompt you to continue
- Choose 'y' to add/update files
- Choose 'n' to cancel

### Issue: Script fails partway through
- The script uses `set -e` to exit on error
- Check the error message
- Fix the issue and re-run (safe to re-run)

---

## 📝 Notes

1. **Git Integration:** The created structure is part of your existing DFT_visual repository
2. **No Conflicts:** The script doesn't modify any existing files in the parent directories
3. **Idempotent:** Safe to run multiple times (will skip existing directories)
4. **Complete:** Encompasses the entire implementation plan from all planning documents

---

**Ready to build! 🚀**

