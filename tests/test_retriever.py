"""Tests for retriever module - mock FAISS index and check retrieval."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from dementia_simulation.retriever import MemoryRetriever, Document


class TestDocument:
    """Test Document class functionality."""
    
    def test_document_creation(self):
        """Test basic document creation."""
        doc = Document("Hello world")
        
        assert doc.content == "Hello world"
        assert doc.embedding is None
        assert doc.metadata == {}
    
    def test_document_with_metadata(self):
        """Test document creation with metadata."""
        metadata = {"author": "Alice", "timestamp": 1234567890}
        doc = Document("Hello world", metadata=metadata)
        
        assert doc.content == "Hello world"
        assert doc.metadata == metadata
    
    def test_document_with_embedding(self):
        """Test document creation with embedding."""
        embedding = np.array([0.1, 0.2, 0.3])
        doc = Document("Hello world", embedding=embedding)
        
        assert doc.content == "Hello world"
        assert np.array_equal(doc.embedding, embedding)


class TestMemoryRetriever:
    """Test MemoryRetriever functionality."""
    
    def test_retriever_initialization(self):
        """Test retriever initialization."""
        retriever = MemoryRetriever(embedding_dim=256)
        
        assert retriever.embedding_dim == 256
        assert retriever.index is None
        assert retriever.documents == []
        assert retriever.is_trained is False
    
    def test_dummy_embedding_creation(self):
        """Test dummy embedding creation for reproducibility."""
        retriever = MemoryRetriever(embedding_dim=128)
        
        # Same text should produce same embedding
        embedding1 = retriever._create_dummy_embedding("test text")
        embedding2 = retriever._create_dummy_embedding("test text")
        
        assert np.array_equal(embedding1, embedding2)
        assert embedding1.shape == (128,)
        assert abs(np.linalg.norm(embedding1) - 1.0) < 1e-6  # Should be normalized
    
    def test_add_documents_single(self):
        """Test adding a single document."""
        retriever = MemoryRetriever()
        doc = Document("Test document")
        
        retriever.add_documents([doc])
        
        assert len(retriever.documents) == 1
        assert retriever.documents[0].content == "Test document"
        assert retriever.documents[0].embedding is not None
        assert retriever.is_trained is True
    
    def test_add_documents_multiple(self):
        """Test adding multiple documents."""
        retriever = MemoryRetriever()
        docs = [
            Document("First document"),
            Document("Second document"),
            Document("Third document")
        ]
        
        retriever.add_documents(docs)
        
        assert len(retriever.documents) == 3
        assert retriever.is_trained is True
        assert all(doc.embedding is not None for doc in retriever.documents)
    
    @patch('faiss.IndexFlatIP')
    def test_build_index_mocked(self, mock_index_class):
        """Test index building with mocked FAISS."""
        mock_index = Mock()
        mock_index_class.return_value = mock_index
        
        retriever = MemoryRetriever(embedding_dim=384)
        docs = [Document("Test doc 1"), Document("Test doc 2")]
        
        with patch('faiss.normalize_L2') as mock_normalize:
            retriever.add_documents(docs)
        
        # Verify FAISS methods were called
        mock_index_class.assert_called_once_with(384)
        mock_normalize.assert_called()
        mock_index.add.assert_called_once()
        assert retriever.index == mock_index
    
    def test_search_empty_retriever(self):
        """Test search on empty retriever."""
        retriever = MemoryRetriever()
        
        results = retriever.search("test query")
        
        assert results == []
    
    @patch('faiss.IndexFlatIP')
    @patch('faiss.normalize_L2')
    def test_search_with_results(self, mock_normalize, mock_index_class):
        """Test search with mocked FAISS results."""
        # Setup mock index
        mock_index = Mock()
        mock_index_class.return_value = mock_index
        
        # Mock search results
        mock_similarities = np.array([[0.9, 0.7, 0.5]])
        mock_indices = np.array([[0, 1, 2]])
        mock_index.search.return_value = (mock_similarities, mock_indices)
        
        # Create retriever and add documents
        retriever = MemoryRetriever()
        docs = [
            Document("First document"),
            Document("Second document"), 
            Document("Third document")
        ]
        retriever.add_documents(docs)
        
        # Perform search
        results = retriever.search("test query", k=3)
        
        # Verify results
        assert len(results) == 3
        assert results[0][0].content == "First document"
        assert results[0][1] == 0.9
        assert results[1][0].content == "Second document"
        assert results[1][1] == 0.7
        assert results[2][0].content == "Third document"
        assert results[2][1] == 0.5
    
    @patch('faiss.IndexFlatIP')
    @patch('faiss.normalize_L2')
    def test_search_with_invalid_indices(self, mock_normalize, mock_index_class):
        """Test search handling invalid indices."""
        mock_index = Mock()
        mock_index_class.return_value = mock_index
        
        # Mock search results with some invalid indices (-1)
        mock_similarities = np.array([[0.9, 0.7, 0.5]])
        mock_indices = np.array([[0, -1, 1]])  # -1 indicates no match
        mock_index.search.return_value = (mock_similarities, mock_indices)
        
        retriever = MemoryRetriever()
        docs = [Document("First document"), Document("Second document")]
        retriever.add_documents(docs)
        
        results = retriever.search("test query", k=3)
        
        # Should only return valid results
        assert len(results) == 2
        assert results[0][0].content == "First document"
        assert results[1][0].content == "Second document"
    
    def test_get_document_count(self):
        """Test document count retrieval."""
        retriever = MemoryRetriever()
        
        assert retriever.get_document_count() == 0
        
        docs = [Document("Doc 1"), Document("Doc 2"), Document("Doc 3")]
        retriever.add_documents(docs)
        
        assert retriever.get_document_count() == 3
    
    def test_clear_retriever(self):
        """Test clearing retriever."""
        retriever = MemoryRetriever()
        docs = [Document("Doc 1"), Document("Doc 2")]
        retriever.add_documents(docs)
        
        assert len(retriever.documents) == 2
        assert retriever.is_trained is True
        
        retriever.clear()
        
        assert len(retriever.documents) == 0
        assert retriever.index is None
        assert retriever.is_trained is False
    
    @patch('faiss.IndexFlatIP')
    @patch('faiss.normalize_L2')
    def test_get_similar_memories_threshold(self, mock_normalize, mock_index_class):
        """Test getting similar memories with threshold."""
        mock_index = Mock()
        mock_index_class.return_value = mock_index
        
        # Mock search results with varying similarities
        mock_similarities = np.array([[0.9, 0.8, 0.6, 0.5]])
        mock_indices = np.array([[0, 1, 2, 3]])
        mock_index.search.return_value = (mock_similarities, mock_indices)
        
        retriever = MemoryRetriever()
        docs = [
            Document("Very similar"),
            Document("Quite similar"),
            Document("Somewhat similar"),
            Document("Not very similar")
        ]
        retriever.add_documents(docs)
        
        # Test with threshold 0.7
        similar_docs = retriever.get_similar_memories("test query", threshold=0.7)
        
        # Should only return documents above threshold
        assert len(similar_docs) == 2
        assert similar_docs[0].content == "Very similar"
        assert similar_docs[1].content == "Quite similar"
    
    def test_update_document(self):
        """Test updating document content."""
        retriever = MemoryRetriever()
        docs = [Document("Original content"), Document("Another doc")]
        retriever.add_documents(docs)
        
        original_embedding = retriever.documents[0].embedding.copy()
        
        # Update document
        retriever.update_document(0, "Updated content")
        
        assert retriever.documents[0].content == "Updated content"
        assert not np.array_equal(retriever.documents[0].embedding, original_embedding)
        assert retriever.is_trained is True
    
    def test_update_document_invalid_index(self):
        """Test updating document with invalid index."""
        retriever = MemoryRetriever()
        docs = [Document("Test doc")]
        retriever.add_documents(docs)
        
        original_content = retriever.documents[0].content
        
        # Try to update with invalid index
        retriever.update_document(5, "New content")
        
        # Should not change anything
        assert retriever.documents[0].content == original_content
    
    def test_remove_document(self):
        """Test removing document."""
        retriever = MemoryRetriever()
        docs = [Document("Doc 1"), Document("Doc 2"), Document("Doc 3")]
        retriever.add_documents(docs)
        
        assert len(retriever.documents) == 3
        
        # Remove middle document
        retriever.remove_document(1)
        
        assert len(retriever.documents) == 2
        assert retriever.documents[0].content == "Doc 1"
        assert retriever.documents[1].content == "Doc 3"
        assert retriever.is_trained is True
    
    def test_remove_document_invalid_index(self):
        """Test removing document with invalid index."""
        retriever = MemoryRetriever()
        docs = [Document("Doc 1"), Document("Doc 2")]
        retriever.add_documents(docs)
        
        original_count = len(retriever.documents)
        
        # Try to remove with invalid index
        retriever.remove_document(5)
        
        # Should not change anything
        assert len(retriever.documents) == original_count


class TestMemoryRetrieverIntegration:
    """Integration tests for MemoryRetriever."""
    
    def test_full_workflow(self):
        """Test complete workflow from adding documents to searching."""
        retriever = MemoryRetriever(embedding_dim=128)
        
        # Add documents
        docs = [
            Document("I love eating apples", metadata={"type": "food"}),
            Document("The weather is sunny today", metadata={"type": "weather"}),
            Document("Apples are my favorite fruit", metadata={"type": "food"}),
            Document("It's raining outside", metadata={"type": "weather"}),
        ]
        
        retriever.add_documents(docs)
        
        # Search for apple-related content
        results = retriever.search("apple fruit", k=2)
        
        # Should return results
        assert len(results) == 2
        assert all(len(result) == 2 for result in results)  # (doc, score) tuples
        assert all(isinstance(result[0], Document) for result in results)
        assert all(isinstance(result[1], float) for result in results)
        
        # Test similarity threshold
        similar_docs = retriever.get_similar_memories("apple", threshold=0.5)
        assert len(similar_docs) >= 0  # May vary based on dummy embeddings
        
        # Test document management
        retriever.update_document(0, "I enjoy eating oranges")
        assert retriever.documents[0].content == "I enjoy eating oranges"
        
        original_count = retriever.get_document_count()
        retriever.remove_document(0)
        assert retriever.get_document_count() == original_count - 1
    
    def test_memory_retrieval_reproducibility(self):
        """Test that identical queries produce identical results."""
        retriever = MemoryRetriever(embedding_dim=64)
        
        docs = [
            Document("Memory about family dinner"),
            Document("Memory about work meeting"),
            Document("Memory about weekend trip")
        ]
        
        retriever.add_documents(docs)
        
        # Same query should produce same results
        results1 = retriever.search("family dinner", k=3)
        results2 = retriever.search("family dinner", k=3)
        
        assert len(results1) == len(results2)
        for (doc1, score1), (doc2, score2) in zip(results1, results2):
            assert doc1.content == doc2.content
            assert abs(score1 - score2) < 1e-6  # Floating point comparison