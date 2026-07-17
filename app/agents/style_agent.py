from app.agents.base_agent import BaseAgent
from app.agents.prompts import STYLE_AGENT_PROMPT
from app.models.finding import AgentReviewResult

class StyleAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="StyleAgent",
            system_prompt=STYLE_AGENT_PROMPT
        )

def run_style_agent(state: dict) -> dict:
    agent = StyleAgent()
    result: AgentReviewResult = agent.analyze(state["diff_text"])
    return {"findings": result.findings}
