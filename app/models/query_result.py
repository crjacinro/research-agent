from dataclasses import dataclass
from typing import List

@dataclass
class QueryResult:
    """Result of a research query containing the agent response, source, and documents."""
    agent_response: str
    source: str
    documents: List[str]
