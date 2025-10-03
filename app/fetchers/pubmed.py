import os
from typing import List

from langchain_community.utilities.pubmed import PubMedAPIWrapper

from app.fetchers.fetcher import Fetcher, TOP_K_RESULTS, MAX_CHARACTERS


class PubMedFetcher(Fetcher):
    """
    Fetcher around LangChain's PubMedAPIWrapper to fetch medical literature.
    """
    def __init__(self):
        self.wrapper = PubMedAPIWrapper(top_k_results=TOP_K_RESULTS, load_max_docs=TOP_K_RESULTS,
                                        email=os.getenv("PUBMED_EMAIL"),
                                        api_key=os.getenv("PUBMED_API_KEY")
                                        )
        self.max_chars = MAX_CHARACTERS

    def search(self, query: str) -> List[str]:
        """
        Returns a list of string snippets from PubMed relevant to the query.
        """
        docs = self.wrapper.load(query)
        print(f"Documents found: {len(docs)}")
        results: List[str] = []
        for doc in docs:
            content = (doc['Summary'] or "").strip()
            if not content:
                continue
            if len(content) > self.max_chars:
                content = content[: self.max_chars] + "..."
            results.append(content)
        return results
