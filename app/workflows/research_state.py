from typing import TypedDict, Optional, List, Literal


class ResearchState(TypedDict):
    query: str
    domain: Optional[Literal["medical", "research", "wikipedia", "duckduckgo"]]
    sources: List[str]
    answer: Optional[str]