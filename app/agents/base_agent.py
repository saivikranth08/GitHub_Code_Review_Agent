from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.models.finding import AgentReviewResult
import structlog

logger = structlog.get_logger()

class BaseAgent:
    """
    Base class for all Review Agents.
    Sets up the Groq LLM and enforces structured JSON output.
    """
    
    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        
        # Initialize Groq via Langchain
        # llama-3.3-70b-versatile is the newest stable Groq model
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.0  # We want deterministic code reviews, not creative writing
        )
        
        # Force the LLM to reply ONLY with data matching the AgentReviewResult Pydantic schema
        self.structured_llm = self.llm.with_structured_output(AgentReviewResult)

    def analyze(self, diff_text: str) -> AgentReviewResult:
        """
        Sends the diff to Groq and returns structured findings.
        """
        logger.info("agent_starting_analysis", agent=self.agent_name)
        
        # 1. Ask Qdrant for Long-Term Memory context
        try:
            from app.memory.qdrant_store import QdrantStore
            qdrant = QdrantStore()
            past_memory_text = qdrant.search_similar_code(diff_text)
        except Exception as e:
            logger.error("qdrant_memory_fetch_failed", error=str(e))
            past_memory_text = ""
            
        # 2. Build the prompt
        final_system_prompt = self.system_prompt
        if past_memory_text:
            final_system_prompt += f"\n\n{past_memory_text}"
        
        messages = [
            SystemMessage(content=final_system_prompt),
            HumanMessage(content=f"Please review the following git diff:\n\n{diff_text}")
        ]
        
        try:
            # The structured_llm automatically parses the JSON back into our Pydantic model!
            result: AgentReviewResult = self.structured_llm.invoke(messages)
            
            # Ensure the agent name is set correctly, just in case the LLM hallucinates a different name
            result.agent_name = self.agent_name
            
            logger.info(
                "agent_completed_analysis", 
                agent=self.agent_name, 
                findings_count=len(result.findings)
            )
            return result
            
        except Exception as e:
            logger.error("agent_analysis_failed", agent=self.agent_name, error=str(e))
            # Return an empty result so the pipeline doesn't crash if one agent fails
            return AgentReviewResult(agent_name=self.agent_name, findings=[])
