from typing import List

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from app.fetchers import Fetcher, TOP_K_RESULTS, MAX_CHARACTERS


class DuckDuckGoFetcher(Fetcher):
    """
    Fetcher around LangChain's DuckDuckGoSearchAPIWrapper for general web information
    such as travel, hotels, news, and sports.
    """

    def __init__(self):
        self.wrapper = DuckDuckGoSearchAPIWrapper()
        self.max_chars = MAX_CHARACTERS
        self.top_k = TOP_K_RESULTS

    def search(self, query: str) -> (List[str], List[str]):
        results_raw = self.wrapper.results(query, max_results=self.top_k)
        results: List[str] = []
        documents: List[str] = []
        for item in results_raw:
            title = (item.get("title") or "").strip()
            snippet = (item.get("snippet") or item.get("body") or "").strip()
            link = (item.get("link") or "").strip()
            content = " - ".join(filter(None, [title, snippet]))
            if link:
                content = f"{content} ({link})" if content else link
            if not content:
                continue
            if len(content) > self.max_chars:
                content = content[: self.max_chars] + "..."
            results.append(content)
            documents.append(link or "Unknown source")
        print(f"DuckDuckGoFetcher found {len(documents)} summaries: {documents}")
        return results, documents
