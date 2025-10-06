from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate

from app.fetchers import Fetcher
from app.fetchers.arxiv import ArxivFetcher
from app.fetchers.pubmed import PubMedFetcher
from app.fetchers.wikipedia import WikipediaFetcher
from app.fetchers.duckduckgo import DuckDuckGoFetcher
from app.utils.llm import get_openai_llm
from app.workflows.research_type import ResearchType
from app.workflows.research_state import ResearchState
from app.models.results import QueryResult, FetcherResult


def _classify_domain(state: ResearchState) -> ResearchState:
    llm = get_openai_llm()

    system_prompt = (f"You are a classifier that outputs exactly one word: "
                     f"{ResearchType.MEDICAL.name},  {ResearchType.ACADEMIC.name},  {ResearchType.KNOWLEDGE.name}, or  {ResearchType.WEB.name}.")
    query_prompt = ("Query: {query}\n"
                  "Classify the domain of the query above. "
                  f"If medical, clinical, health or biological → '{ResearchType.MEDICAL.name}'. "
                  f"If encyclopedic, factual, trivial, or general knowledge → '{ResearchType.KNOWLEDGE.name}'. "
                  f"If academic, research papers, scientific → '{ResearchType.ACADEMIC.name}'. "
                  f"If travel/hotels/flights, current events/news, sports, or general web info → '{ResearchType.WEB.name}'. "
                  f"Else → '{ResearchType.WEB.name}'.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", ("%s" % query_prompt))
    ])
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]})

    domain: ResearchType = ResearchType[response.content.strip().upper()]
    state["domain"] = domain
    print(f"Domain identified: {domain}")
    return state

def _identify_medical_terms(state: ResearchState) -> ResearchState:
    llm = get_openai_llm()
    system_prompt = (f"You are an expert in health and medical field. Identify the important medical terms in the query that would still capture the idea of the query. "
                     f"Use a maximum of 5 terms, separated by commas")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", ("%s" % "Query: {query}"))
    ])
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]})

    terms = response.content.strip()
    state["terms"] = terms
    print(f"Medical terms identified: {terms}")
    return state

def _retrieve_fetcher(domain: ResearchType) -> Fetcher:
    if domain == ResearchType.MEDICAL:
        return PubMedFetcher()
    elif domain == ResearchType.KNOWLEDGE:
        return WikipediaFetcher()
    elif domain == ResearchType.ACADEMIC:
        return ArxivFetcher()
    else:
        return DuckDuckGoFetcher()

def _route_after_classify(state: ResearchState) -> str:
    if state["domain"] == ResearchType.MEDICAL:
        return "identify"
    else:
        return "retrieve"

def _retrieve_sources(state: ResearchState) -> ResearchState:
    print(f"Retrieving sources for query...")
    query = state["query"]
    terms = state.get("terms", "")  # Use empty string if terms not set
    domain = state.get("domain")

    fetcher = _retrieve_fetcher(domain)
    fetcher_result: FetcherResult = fetcher.search(query, terms)

    # Check if medical domain returned empty results and fallback to web search
    if domain != ResearchType.WEB and (not fetcher_result.raw_sources or not fetcher_result.documents):
        print(f"PubMed returned empty results, falling back to web search...")
        web_fetcher = DuckDuckGoFetcher()
        fallback_result: FetcherResult = web_fetcher.search(query, terms)
        state["sources"] = fallback_result.raw_sources
        state["documents"] = fallback_result.documents
        state["domain"] = ResearchType.WEB
    else:
        state["sources"] = fetcher_result.raw_sources
        state["documents"] = fetcher_result.documents

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
    graph.add_node("identify", _identify_medical_terms)
    graph.add_node("retrieve", _retrieve_sources)
    graph.add_node("synthesize", _synthesize_answer)

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        _route_after_classify, {
            "identify": "identify",
            "retrieve": "retrieve"
        }
    )
    graph.add_edge("identify", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()

def process_query(query: str) -> QueryResult:
    graph = _build_research_graph()
    final_state = graph.invoke({"query": query, "domain": ResearchType.WEB})
    answer = final_state.get("answer")
    domain = final_state.get("domain").name.lower()
    documents = final_state.get("documents", [])

    return QueryResult(
        agent_response=answer,
        domain=domain,
        documents=documents
    )
