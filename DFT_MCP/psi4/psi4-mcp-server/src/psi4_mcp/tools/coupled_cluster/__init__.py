"""
Coupled Cluster Tools Package.

MCP tools for coupled cluster calculations:
    - CCSD (Coupled Cluster Singles and Doubles)
    - CCSD(T) (with perturbative triples - gold standard)
    - CC2 (Approximate CC with singles and doubles)
    - CC3 (Iterative triples)
    - CCSDT (Full iterative triples)
    - Brueckner CC
    - EOM-CCSD variants
    - LR-CCSD (Linear Response)
"""

from psi4_mcp.tools.coupled_cluster.ccsd import (
    CCSDTool,
    calculate_ccsd,
)

from psi4_mcp.tools.coupled_cluster.ccsd_t import (
    CCSD_T_Tool,
    calculate_ccsd_t,
)

from psi4_mcp.tools.coupled_cluster.cc2 import (
    CC2Tool,
    calculate_cc2,
)

from psi4_mcp.tools.coupled_cluster.cc3 import (
    CC3Tool,
    calculate_cc3,
)

from psi4_mcp.tools.coupled_cluster.ccsdt import (
    CCSDTFullTool,
    calculate_ccsdt,
)

from psi4_mcp.tools.coupled_cluster.brueckner import (
    BruecknerCCTool,
    calculate_brueckner_cc,
)

from psi4_mcp.tools.coupled_cluster.eom_ccsd import (
    EOMCCSDTool,
    calculate_eom_ccsd,
)

from psi4_mcp.tools.coupled_cluster.lr_ccsd import (
    LRCCSDTool,
    calculate_lr_ccsd,
)


__all__ = [
    "CCSDTool", "calculate_ccsd",
    "CCSD_T_Tool", "calculate_ccsd_t",
    "CC2Tool", "calculate_cc2",
    "CC3Tool", "calculate_cc3",
    "CCSDTFullTool", "calculate_ccsdt",
    "BruecknerCCTool", "calculate_brueckner_cc",
    "EOMCCSDTool", "calculate_eom_ccsd",
    "LRCCSDTool", "calculate_lr_ccsd",
]
