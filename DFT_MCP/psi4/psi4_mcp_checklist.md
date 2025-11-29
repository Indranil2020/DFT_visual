# Psi4 MCP Server - Quick Reference Checklist

## **CRITICAL: DO NOT SKIP ANY ITEMS**

This checklist accompanies the comprehensive plan. Check off each item as completed.

---

## **Pre-Implementation (Week 1)**

### Environment Setup
- [ ] Python 3.10+ installed
- [ ] Psi4 installed via conda or pip
- [ ] Psi4 import test successful
- [ ] PSI_SCRATCH environment variable set
- [ ] MCP SDK installed: `pip install mcp[cli]`
- [ ] FastMCP installed: `pip install fastmcp`
- [ ] ASE installed: `pip install ase`
- [ ] All dependencies installed and tested
- [ ] Virtual environment created and activated

### Research Completed
- [ ] Psi4 PsiAPI documentation read and summarized
- [ ] Psi4 methods catalog created
- [ ] ASE Calculator interface understood
- [ ] MCP protocol specification reviewed
- [ ] Existing MCP servers analyzed (VASPilot, AiiDA, GPAW)
- [ ] Best practices document created
- [ ] Test cases identified from Psi4 test suite

### Architecture Defined
- [ ] Project structure created
- [ ] All Pydantic models defined
- [ ] Tool specifications documented
- [ ] Error handling framework designed
- [ ] Architecture review completed

---

## **Phase 1: Core Infrastructure (Week 2)**

### Server Initialization
- [ ] FastMCP server initialized
- [ ] Psi4 properly configured
- [ ] Logging configured (STDERR only!)
- [ ] Environment variables handled
- [ ] Server runs without errors

### Input Validation System
- [ ] Geometry validator implemented
- [ ] Basis set validator implemented
- [ ] Method validator implemented
- [ ] Memory validator implemented
- [ ] Options validator implemented
- [ ] All validators have unit tests
- [ ] Clear error messages for all validation failures

### Output Parser System
- [ ] Energy output parser implemented
- [ ] Optimization output parser implemented
- [ ] Frequency output parser implemented
- [ ] Properties output parser implemented
- [ ] TDDFT output parser implemented
- [ ] All parsers have unit tests

---

## **Phase 2: Core Calculation Tools (Weeks 3-4)**

### Energy Calculation Tool
- [ ] Basic energy calculation works
- [ ] HF method supported
- [ ] DFT methods supported (B3LYP, PBE, etc.)
- [ ] MP2 supported
- [ ] Coupled cluster supported
- [ ] Progress reporting implemented
- [ ] Error handling implemented
- [ ] All reference types work (RHF, UHF, ROHF)
- [ ] Options handling implemented
- [ ] Unit tests pass
- [ ] Examples documented

### Geometry Optimization Tool
- [ ] Basic optimization works
- [ ] Progress callbacks implemented
- [ ] Convergence criteria configurable
- [ ] Multiple coordinate systems supported
- [ ] Constrained optimization works
- [ ] Transition state search works
- [ ] Handles non-convergence gracefully
- [ ] Trajectory extraction works
- [ ] Unit tests pass
- [ ] Examples documented

### Frequency Calculation Tool
- [ ] Frequencies calculated correctly
- [ ] Thermodynamic properties computed
- [ ] IR intensities extracted
- [ ] Raman activities (if applicable)
- [ ] Stationary point classification works
- [ ] Normal mode data available
- [ ] Unit tests pass
- [ ] Examples documented

### Properties Tool
- [ ] Dipole moment calculation works
- [ ] Quadrupole moment works
- [ ] Polarizability works
- [ ] HOMO-LUMO gap extraction works
- [ ] Mulliken charges work
- [ ] ESP charges work
- [ ] Bond orders work
- [ ] Unit tests pass
- [ ] Examples documented

---

## **Phase 3: Advanced Tools (Weeks 5-6)**

