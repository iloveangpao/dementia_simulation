"""
Tests for the RAG Pipeline implementation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag_pipeline import RAGPipeline, generate_response, create_rag_pipeline


class TestRAGPipeline(unittest.TestCase):
    """Test cases for RAG Pipeline functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_persona = {
            "name": "Mary",
            "age": "75", 
            "condition": "mild dementia",
            "personality": "gentle and caring"
        }
        
        self.sample_history = [
            {
                "user": "Good morning! How are you feeling today?",
                "assistant": "Oh, good morning dear. I'm feeling a bit confused this morning."
            }
        ]
        
        self.sample_input = "Would you like to have breakfast now?"
    
    def test_rag_pipeline_initialization(self):
        """Test RAG pipeline initialization"""        
        rag = RAGPipeline()
        
        self.assertIsNotNone(rag)
        self.assertEqual(rag.model_name, "microsoft/DialoGPT-medium")
        # Pipeline will be None due to missing transformers library
        self.assertIsNone(rag.pipeline)
    
    def test_retrieve_documents(self):
        """Test document retrieval functionality"""
        rag = RAGPipeline()
        
        docs = rag.retrieve_documents("memory loss")
        
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        self.assertLessEqual(len(docs), 3)  # Default top_k
    
    def test_build_persona_prompt(self):
        """Test persona-aware prompt building"""
        rag = RAGPipeline()
        
        context_docs = ["Dementia patients often experience memory loss."]
        prompt = rag.build_persona_prompt(
            self.sample_input, 
            self.sample_persona, 
            self.sample_history, 
            context_docs
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Mary", prompt)
        self.assertIn("mild dementia", prompt)
        self.assertIn("breakfast", prompt)
    
    def test_generate_response_success(self):
        """Test successful response generation"""
        rag = RAGPipeline()
        
        # Mock the pipeline to simulate having transformers available
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = [{"generated_text": "Yes, I would like breakfast please."}]
        rag.pipeline = mock_pipeline_instance
        
        response = rag.generate_response(
            self.sample_input,
            self.sample_persona,
            self.sample_history
        )
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_generate_response_fallback(self):
        """Test fallback response when pipeline is not available"""
        rag = RAGPipeline()
        # pipeline will be None due to missing transformers library
        
        response = rag.generate_response(
            self.sample_input,
            self.sample_persona,
            self.sample_history
        )
        
        # Should return fallback response
        self.assertIsInstance(response, str)
        self.assertIn("Mary", response)
        self.assertIn("trouble finding the right words", response)
    
    def test_post_process_response(self):
        """Test response post-processing"""
        rag = RAGPipeline()
        
        # Test normal response
        response = rag._post_process_response("Yes, I would like breakfast.", self.sample_persona)
        self.assertEqual(response, "Yes, I would like breakfast.")
        
        # Test empty response
        response = rag._post_process_response("", self.sample_persona)
        self.assertIn("Mary", response)
        
        # Test very long response
        long_response = " ".join(["word"] * 50)
        response = rag._post_process_response(long_response, self.sample_persona)
        self.assertTrue(response.endswith("..."))
    
    @patch('rag_pipeline.create_rag_pipeline')
    def test_convenience_function(self, mock_create_rag):
        """Test the convenience generate_response function"""
        mock_pipeline = Mock()
        mock_pipeline.generate_response.return_value = "Test response"
        mock_create_rag.return_value = mock_pipeline
        
        response = generate_response(
            self.sample_input,
            self.sample_persona,
            self.sample_history
        )
        
        self.assertEqual(response, "Test response")
        mock_create_rag.assert_called_once()
        mock_pipeline.generate_response.assert_called_once_with(
            self.sample_input,
            self.sample_persona,
            self.sample_history
        )
    
    def test_factory_function(self):
        """Test the factory function"""
        rag = create_rag_pipeline("test-model")
        
        self.assertIsInstance(rag, RAGPipeline)
        self.assertEqual(rag.model_name, "test-model")


class TestIntegration(unittest.TestCase):
    """Integration tests for the RAG pipeline"""
    
    def test_full_pipeline_structure(self):
        """Test that the pipeline has all required components"""
        rag = RAGPipeline()
        
        # Check that all required methods exist
        self.assertTrue(hasattr(rag, 'retrieve_documents'))
        self.assertTrue(hasattr(rag, 'build_persona_prompt'))
        self.assertTrue(hasattr(rag, 'generate_response'))
        self.assertTrue(callable(rag.retrieve_documents))
        self.assertTrue(callable(rag.build_persona_prompt))
        self.assertTrue(callable(rag.generate_response))


if __name__ == '__main__':
    unittest.main()