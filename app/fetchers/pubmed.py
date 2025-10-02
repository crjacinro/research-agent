from typing import List

from langchain_community.utilities.pubmed import PubMedAPIWrapper

from Bio import Entrez
Entrez.email = "you@example.com"
Entrez.api_key = "0521afc7bb7c9e3baffcb3e5f21f7c4ca00a"  # optional

class PubMedFetcher:
    """
    Thin wrapper around LangChain's PubMedAPIWrapper to fetch medical literature.
    """

    def __init__(self, top_k_results: int = 5, max_chars: int = 5000):
        self.wrapper = PubMedAPIWrapper(top_k_results=top_k_results, load_max_docs=top_k_results, email="villasica.serge@gmail.com", api_key="0521afc7bb7c9e3baffcb3e5f21f7c4ca00a")
        self.max_chars = max_chars

    def search(self, query: str) -> List[str]:
        """
        Returns a list of string snippets from PubMed relevant to the query.
        """
        docs = self.wrapper.load(query)
        results: List[str] = []
        for doc in docs:
            content = (doc.page_content or "").strip()
            if not content:
                continue
            if len(content) > self.max_chars:
                content = content[: self.max_chars] + "..."
            results.append(content)
        return results