### TDDFT Tool
- [ ] Ground state DFT works
- [ ] TDDFT calculation works
- [ ] Singlet states calculated
- [ ] Triplet states calculated
- [ ] TDA option works
- [ ] Oscillator strengths extracted
- [ ] Transition dipoles extracted
- [ ] UV-Vis spectrum generated
- [ ] Unit tests pass
- [ ] Examples documented

### SAPT Tool
- [ ] SAPT0 works
- [ ] SAPT2 works
- [ ] SAPT2+ works
- [ ] Dimer input format handled
- [ ] Energy components extracted correctly
- [ ] Interpretation helper works
- [ ] Unit tests pass
- [ ] Examples documented

### Coupled Cluster Tool
- [ ] CCSD works
- [ ] CCSD(T) works
- [ ] Large systems handled efficiently
- [ ] Unit tests pass
- [ ] Examples documented

---

## **Phase 4: Resources & Prompts (Week 7)**

### Basis Set Resource
- [ ] List all basis sets
- [ ] Get basis set details
- [ ] Recommendations provided
- [ ] Citations included
- [ ] Tests pass

### Method Resource
- [ ] List all methods
- [ ] Method details provided
- [ ] Complexity information included
- [ ] Recommendations work
- [ ] Tests pass

### Prompt Templates
- [ ] Optimization workflow template
- [ ] Method/basis suggestion template
- [ ] Error recovery template
- [ ] Tests pass

---

## **Phase 5: Error Handling (Week 8)**

### Error Detection
- [ ] All error types defined
- [ ] Pattern matching works
- [ ] Error categorization accurate
- [ ] Fix suggestions helpful
- [ ] Auto-recovery implemented
- [ ] Unit tests cover all error types

### Convergence Recovery
- [ ] SOSCF strategy works
- [ ] Damping strategy works
- [ ] Level shift strategy works
- [ ] SAD guess strategy works
- [ ] Multiple strategies tried automatically
- [ ] Tests validate recovery

---

## **Phase 6: Testing (Weeks 9-10)**

### Unit Tests
- [ ] Energy tool tests (20+ tests)
- [ ] Optimization tool tests (15+ tests)
- [ ] Frequency tool tests (10+ tests)
- [ ] Properties tool tests (15+ tests)
- [ ] TDDFT tool tests (10+ tests)
- [ ] Validation tests (20+ tests)
- [ ] Parser tests (15+ tests)
- [ ] Code coverage >90%
- [ ] All tests pass

### Integration Tests
- [ ] Full optimization workflow test
- [ ] TDDFT workflow test
- [ ] Multi-step workflow test
- [ ] MCP protocol compliance test
- [ ] All integration tests pass

### Validation Tests
- [ ] Water (H2O) - HF validated
- [ ] Water (H2O) - DFT validated
- [ ] Water (H2O) - MP2 validated
- [ ] Methane (CH4) - frequencies validated
- [ ] Ethylene (C2H4) - TDDFT validated
- [ ] Neon dimer - SAPT validated
- [ ] Formaldehyde - properties validated

---

## **Phase 7: Documentation (Week 11)**

### API Documentation
- [ ] Installation guide written
- [ ] Quick start guide written
- [ ] Tool reference complete
- [ ] Resource reference complete
- [ ] Prompt templates documented
- [ ] Error handling guide written
- [ ] Performance optimization guide written
- [ ] FAQ populated
- [ ] Troubleshooting guide complete

### Examples
- [ ] Basic energy example
- [ ] Geometry optimization example
- [ ] Frequency calculation example
- [ ] TDDFT spectrum example
- [ ] SAPT analysis example
- [ ] Advanced workflow example
- [ ] All examples tested and work

---

## **Phase 8: Deployment (Week 12)**

### Performance Optimization
- [ ] Memory management optimized
- [ ] Computation efficiency improved
- [ ] Caching implemented
- [ ] Benchmarks run
- [ ] Performance acceptable

