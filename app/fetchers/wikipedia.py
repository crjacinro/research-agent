from typing import List

from langchain_community.utilities import WikipediaAPIWrapper

from app.fetchers import Fetcher, MAX_CHARACTERS, TOP_K_RESULTS
from app.models.results import FetcherResult


class WikipediaFetcher(Fetcher):
    """
    Fetcher around LangChain's WikipediaAPIWrapper for general factual knowledge.
    """

    def __init__(self):
        self.wrapper = WikipediaAPIWrapper(top_k_results=TOP_K_RESULTS, doc_content_chars_max=MAX_CHARACTERS)
        self.max_chars = MAX_CHARACTERS

    def search(self, query: str, terms:str="") -> FetcherResult:
        docs = self.wrapper.load(query)
        results: List[str] = []
        documents: List[str] = []
        for doc in docs:
            content = (getattr(doc, "page_content", "") or "").strip()
            if not content:
                continue
            if len(content) > self.max_chars:
                content = content[: self.max_chars] + "..."
            results.append(content)
            documents.append(doc.metadata["source"] or "Unknown source")
        print(f"WikipediaFetcher found {len(results)} summaries: {documents}")
        return FetcherResult(results, documents)


