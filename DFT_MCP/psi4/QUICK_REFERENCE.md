# Psi4 MCP Server - Quick Reference Card

**One-page reference for getting started**

---

## 🚀 Setup Commands (Copy & Paste)

```bash
# 1. Navigate to planning directory
cd /home/niel/git/DFT_visual/DFT_MCP/psi4/

# 2. Run setup script
chmod +x setup_structure.sh
./setup_structure.sh

# 3. Verify structure
chmod +x verify_structure.sh
./verify_structure.sh

# 4. Navigate to project
cd psi4-mcp-server

# 5. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 6. Install Psi4 (using conda)
conda create -n psi4-mcp python=3.10
conda activate psi4-mcp
conda install -c psi4 psi4

# 7. Set environment
export PSI_SCRATCH=/tmp/psi4_scratch
mkdir -p $PSI_SCRATCH

# 8. Install dependencies
pip install mcp[cli] fastmcp ase numpy pydantic pytest pytest-asyncio

# 9. Verify Psi4
python -c "import psi4; print(f'Psi4 version: {psi4.__version__}')"

# 10. Start implementing!
```

---

## 📚 Document Quick Access

| Read This | When You Need |
|-----------|---------------|
| `psi4_mcp_executive_summary.md` | Overview, timeline, Day 1 guide |
| `psi4_mcp_comprehensive_plan.md` | Detailed implementation steps |
| `psi4_mcp_architecture.md` | System design, data flows |
| `psi4_mcp_technical_spec.md` | Pydantic models, API specs |
| `psi4_mcp_checklist.md` | Task-by-task checklist |
| `SETUP_INSTRUCTIONS.md` | Setup script details |

---

## 📂 Key Directories After Setup

```
psi4-mcp-server/
├── src/psi4_mcp/
│   ├── server.py              ← Start here (main entry point)
│   ├── models/                ← Define data structures first
│   ├── tools/core/            ← Implement core tools (Week 3-4)
│   ├── utils/validation/      ← Build validators (Week 2)
│   └── utils/parsing/         ← Build parsers (Week 2)
├── tests/unit/                ← Write tests as you go
└── docs/getting-started/      ← Document as you build
```

---

## ⏱️ 13-Week Timeline

| Weeks | Phase | Focus |
|-------|-------|-------|
| 1 | Phase 0 | Foundation & setup |
| 2 | Phase 1 | Core infrastructure |
| 3-4 | Phase 2 | Core calculation tools |
| 5-6 | Phase 3 | Advanced tools |
| 7 | Phase 4 | Resources & prompts |
| 8 | Phase 5 | Error handling |
| 9-10 | Phase 6-7 | Testing |
| 11 | Phase 8 | Documentation |
| 12 | Phase 9 | Deployment |
| 13 | Phase 10 | Final review & launch |

---

## 🎯 Week 1 Goals (Phase 0)

- [ ] Environment setup complete
- [ ] Project structure created
- [ ] All Pydantic models implemented
- [ ] Basic energy calculation tool working
- [ ] Simple validation working
- [ ] First unit tests passing

---

## 🔧 First File to Create

**`src/psi4_mcp/server.py`** - Basic structure:

```python
from mcp.server.fastmcp import FastMCP
import psi4
import logging
import sys

# Configure logging (MUST use stderr for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Initialize MCP server
mcp = FastMCP("psi4-quantum-chemistry")

# Initialize Psi4
psi4.set_memory('2 GB')
psi4.set_num_threads(4)

@mcp.tool()
async def calculate_energy(
    geometry: str,
    method: str = "hf",
    basis: str = "sto-3g"
):
    """Calculate single-point energy"""
    # Implementation here
    pass

if __name__ == "__main__":
    mcp.run()
```

---

## 📊 Structure Statistics

- **Directories:** 95
- **Files (when complete):** 380+
- **Tool categories:** 17
- **Utility categories:** 14
- **Test files:** 95+
- **Estimated LOC:** ~70,000

---

## ✅ Daily Checklist Template

```markdown
## Day X - [Date]

### Goals
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Completed
- [x] Thing 1
- [x] Thing 2

### Blockers
- None / [describe]

### Tomorrow
- Next task 1
- Next task 2
```

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Psi4 import fails | Check conda environment activated |
| SCF not converging | Use convergence helpers (Week 8) |
| Memory errors | Reduce basis set or use DF methods |
| MCP connection fails | Check logging goes to stderr only |
| Tests failing | Check fixtures and mock data |

---

## 🔗 Essential Links

- **Psi4 Manual:** https://psicode.org/psi4manual/master/
- **MCP Spec:** https://modelcontextprotocol.io/
- **FastMCP:** https://gofastmcp.com/
- **Psi4 Forum:** https://forum.psicode.org/

---

## 💡 Pro Tips

1. **Start small** - Get one tool working perfectly before adding more
2. **Test early** - Write tests as you write code
3. **Use the checklist** - Track progress systematically
4. **Follow the phases** - Don't skip ahead
5. **Document as you go** - Future you will thank you
6. **Ask for help** - Use Psi4 forum and MCP community

---

## 🎓 Learning Path

1. **Day 1:** Read executive summary, run setup
2. **Day 2-3:** Study architecture, understand MCP protocol
3. **Day 4-5:** Implement basic models and server
4. **Week 2:** Build validation and parsing infrastructure
5. **Week 3+:** Implement tools one by one

---

## 📝 Git Workflow

```bash
# This is a subfolder in existing repo
cd /home/niel/git/DFT_visual

# Check status
git status

# Add new files
git add DFT_MCP/psi4/psi4-mcp-server/

# Commit progress
git commit -m "feat: implement energy calculation tool"

# Push to remote
git push origin main
```

---

**Print this page and keep it handy! 📄**

**Last Updated:** 2025-11-27

