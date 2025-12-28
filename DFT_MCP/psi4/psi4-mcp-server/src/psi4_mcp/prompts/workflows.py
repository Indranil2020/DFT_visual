"""Workflow Prompts."""
from typing import Dict, Any, List, ClassVar
from mcp.types import GetPromptResult, PromptMessage, PromptArgument
from psi4_mcp.prompts.base_prompt import BasePrompt, register_prompt

@register_prompt
class OptimizationWorkflowPrompt(BasePrompt):
    name = "optimization_workflow"
    description = "Geometry optimization workflow"
    arguments = [PromptArgument(name="molecule", description="Molecule", required=True)]
    
    def render(self, args: Dict[str, Any]) -> GetPromptResult:
        mol = args.get("molecule", "molecule")
        text = f"# Optimization Workflow for {mol}\n1. Optimize geometry\n2. Calculate frequencies\n3. Verify minimum"
        return GetPromptResult(description=f"Workflow for {mol}", 
                              messages=[PromptMessage(role="user", content={"type": "text", "text": text})])

@register_prompt
class ThermochemistryPrompt(BasePrompt):
    name = "thermochemistry"
    description = "Thermochemistry calculation"
    arguments = [PromptArgument(name="molecule", description="Molecule", required=True)]
    
    def render(self, args: Dict[str, Any]) -> GetPromptResult:
        mol = args.get("molecule", "molecule")
        text = f"# Thermochemistry for {mol}\n1. Optimize\n2. Frequencies\n3. Extract H, S, G"
        return GetPromptResult(description=f"Thermo for {mol}",
                              messages=[PromptMessage(role="user", content={"type": "text", "text": text})])
