from typing import TypedDict, Optional, List, Literal

from app.workflows.research_type import ResearchType


class ResearchState(TypedDict):
    query: str
    domain: ResearchType = ResearchType.WEB
    sources: List[str]
    answer: Optional[str]