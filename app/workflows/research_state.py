from typing import TypedDict, Optional, List, Literal

from app.workflows.research_type import ResearchType


class ResearchState(TypedDict):
    query: str
    domain: ResearchType
    sources: List[str]
    documents: List[str]
    terms: str
    answer: Optional[str]