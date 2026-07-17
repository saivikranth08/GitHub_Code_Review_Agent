from app.agents.base_agent import BaseAgent
from app.agents.prompts import PERFORMANCE_AGENT_PROMPT
from app.models.finding import AgentReviewResult

class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="PerformanceAgent",
            system_prompt=PERFORMANCE_AGENT_PROMPT
        )

def run_performance_agent(state: dict) -> dict:
    agent = PerformanceAgent()
    result: AgentReviewResult = agent.analyze(state["diff_text"])
    return {"findings": result.findings}
