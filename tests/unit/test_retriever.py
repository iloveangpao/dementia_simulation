"""Unit tests for FAISS retriever."""

import os
import pytest

from dementia_simulation.retriever.faiss_retriever import (
    FAISSRetriever,
    create_dementia_knowledge_base,
    initialize_retriever_with_knowledge_base,
)


class TestFAISSRetriever:
    """Test FAISSRetriever class."""

    def test_retriever_initialization(self, temp_dir):
        """Test retriever initialization."""
        index_path = os.path.join(temp_dir, "test_index.index")
        docs_path = os.path.join(temp_dir, "test_docs.json")

        retriever = FAISSRetriever(
            model_name="all-MiniLM-L6-v2",
            index_path=index_path,
            documents_path=docs_path
        )

        assert retriever.model_name == "all-MiniLM-L6-v2"
        assert retriever.index_path == index_path
        assert retriever.documents_path == docs_path
        assert retriever.dimension > 0  # Should have embedding dimension

    def test_create_index(self, temp_dir):
        """Test index creation."""
        retriever = FAISSRetriever()

        # Test flat index
        index = retriever.create_index("flat")
        assert index is not None
        assert retriever.index is not None

        # Test with invalid index type
        with pytest.raises(ValueError):
            retriever.create_index("invalid_type")

    def test_add_documents(self, temp_dir):
        """Test adding documents to the index."""
        retriever = FAISSRetriever()

        documents = [
            {"text": "This is a test document about dementia care.", "category": "test"},
            {"text": "Another document about patient communication.", "category": "test"}
        ]

        retriever.add_documents(documents)

        assert len(retriever.documents) == 2
        assert retriever.index is not None
        assert retriever.index.ntotal == 2  # Should have 2 vectors

    def test_search_empty_index(self, temp_dir):
        """Test searching with empty index."""
        retriever = FAISSRetriever()

        results = retriever.search("test query", k=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_with_documents(self, temp_dir):
        """Test searching with documents."""
        retriever = FAISSRetriever()

        documents = [
            {"text": "Information about dementia care and empathy.", "category": "care"},
            {"text": "Validation therapy techniques for patients.", "category": "therapy"},
            {"text": "Completely unrelated content about cooking.", "category": "other"}
        ]

        retriever.add_documents(documents)

        # Search for relevant content
        results = retriever.search("dementia care empathy", k=3)

        assert isinstance(results, list)
        assert len(results) <= 3

        # Results should be tuples of (document, score)
        for doc, score in results:
            assert isinstance(doc, dict)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    def test_save_and_load_index(self, temp_dir):
        """Test saving and loading index."""
        index_path = os.path.join(temp_dir, "test_index.index")
        docs_path = os.path.join(temp_dir, "test_docs.json")

        # Create and populate retriever
        retriever1 = FAISSRetriever(index_path=index_path, documents_path=docs_path)

        documents = [
            {"text": "Test document for saving", "category": "test"},
            {"text": "Another test document", "category": "test"}
        ]

        retriever1.add_documents(documents)
        retriever1.save_index()

        # Check files were created
        assert os.path.exists(index_path)
        assert os.path.exists(docs_path)

        # Load in new retriever
        retriever2 = FAISSRetriever(index_path=index_path, documents_path=docs_path)
        success = retriever2.load_index()

        assert success
        assert len(retriever2.documents) == 2
        assert retriever2.index is not None
        assert retriever2.index.ntotal == 2

    def test_get_stats(self, temp_dir):
        """Test getting retriever statistics."""
        retriever = FAISSRetriever()

        stats = retriever.get_stats()

        assert isinstance(stats, dict)
        assert "model_name" in stats
        assert "embedding_dimension" in stats
        assert "total_documents" in stats
        assert "index_trained" in stats
        assert "index_total_vectors" in stats

        # Add some documents and check stats update
        documents = [{"text": "Test document", "category": "test"}]
        retriever.add_documents(documents)

        new_stats = retriever.get_stats()
        assert new_stats["total_documents"] == 1
        assert new_stats["index_total_vectors"] == 1


class TestKnowledgeBase:
    """Test knowledge base functions."""

    def test_create_dementia_knowledge_base(self):
        """Test creating the dementia knowledge base."""
        documents = create_dementia_knowledge_base()

        assert isinstance(documents, list)
        assert len(documents) > 0

        # Check document structure
        for doc in documents:
            assert isinstance(doc, dict)
            assert "text" in doc
            assert "category" in doc
            assert "severity" in doc
            assert "topic" in doc

            # Check that text is not empty
            assert len(doc["text"]) > 0

            # Check severity levels
            assert isinstance(doc["severity"], list)
            for severity in doc["severity"]:
                assert severity in ["mild", "moderate", "severe"]

    def test_initialize_retriever_with_knowledge_base(self, temp_dir):
        """Test initializing retriever with knowledge base."""
        index_path = os.path.join(temp_dir, "kb_index.index")
        docs_path = os.path.join(temp_dir, "kb_docs.json")

        retriever = FAISSRetriever(index_path=index_path, documents_path=docs_path)

        initialize_retriever_with_knowledge_base(retriever)

        # Should have loaded knowledge base
        assert len(retriever.documents) > 0
        assert retriever.index is not None
        assert retriever.index.ntotal > 0

        # Should be able to search
        results = retriever.search("agitation in dementia", k=3)
        assert len(results) > 0

        # Check that files were saved
        assert os.path.exists(index_path)
        assert os.path.exists(docs_path)

    def test_knowledge_base_content_quality(self):
        """Test quality of knowledge base content."""
        documents = create_dementia_knowledge_base()

        # Check for coverage of different topics
        topics = set()
        categories = set()
        severities = set()

        for doc in documents:
            topics.add(doc["topic"])
            categories.add(doc["category"])
            for severity in doc["severity"]:
                severities.add(severity)

        # Should cover multiple topics and categories
        assert len(topics) >= 5
        assert len(categories) >= 3

        # Should cover all severity levels
        assert "mild" in severities
        assert "moderate" in severities
        assert "severe" in severities

        # Check text quality (minimum length, no empty docs)
        for doc in documents:
            assert len(doc["text"]) >= 50  # Reasonable minimum length
            assert not doc["text"].isspace()  # Not just whitespace