### Deployment Configuration
- [ ] pyproject.toml complete
- [ ] Package builds successfully
- [ ] Docker image builds
- [ ] Docker image tested
- [ ] Installation instructions validated

### CI/CD
- [ ] GitHub Actions configured
- [ ] Tests run automatically
- [ ] Coverage reported
- [ ] Build artifacts created
- [ ] CI/CD pipeline working

---

## **Phase 9: Final Review (Week 13)**

### Security Audit
- [ ] Input sanitization verified
- [ ] Memory limits enforced
- [ ] File system access restricted
- [ ] Process isolation implemented
- [ ] Error messages sanitized
- [ ] Rate limiting configured
- [ ] Audit logging implemented

### Benchmarking
- [ ] Small molecule benchmark complete
- [ ] Medium molecule benchmark complete
- [ ] Large molecule benchmark complete
- [ ] Sequential calculation benchmark complete
- [ ] Memory profiling complete
- [ ] Performance meets requirements

### Documentation Review
- [ ] All tools documented
- [ ] All examples work
- [ ] Installation guide tested
- [ ] Troubleshooting guide complete
- [ ] FAQ reviewed

### Release
- [ ] Version tagged
- [ ] Changelog updated
- [ ] PyPI package published
- [ ] Docker image published
- [ ] GitHub release created
- [ ] Documentation deployed
- [ ] Announcement published

---

## **Quality Gates**

### Must Pass Before Moving to Next Phase:
- [ ] All previous phase items checked
- [ ] All tests in current phase pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No critical bugs

---

## **Critical Reminders**

### ⚠️ STDIO Transport Rules:
- **NEVER** use `print()` statements
- **ALWAYS** log to `stderr`
- **NEVER** write to `stdout` except JSON-RPC messages

### ⚠️ Psi4 Specific:
- **ALWAYS** set PSI_SCRATCH before calculations
- **ALWAYS** configure memory before large calculations
- **ALWAYS** clean up after calculations
- **ALWAYS** handle convergence failures

### ⚠️ MCP Protocol:
- **ALWAYS** validate input with Pydantic
- **ALWAYS** report progress for long operations
- **ALWAYS** provide clear error messages
- **ALWAYS** use proper tool descriptions

### ⚠️ Testing:
- **ALWAYS** test with real Psi4 calculations
- **ALWAYS** validate against known reference values
- **ALWAYS** test error handling paths
- **ALWAYS** test edge cases

---

## **Sign-Off Sheet**

| Phase | Completed | Date | Reviewer | Notes |
|-------|-----------|------|----------|-------|
| 0: Foundation | [ ] | ___ | ___ | |
| 1: Infrastructure | [ ] | ___ | ___ | |
| 2: Core Tools | [ ] | ___ | ___ | |
| 3: Advanced Tools | [ ] | ___ | ___ | |
| 4: Resources | [ ] | ___ | ___ | |
| 5: Error Handling | [ ] | ___ | ___ | |
| 6: Testing | [ ] | ___ | ___ | |
| 7: Documentation | [ ] | ___ | ___ | |
| 8: Deployment | [ ] | ___ | ___ | |
| 9: Final Review | [ ] | ___ | ___ | |

---

## **Emergency Contacts & Resources**

### Documentation:
- Psi4 Manual: https://psicode.org/psi4manual/master/
- MCP Specification: https://modelcontextprotocol.io/
- ASE Documentation: https://wiki.fysik.dtu.dk/ase/

### Support:
- Psi4 Forum: https://forum.psicode.org/
- MCP GitHub: https://github.com/modelcontextprotocol/

### Reference Implementations:
- VASPilot: (See project documents)
- AiiDA MCP: https://github.com/khsrali/aiida-mcp
- GPAW MCP: https://github.com/pathintegral-institute/mcp.science

---

**IMPORTANT:** This checklist should be used in conjunction with the comprehensive plan. Every item must be completed before the project is considered done.

**Last Updated:** 2025-11-27  
**Version:** 1.0
