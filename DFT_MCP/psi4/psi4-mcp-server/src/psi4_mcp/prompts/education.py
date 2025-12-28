"""Educational Prompts."""
from typing import Dict, Any, List, ClassVar
from mcp.types import GetPromptResult, PromptMessage, PromptArgument
from psi4_mcp.prompts.base_prompt import BasePrompt, register_prompt

@register_prompt
class MethodSelectionPrompt(BasePrompt):
    name = "method_selection"
    description = "Help select methods"
    arguments = [PromptArgument(name="task", description="Task type", required=True)]
    
    def render(self, args: Dict[str, Any]) -> GetPromptResult:
        task = args.get("task", "energy")
        text = f"# Method Selection for {task}\n- Quick: B3LYP/def2-SVP\n- Balanced: B3LYP/def2-TZVP\n- Accurate: CCSD(T)/cc-pVTZ"
        return GetPromptResult(description=f"Methods for {task}",
                              messages=[PromptMessage(role="user", content={"type": "text", "text": text})])

@register_prompt
class TroubleshootingPrompt(BasePrompt):
    name = "troubleshooting"
    description = "Troubleshoot errors"
    arguments = [PromptArgument(name="error", description="Error type", required=True)]
    
    def render(self, args: Dict[str, Any]) -> GetPromptResult:
        err = args.get("error", "convergence")
        text = f"# Troubleshooting {err}\n- Check geometry\n- Try SOSCF\n- Increase damping"
        return GetPromptResult(description=f"Fix {err}",
                              messages=[PromptMessage(role="user", content={"type": "text", "text": text})])
