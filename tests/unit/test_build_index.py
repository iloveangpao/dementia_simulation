"""Unit tests for build_index.py utility."""

import pytest
import os
import json
import tempfile
from pathlib import Path
import sys

# Add project root to path to import build_index
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from build_index import (
    load_documents_from_json,
    load_documents_from_markdown,
    discover_documents,
)


class TestDocumentLoaders:
    """Test document loading functions."""

    def test_load_documents_from_json(self, temp_dir):
        """Test loading documents from JSON file."""
        # Create test JSON file
        test_docs = [
            {"text": "Test document 1", "category": "test"},
            {"text": "Test document 2", "category": "test"},
        ]
        json_file = os.path.join(temp_dir, "test_docs.json")
        with open(json_file, "w") as f:
            json.dump(test_docs, f)

        # Load documents
        loaded_docs = load_documents_from_json(json_file)

        assert len(loaded_docs) == 2
        assert loaded_docs[0]["text"] == "Test document 1"
        assert loaded_docs[1]["text"] == "Test document 2"

    def test_load_documents_from_markdown(self, temp_dir):
        """Test loading documents from Markdown file."""
        # Create test Markdown file
        md_content = """# Title

## Section 1

This is the first section with some content about dementia care.
It should be extracted as a separate document.

## Section 2

This is the second section with more information.
It also should be extracted separately.

Some more text to make it long enough.
"""
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w") as f:
            f.write(md_content)

        # Load documents
        loaded_docs = load_documents_from_markdown(md_file)

        assert len(loaded_docs) == 2
        assert loaded_docs[0]["title"] == "Section 1"
        assert loaded_docs[1]["title"] == "Section 2"
        assert "dementia care" in loaded_docs[0]["text"]
        assert loaded_docs[0]["source_file"] == "test.md"

    def test_load_documents_from_markdown_filters_short_sections(self, temp_dir):
        """Test that short sections are filtered out."""
        md_content = """## Section 1

Short text.

## Section 2

This is a much longer section that should be included because it has enough
content to be meaningful and useful for the knowledge base system.
"""
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w") as f:
            f.write(md_content)

        loaded_docs = load_documents_from_markdown(md_file)

        # Only the longer section should be included
        assert len(loaded_docs) == 1
        assert loaded_docs[0]["title"] == "Section 2"

    def test_discover_documents(self, temp_dir):
        """Test document discovery from multiple directories."""
        # Create processed directory with JSON
        processed_dir = os.path.join(temp_dir, "processed")
        os.makedirs(processed_dir)
        test_docs = [{"text": "Processed document", "category": "processed"}]
        with open(os.path.join(processed_dir, "docs.json"), "w") as f:
            json.dump(test_docs, f)

        # Create knowledge base directory with Markdown
        kb_dir = os.path.join(temp_dir, "knowledge_base")
        os.makedirs(kb_dir)
        md_content = """## Care Guidelines

This section contains comprehensive care guidelines for dementia patients.
It includes best practices and recommendations from experts.
"""
        with open(os.path.join(kb_dir, "guide.md"), "w") as f:
            f.write(md_content)

        # Discover documents
        all_docs = discover_documents(processed_dir, kb_dir)

        # Should find documents from both directories
        assert len(all_docs) == 2
        texts = [doc["text"] for doc in all_docs]
        assert any("Processed document" in text for text in texts)
        assert any("care guidelines" in text.lower() for text in texts)

    def test_discover_documents_handles_missing_dirs(self, temp_dir):
        """Test discovery with non-existent directories."""
        # Use non-existent directories
        processed_dir = os.path.join(temp_dir, "nonexistent_processed")
        kb_dir = os.path.join(temp_dir, "nonexistent_kb")

        all_docs = discover_documents(processed_dir, kb_dir)

        # Should return empty list without error
        assert all_docs == []

    def test_discover_documents_ignores_invalid_files(self, temp_dir):
        """Test that invalid files are gracefully ignored."""
        kb_dir = os.path.join(temp_dir, "knowledge_base")
        os.makedirs(kb_dir)

        # Create invalid JSON file
        with open(os.path.join(kb_dir, "invalid.json"), "w") as f:
            f.write("{invalid json")

        # Should not raise error, just skip the file
        all_docs = discover_documents(temp_dir, kb_dir)
        assert isinstance(all_docs, list)


class TestBuildIndexIntegration:
    """Integration tests for the build_index script."""

    def test_build_index_with_knowledge_base(self):
        """Test building index from actual knowledge base."""
        # This test uses the actual knowledge_base directory
        kb_dir = "data/knowledge_base"

        if not os.path.exists(kb_dir):
            pytest.skip("Knowledge base directory not found")

        # Import after ensuring modules are available
        from src.dementia_simulation.retriever.faiss_retriever import FAISSRetriever

        with tempfile.TemporaryDirectory() as tmpdir:
            # Load documents
            docs = discover_documents("data/processed", kb_dir)

            # Should find at least the dementia_care_guide.md
            assert len(docs) > 0

            # Build index
            index_path = os.path.join(tmpdir, "test_index.index")
            docs_path = os.path.join(tmpdir, "test_docs.json")

            retriever = FAISSRetriever(index_path=index_path, documents_path=docs_path)
            retriever.create_index("flat")
            retriever.add_documents(docs)
            retriever.save_index()

            # Verify files were created
            assert os.path.exists(index_path)
            assert os.path.exists(docs_path)

            # Test retrieval
            results = retriever.search("communication with dementia patients", k=3)
            assert len(results) > 0
            assert all(isinstance(score, float) for _, score in results)
