# Prompts package — each agent imports its own prompt from here
# Usage example inside an agent:
#   from prompts.security import SECURITY_SYSTEM_PROMPT

from prompts.security import SECURITY_SYSTEM_PROMPT
from prompts.performance import PERFORMANCE_SYSTEM_PROMPT
from prompts.style import STYLE_SYSTEM_PROMPT
from prompts.architecture import ARCHITECTURE_SYSTEM_PROMPT
from prompts.test import TEST_SYSTEM_PROMPT
from prompts.compliance import COMPLIANCE_SYSTEM_PROMPT

__all__ = [
    "SECURITY_SYSTEM_PROMPT",
    "PERFORMANCE_SYSTEM_PROMPT",
    "STYLE_SYSTEM_PROMPT",
    "ARCHITECTURE_SYSTEM_PROMPT",
    "TEST_SYSTEM_PROMPT",
    "COMPLIANCE_SYSTEM_PROMPT",
]
