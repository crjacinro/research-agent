import pytest
from unittest.mock import Mock, patch

from app.workflows.research_graph import (
    _retrieve_fetcher,
    _retrieve_sources,
    _build_research_graph,
    process_query,
    _route_after_classify,
    _identify_medical_terms
)
from app.workflows.research_type import ResearchType
from app.workflows.research_state import ResearchState
from app.models.results import QueryResult, FetcherResult

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
    def test_retrieve_sources_with_terms(self, mock_retrieve_fetcher):
        mock_fetcher = Mock()
        mock_fetcher.search.return_value = FetcherResult(
            raw_sources=["Source 1", "Source 2", "Source 3"],
            documents=["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        )
        mock_retrieve_fetcher.return_value = mock_fetcher
        
        state = ResearchState(
            query="Test query",
            domain=ResearchType.MEDICAL,
            terms="diabetes, insulin, blood sugar",
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        assert result["sources"] == ["Source 1", "Source 2", "Source 3"]
        assert result["documents"] == ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        assert result["query"] == "Test query"
        assert result["domain"] == ResearchType.MEDICAL
        mock_retrieve_fetcher.assert_called_once_with(ResearchType.MEDICAL)
        mock_fetcher.search.assert_called_once_with("Test query", "diabetes, insulin, blood sugar")

    @patch('app.workflows.research_graph._retrieve_fetcher')
    def test_retrieve_sources_empty_results(self, mock_retrieve_fetcher):
        mock_fetcher = Mock()
        mock_fetcher.search.return_value = FetcherResult(
            raw_sources=[],
            documents=[]
        )
        mock_retrieve_fetcher.return_value = mock_fetcher
        
        state = ResearchState(
            query="Test query",
            domain=ResearchType.WEB,
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        assert result["sources"] == []
        assert result["documents"] == []
        mock_fetcher.search.assert_called_once_with("Test query", "")

    @patch('app.workflows.research_graph.DuckDuckGoFetcher')
    @patch('app.workflows.research_graph._retrieve_fetcher')
    def test_retrieve_sources_medical_fallback(self, mock_retrieve_fetcher, mock_duckduckgo_fetcher):
        """Test that medical domain falls back to DuckDuckGo when PubMed returns empty results"""
        # Mock PubMed fetcher returning empty results
        mock_pubmed_fetcher = Mock()
        mock_pubmed_fetcher.search.return_value = FetcherResult(
            raw_sources=[],
            documents=[]
        )
        mock_retrieve_fetcher.return_value = mock_pubmed_fetcher
        
        # Mock DuckDuckGo fetcher returning results
        mock_web_fetcher = Mock()
        mock_web_fetcher.search.return_value = FetcherResult(
            raw_sources=["Web source 1", "Web source 2"],
            documents=["web_doc1.pdf", "web_doc2.pdf"]
        )
        mock_duckduckgo_fetcher.return_value = mock_web_fetcher
        
        state = ResearchState(
            query="Test medical query",
            domain=ResearchType.MEDICAL,
            terms="diabetes, insulin",
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        # Should use fallback results from DuckDuckGo
        assert result["sources"] == ["Web source 1", "Web source 2"]
        assert result["documents"] == ["web_doc1.pdf", "web_doc2.pdf"]
        
        # Verify PubMed was called first
        mock_retrieve_fetcher.assert_called_once_with(ResearchType.MEDICAL)
        mock_pubmed_fetcher.search.assert_called_once_with("Test medical query", "diabetes, insulin")
        
        # Verify DuckDuckGo fallback was called
        mock_duckduckgo_fetcher.assert_called_once()
        mock_web_fetcher.search.assert_called_once_with("Test medical query", "diabetes, insulin")

    @patch('app.workflows.research_graph._retrieve_fetcher')
    def test_retrieve_sources_medical_no_fallback_needed(self, mock_retrieve_fetcher):
        """Test that medical domain doesn't fallback when PubMed returns results"""
        mock_fetcher = Mock()
        mock_fetcher.search.return_value = FetcherResult(
            raw_sources=["Medical source 1", "Medical source 2"],
            documents=["medical_doc1.pdf", "medical_doc2.pdf"]
        )
        mock_retrieve_fetcher.return_value = mock_fetcher
        
        state = ResearchState(
            query="Test medical query",
            domain=ResearchType.MEDICAL,
            terms="diabetes, insulin",
            sources=[]
        )
        
        result = _retrieve_sources(state)
        
        # Should use PubMed results (no fallback)
        assert result["sources"] == ["Medical source 1", "Medical source 2"]
        assert result["documents"] == ["medical_doc1.pdf", "medical_doc2.pdf"]
        mock_fetcher.search.assert_called_once_with("Test medical query", "diabetes, insulin")

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
        
        result = process_query(query)
        
        assert isinstance(result, QueryResult)
        assert result.agent_response == "Machine learning is a subset of AI..."
        assert result.domain == "academic"
        assert result.documents == ["doc1.pdf", "doc2.pdf"]
        mock_build_graph.assert_called_once()
        mock_graph.invoke.assert_called_once_with({"query": query, "domain": ResearchType.WEB})

    @patch('app.workflows.research_graph._build_research_graph')
    def test_process_query_medical_with_terms(self, mock_build_graph):
        mock_graph = Mock()
        mock_final_state = {
            "query": "What are the symptoms of diabetes?",
            "domain": ResearchType.MEDICAL,
            "terms": "diabetes, insulin, blood sugar",
            "sources": ["Medical Source 1", "Medical Source 2"],
            "documents": ["medical_doc1.pdf", "medical_doc2.pdf"],
            "answer": "Diabetes symptoms include increased thirst, frequent urination..."
        }
        mock_graph.invoke.return_value = mock_final_state
        mock_build_graph.return_value = mock_graph
        
        query = "What are the symptoms of diabetes?"
        
        result = process_query(query)
        
        assert isinstance(result, QueryResult)
        assert result.agent_response == "Diabetes symptoms include increased thirst, frequent urination..."
        assert result.domain == "medical"
        assert result.documents == ["medical_doc1.pdf", "medical_doc2.pdf"]
        mock_graph.invoke.assert_called_once_with({"query": query, "domain": ResearchType.WEB})

class TestResearchGraphIntegration:
    def test_research_graph_workflow_structure(self):
        graph = _build_research_graph()
        
        assert graph is not None
        assert hasattr(graph, 'invoke')
        
        try:
            assert callable(graph.invoke)
        except Exception as e:
            pytest.fail(f"Graph structure test failed: {e}")

    @patch('app.workflows.research_graph._classify_domain')
    @patch('app.workflows.research_graph._identify_medical_terms')
    @patch('app.workflows.research_graph._retrieve_sources')
    @patch('app.workflows.research_graph._synthesize_answer')
    def test_medical_query_flow(self, mock_synthesize, mock_retrieve, mock_identify, mock_classify):
        """Test that medical queries go through identify -> retrieve -> synthesize"""
        mock_classify.return_value = ResearchState(
            query="What are diabetes symptoms?",
            domain=ResearchType.MEDICAL
        )
        
        mock_identify.return_value = ResearchState(
            query="What are diabetes symptoms?",
            domain=ResearchType.MEDICAL,
            terms="diabetes, symptoms, blood sugar"
        )
        
        mock_retrieve.return_value = ResearchState(
            query="What are diabetes symptoms?",
            domain=ResearchType.MEDICAL,
            terms="diabetes, symptoms, blood sugar",
            sources=["Medical Source 1"],
            documents=["doc1.pdf"]
        )
        
        mock_synthesize.return_value = ResearchState(
            query="What are diabetes symptoms?",
            domain=ResearchType.MEDICAL,
            terms="diabetes, symptoms, blood sugar",
            sources=["Medical Source 1"],
            documents=["doc1.pdf"],
            answer="Diabetes symptoms include..."
        )
        
        graph = _build_research_graph()
        graph.invoke({"query": "What are diabetes symptoms?", "domain": ResearchType.WEB})
        
        mock_classify.assert_called_once()
        mock_identify.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_synthesize.assert_called_once()

    @patch('app.workflows.research_graph._classify_domain')
    @patch('app.workflows.research_graph._retrieve_sources')
    @patch('app.workflows.research_graph._synthesize_answer')
    def test_non_medical_query_flow(self, mock_synthesize, mock_retrieve, mock_classify):
        """Test that non-medical queries skip identify and go directly to retrieve -> synthesize"""
        mock_classify.return_value = ResearchState(
            query="What is machine learning?",
            domain=ResearchType.ACADEMIC
        )
        
        mock_retrieve.return_value = ResearchState(
            query="What is machine learning?",
            domain=ResearchType.ACADEMIC,
            sources=["Academic Source 1"],
            documents=["paper1.pdf"]
        )
        
        mock_synthesize.return_value = ResearchState(
            query="What is machine learning?",
            domain=ResearchType.ACADEMIC,
            sources=["Academic Source 1"],
            documents=["paper1.pdf"],
            answer="Machine learning is..."
        )
        
        graph = _build_research_graph()
        graph.invoke({"query": "What is machine learning?", "domain": ResearchType.WEB})
        
        mock_classify.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_synthesize.assert_called_once()
        
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

class TestRouteAfterClassify:
    def test_route_medical_to_identify(self):
        state = ResearchState(
            query="What are the symptoms of diabetes?",
            domain=ResearchType.MEDICAL
        )

        result = _route_after_classify(state)
        assert result == "identify"

    def test_route_academic_to_retrieve(self):
        state = ResearchState(
            query="What is machine learning?",
            domain=ResearchType.ACADEMIC
        )

        result = _route_after_classify(state)
        assert result == "retrieve"

    def test_route_knowledge_to_retrieve(self):
        state = ResearchState(
            query="What is the capital of France?",
            domain=ResearchType.KNOWLEDGE
        )

        result = _route_after_classify(state)
        assert result == "retrieve"

    def test_route_web_to_retrieve(self):
        state = ResearchState(
            query="What's the weather today?",
            domain=ResearchType.WEB
        )

        result = _route_after_classify(state)
        assert result == "retrieve"


class TestIdentifyMedicalTerms:
    def test_identify_medical_terms_function_exists(self):
        """Test that the _identify_medical_terms function exists and is callable"""
        assert callable(_identify_medical_terms)

    def test_identify_medical_terms_state_structure(self):
        """Test that the function maintains proper state structure"""
        state = ResearchState(
            query="What are the symptoms of diabetes?",
            domain=ResearchType.MEDICAL
        )

        try:
            result = _identify_medical_terms(state)
            assert isinstance(result, dict)
            assert "query" in result
            assert "domain" in result
        except Exception as e:
            assert "OpenAI" in str(e) or "API" in str(e) or "key" in str(e).lower()
