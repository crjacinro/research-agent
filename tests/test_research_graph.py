import pytest
from unittest.mock import Mock, patch

from app.workflows.research_graph import (
    _retrieve_fetcher,
    _retrieve_sources,
    _build_research_graph,
    process_query
)
from app.workflows.research_type import ResearchType
from app.workflows.research_state import ResearchState


class TestRetrieveFetcher:
    @patch('app.workflows.research_graph.PubMedFetcher')
    def test_retrieve_fetcher_medical(self, mock_pubmed_fetcher):
        mock_fetcher = Mock()
        mock_pubmed_fetcher.return_value = mock_fetcher
        
        result = _retrieve_fetcher(ResearchType.MEDICAL)
        
        assert result == mock_fetcher
        mock_pubmed_fetcher.assert_called_once()

    @patch('app.workflows.research_graph.WikipediaFetcher')
    def test_retrieve_fetcher_knowledge(self, mock_wikipedia_fetcher):
        mock_fetcher = Mock()
        mock_wikipedia_fetcher.return_value = mock_fetcher
        
        result = _retrieve_fetcher(ResearchType.KNOWLEDGE)
        
        assert result == mock_fetcher
        mock_wikipedia_fetcher.assert_called_once()

    @patch('app.workflows.research_graph.ArxivFetcher')
    def test_retrieve_fetcher_academic(self, mock_arxiv_fetcher):
        mock_fetcher = Mock()
        mock_arxiv_fetcher.return_value = mock_fetcher
        
        result = _retrieve_fetcher(ResearchType.ACADEMIC)
        
        assert result == mock_fetcher
        mock_arxiv_fetcher.assert_called_once()

    @patch('app.workflows.research_graph.DuckDuckGoFetcher')
    def test_retrieve_fetcher_web(self, mock_duckduckgo_fetcher):
        mock_fetcher = Mock()
        mock_duckduckgo_fetcher.return_value = mock_fetcher
        
        result = _retrieve_fetcher(ResearchType.WEB)
        
        assert result == mock_fetcher
        mock_duckduckgo_fetcher.assert_called_once()


class TestRetrieveSources:
    @patch('app.workflows.research_graph._retrieve_fetcher')
    def test_retrieve_sources_success(self, mock_retrieve_fetcher):
        mock_fetcher = Mock()
        mock_fetcher.search.return_value = (["Source 1", "Source 2", "Source 3"], ["doc1.pdf", "doc2.pdf", "doc3.pdf"])
        mock_retrieve_fetcher.return_value = mock_fetcher
        
        state = ResearchState(
            query="Test query",
            domain=ResearchType.MEDICAL,
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        assert result["sources"] == ["Source 1", "Source 2", "Source 3"]
        assert result["documents"] == ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        assert result["query"] == "Test query"
        assert result["domain"] == ResearchType.MEDICAL
        mock_retrieve_fetcher.assert_called_once_with(ResearchType.MEDICAL)
        mock_fetcher.search.assert_called_once_with("Test query")

    @patch('app.workflows.research_graph._retrieve_fetcher')
    def test_retrieve_sources_empty_results(self, mock_retrieve_fetcher):
        mock_fetcher = Mock()
        mock_fetcher.search.return_value = ([], [])
        mock_retrieve_fetcher.return_value = mock_fetcher
        
        state = ResearchState(
            query="Test query",
            domain=ResearchType.WEB,
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        assert result["sources"] == []
        assert result["documents"] == []
        mock_fetcher.search.assert_called_once_with("Test query")

class TestProcessQuery:
    @patch('app.workflows.research_graph._build_research_graph')
    def test_process_query_success(self, mock_build_graph):
        mock_graph = Mock()
        mock_final_state = {
            "query": "What is machine learning?",
            "domain": ResearchType.ACADEMIC,
            "sources": ["Source 1", "Source 2"],
            "documents": ["doc1.pdf", "doc2.pdf"],
            "answer": "Machine learning is a subset of AI..."
        }
        mock_graph.invoke.return_value = mock_final_state
        mock_build_graph.return_value = mock_graph
        
        query = "What is machine learning?"
        
        answer, domain, documents = process_query(query)
        
        assert answer == "Machine learning is a subset of AI..."
        assert domain == "academic"
        assert documents == ["doc1.pdf", "doc2.pdf"]
        mock_build_graph.assert_called_once()
        mock_graph.invoke.assert_called_once_with({"query": query})

class TestResearchGraphIntegration:
    def test_research_graph_workflow_structure(self):
        graph = _build_research_graph()
        
        assert graph is not None
        assert hasattr(graph, 'invoke')
        
        try:
            assert callable(graph.invoke)
        except Exception as e:
            pytest.fail(f"Graph structure test failed: {e}")

    def test_research_state_typing(self):
        state = ResearchState(
            query="Test query",
            domain=ResearchType.MEDICAL,
            sources=["Source 1", "Source 2"],
            documents=["doc1.pdf", "doc2.pdf"],
            answer="Test answer"
        )
        
        assert state["query"] == "Test query"
        assert state["domain"] == ResearchType.MEDICAL
        assert state["sources"] == ["Source 1", "Source 2"]
        assert state["documents"] == ["doc1.pdf", "doc2.pdf"]
        assert state["answer"] == "Test answer"

    def test_research_state_partial(self):
        state = ResearchState(query="Test query")
        
        assert state["query"] == "Test query"
        assert state.get("domain") is None or isinstance(state.get("domain"), ResearchType)
        assert state.get("sources") is None or isinstance(state.get("sources"), list)
        assert state.get("documents") is None or isinstance(state.get("documents"), list)
        assert state.get("answer") is None or isinstance(state.get("answer"), str)

    def test_research_type_enum_values(self):
        assert hasattr(ResearchType, 'MEDICAL')
        assert hasattr(ResearchType, 'ACADEMIC')
        assert hasattr(ResearchType, 'KNOWLEDGE')
        assert hasattr(ResearchType, 'WEB')
        
        assert ResearchType.MEDICAL.name == "MEDICAL"
        assert ResearchType.ACADEMIC.name == "ACADEMIC"
        assert ResearchType.KNOWLEDGE.name == "KNOWLEDGE"
        assert ResearchType.WEB.name == "WEB"

    def test_fetcher_retrieval_logic(self):
        with patch('app.workflows.research_graph.PubMedFetcher') as mock_pubmed:
            mock_pubmed.return_value = Mock()
            result = _retrieve_fetcher(ResearchType.MEDICAL)
            mock_pubmed.assert_called_once()
            assert result is not None

        with patch('app.workflows.research_graph.WikipediaFetcher') as mock_wikipedia:
            mock_wikipedia.return_value = Mock()
            result = _retrieve_fetcher(ResearchType.KNOWLEDGE)
            mock_wikipedia.assert_called_once()
            assert result is not None

        with patch('app.workflows.research_graph.ArxivFetcher') as mock_arxiv:
            mock_arxiv.return_value = Mock()
            result = _retrieve_fetcher(ResearchType.ACADEMIC)
            mock_arxiv.assert_called_once()
            assert result is not None

        with patch('app.workflows.research_graph.DuckDuckGoFetcher') as mock_duckduckgo:
            mock_duckduckgo.return_value = Mock()
            result = _retrieve_fetcher(ResearchType.WEB)
            mock_duckduckgo.assert_called_once()
            assert result is not None