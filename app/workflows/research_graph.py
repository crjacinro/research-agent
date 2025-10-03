from typing import Literal

from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate

from app.fetchers.arxiv import ArxivFetcher
from app.fetchers.pubmed import PubMedFetcher
from app.fetchers.wikipedia import WikipediaFetcher
from app.utils.llm import get_openai_llm
from app.workflows.research_state import ResearchState

def _classify_domain(state: ResearchState) -> ResearchState:
    print(f"Classifying domain for query...")
    llm = get_openai_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a classifier that outputs exactly one word: medical, research, or wikipedia."),
        ("user", "Query: {query}\nIf the query above is about medical/clinical/health → 'medical'. If about general factual knowledge (definitions, dates, places, encyclopedic) → 'wikipedia'. Else → 'research'.")
    ])
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]})
    text = response.content.strip().lower()
    domain: Literal["medical", "research", "wikipedia"]
    if "medical" in text:
        domain = "medical"
    elif "wikipedia" in text:
        domain = "wikipedia"
    else:
        domain = "research"
    state["domain"] = domain
    print(f"Domain identified: {domain}")
    return state


def _retrieve_sources(state: ResearchState) -> ResearchState:
    print(f"Retrieving sources for query...")
    query = state["query"]
    domain = state.get("domain") or "research"
    if domain == "medical":
        fetcher = PubMedFetcher()
        sources = fetcher.search(query)
        state["domain"] = "PubMed"
    elif domain == "wikipedia":
        fetcher = WikipediaFetcher()
        sources = fetcher.search(query)
        state["domain"] = "Wikipedia"
    else:
        fetcher = ArxivFetcher()
        sources = fetcher.search(query)
        state["domain"] = "Arxiv"
    state["sources"] = sources
    print(f"Sources identified: {sources}")
    return state


def _synthesize_answer(state: ResearchState) -> ResearchState:
    llm = get_openai_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert research assistant. Synthesize a helpful, well-cited, concise answer using the provided sources. Cite inline with [n]."),
        ("user", "Query: {query}\n\nSources:\n{sources}\n\nInstructions: Provide a factual, neutral, safety-conscious answer suitable for general audiences.")
    ])
    sources_text = "\n\n".join(f"[{i+1}] {s}" for i, s in enumerate(state.get("sources", []))) or "No sources found"
    chain = prompt | llm
    response = chain.invoke({"query": state["query"], "sources": sources_text})
    state["answer"] = response.content
    return state


def _build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("classify", _classify_domain)
    graph.add_node("retrieve", _retrieve_sources)
    graph.add_node("synthesize", _synthesize_answer)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()

def process_query(query: str) -> (str, str) :
    graph = _build_research_graph()
    final_state = graph.invoke({"query": query})
    answer = final_state.get("answer")
    domain = final_state.get("domain")

    return answer, domain


