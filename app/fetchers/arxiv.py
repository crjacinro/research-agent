from typing import List

from langchain_community.utilities import ArxivAPIWrapper

from app.fetchers import Fetcher, MAX_CHARACTERS, TOP_K_RESULTS
from app.models.results import FetcherResult


class ArxivFetcher(Fetcher):
    """
    Fetcher around LangChain's ArxivAPIWrapper to fetch research papers.
    """

    def __init__(self):
        self.wrapper = ArxivAPIWrapper(top_k_results=TOP_K_RESULTS, load_all_available_meta=False)
        self.max_chars = MAX_CHARACTERS

    def search(self, query: str, terms:str="") -> FetcherResult:
        """
        Returns a list of string snippets from arXiv relevant to the query.
        """
        docs = self.wrapper.load(query)
        results: List[str] = []
        documents: List[str] = []
        for doc in docs:
            content = (doc.page_content or "").strip()
            if not content:
                continue
            if len(content) > self.max_chars:
                content = content[: self.max_chars] + "..."
            results.append(content)
            documents.append(doc.metadata["Title"] or "Unknown source")
        print(f"ArxivFetcher found {len(results)} documents: {documents}")
        return FetcherResult(results, documents)
