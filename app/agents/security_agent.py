from app.agents.base_agent import BaseAgent
from app.agents.prompts import SECURITY_AGENT_PROMPT
from app.models.finding import AgentReviewResult

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="SecurityAgent",
            system_prompt=SECURITY_AGENT_PROMPT
        )

# A simple wrapper function used by LangGraph to call this agent
def run_security_agent(state: dict) -> dict:
    agent = SecurityAgent()
    result: AgentReviewResult = agent.analyze(state["diff_text"])
    # LangGraph will automatically combine this list with lists returned by other parallel nodes
    return {"findings": result.findings}
