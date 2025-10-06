from dataclasses import dataclass
from typing import List

@dataclass
class QueryResult:
    """Result of a research query containing the agent response, source, and documents."""
    agent_response: str
    domain: str
    documents: List[str]

@dataclass
class FetcherResult:
    """Result of a fetcher search containing the results and documents."""
    raw_sources: List[str]
    documents: List[str]