from typing import List

from langchain_community.utilities import ArxivAPIWrapper


class ArxivFetcher:
    """
    Fetcher around LangChain's ArxivAPIWrapper to fetch research papers.
    """

    def __init__(self, top_k_results: int = 5, max_chars: int = 5000):
        self.wrapper = ArxivAPIWrapper(top_k_results=top_k_results, load_all_available_meta=False)
        self.max_chars = max_chars

    def search(self, query: str) -> List[str]:
        """
        Returns a list of string snippets from arXiv relevant to the query.
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


