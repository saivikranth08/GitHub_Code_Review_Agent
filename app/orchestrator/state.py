from typing import TypedDict, Annotated
import operator
from app.models.finding import Finding

class CodeReviewState(TypedDict):
    """
    The state dictionary that gets passed through the LangGraph.
    """
    pr_number: int
    repo: str
    diff_text: str
    
    # Annotated with operator.add means when parallel agents return lists of findings,
    # LangGraph will automatically combine them into one massive list.
    findings: Annotated[list[Finding], operator.add]
