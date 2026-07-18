from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.models.finding import Finding
import structlog

logger = structlog.get_logger()

class QualityScore(BaseModel):
    confidence_score: float = Field(description="A float between 0.0 and 1.0 representing how confident you are that this is a true positive finding.")
    reason: str = Field(description="A short explanation of why you gave this score.")

class QualityEvaluator:
    """
    Acts as a Senior Staff Engineer.
    Reviews the findings produced by the agents to filter out hallucinations and false positives.
    """
    def __init__(self):
        # We use the most capable model for the judge
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.0
        )
        self.structured_llm = self.llm.with_structured_output(QualityScore)
        
        self.system_prompt = (
            "You are a Senior Staff Engineer evaluating an AI Code Review Agent's finding.\n"
            "Your job is to catch 'false positives' (hallucinations, incorrect assumptions, or overly pedantic complaints).\n"
            "You must return a confidence score between 0.0 (definitely wrong/false positive) and 1.0 (absolutely correct).\n\n"
            "Criteria for high score:\n"
            "- The issue actually exists in the provided code diff.\n"
            "- The suggested fix is syntactically valid and solves the problem.\n"
            "- The finding is not a hallucination about code that doesn't exist.\n"
        )

    def evaluate_finding(self, diff_text: str, finding: Finding) -> QualityScore:
        """
        Grades a finding based on the original diff.
        """
        prompt = (
            f"Here is the raw git diff:\n{diff_text}\n\n"
            f"The Agent reported the following finding:\n"
            f"Title: {finding.title}\n"
            f"Description: {finding.description}\n"
            f"Suggestion: {finding.suggestion}\n\n"
            f"Grade this finding."
        )
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            score: QualityScore = self.structured_llm.invoke(messages)
            logger.info("finding_evaluated", title=finding.title, score=score.confidence_score, reason=score.reason)
            return score
            
        except Exception as e:
            logger.error("quality_evaluation_failed", error=str(e))
            # If the judge fails, default to passing it through to avoid blocking the pipeline completely
            return QualityScore(confidence_score=1.0, reason="Evaluation failed, defaulting to pass.")
