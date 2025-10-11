"""Unit tests for build_index utility."""

import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from build_index import load_processed_chunks, load_knowledge_base_markdown, build_index


class TestLoadProcessedChunks:
    """Test loading processed chunks."""

    def test_load_existing_chunks(self, tmp_path):
        """Test loading chunks from a valid JSON file."""
        # Create test chunks file
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()

        chunks_file = processed_dir / "text_chunks.json"
        test_chunks = [
            {"text": "Test chunk 1", "source": "test1.txt", "id": 0},
            {"text": "Test chunk 2", "source": "test2.txt", "id": 1},
        ]

        with open(chunks_file, "w") as f:
            json.dump(test_chunks, f)

        # Load chunks
        result = load_processed_chunks(str(processed_dir))

        assert len(result) == 2
        assert result[0]["text"] == "Test chunk 1"
        assert result[1]["text"] == "Test chunk 2"

    def test_load_nonexistent_chunks(self, tmp_path):
        """Test loading from non-existent directory."""
        result = load_processed_chunks(str(tmp_path / "nonexistent"))
        assert result == []


class TestLoadKnowledgeBaseMarkdown:
    """Test loading knowledge base markdown files."""

    def test_load_markdown_files(self, tmp_path):
        """Test loading and parsing markdown files."""
        kb_dir = tmp_path / "knowledge_base"
        kb_dir.mkdir()

        # Create test markdown file
        md_file = kb_dir / "test_guide.md"
        md_content = """# Test Guide

## Section 1

This is a test paragraph with some content.
It has multiple sentences.

## Section 2

Another paragraph here with more information.
More details about care strategies.

### Subsection

Even more detailed information in this subsection.
"""
        md_file.write_text(md_content)

        # Load documents
        result = load_knowledge_base_markdown(str(kb_dir))

        # Should have multiple chunks
        assert len(result) > 0

        # Check structure
        for doc in result:
            assert "text" in doc
            assert "source_file" in doc
            assert "chunk_id" in doc
            assert "category" in doc
            assert doc["category"] == "knowledge_base"
            assert doc["source_file"] == "test_guide.md"
            # All chunks should be at least 50 chars (per filtering logic)
            assert len(doc["text"]) >= 50

    def test_load_empty_kb_dir(self, tmp_path):
        """Test loading from empty directory."""
        kb_dir = tmp_path / "empty_kb"
        kb_dir.mkdir()

        result = load_knowledge_base_markdown(str(kb_dir))
        assert result == []

    def test_load_nonexistent_kb_dir(self, tmp_path):
        """Test loading from non-existent directory."""
        result = load_knowledge_base_markdown(str(tmp_path / "nonexistent"))
        assert result == []


class TestBuildIndex:
    """Test build_index function."""

    def test_build_index_with_default_source(self, tmp_path):
        """Test building index with default knowledge base."""
        output_dir = tmp_path / "embeddings"

        # Build index
        build_index(
            output_dir=str(output_dir),
            source="default",
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        # Check that files were created
        assert (output_dir / "faiss_index.index").exists()
        assert (output_dir / "documents.json").exists()

        # Verify documents.json content
        with open(output_dir / "documents.json", "r") as f:
            documents = json.load(f)

        assert len(documents) > 0

        # Check document structure
        for doc in documents:
            assert "text" in doc
            assert "category" in doc
            assert "id" in doc

    def test_build_index_with_knowledge_base_source(self, tmp_path):
        """Test building index from markdown knowledge base."""
        # Create knowledge base
        kb_dir = tmp_path / "knowledge_base"
        kb_dir.mkdir()

        md_file = kb_dir / "care_guide.md"
        md_content = """# Care Guide

## Communication Tips

When communicating with dementia patients, use simple clear language.
Be patient and allow time for responses.

## Behavioral Management

Look for triggers and redirect attention to positive activities.
Maintain a calm demeanor and soothing voice tone.
"""
        md_file.write_text(md_content)

        output_dir = tmp_path / "embeddings"

        # Build index
        build_index(
            output_dir=str(output_dir),
            source="knowledge_base",
            kb_dir=str(kb_dir),
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        # Check that files were created
        assert (output_dir / "faiss_index.index").exists()
        assert (output_dir / "documents.json").exists()

        # Verify documents
        with open(output_dir / "documents.json", "r") as f:
            documents = json.load(f)

        assert len(documents) > 0

        # Should have knowledge_base category
        assert any(doc["category"] == "knowledge_base" for doc in documents)
        assert any(doc["source_file"] == "care_guide.md" for doc in documents)

    def test_build_index_with_auto_source(self, tmp_path):
        """Test auto-detection of document source."""
        output_dir = tmp_path / "embeddings"

        # Build with auto (should fall back to default)
        build_index(
            output_dir=str(output_dir),
            source="auto",
            processed_dir=str(tmp_path / "nonexistent_processed"),
            kb_dir=str(tmp_path / "nonexistent_kb"),
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        # Should still create files using default knowledge base
        assert (output_dir / "faiss_index.index").exists()
        assert (output_dir / "documents.json").exists()


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_build_and_load_index(self, tmp_path):
        """Test building an index and then loading it with retriever."""
        from src.dementia_simulation.retriever.faiss_retriever import FAISSRetriever

        output_dir = tmp_path / "embeddings"

        # Build index
        build_index(
            output_dir=str(output_dir),
            source="default",
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        # Create retriever and load index
        index_path = output_dir / "faiss_index.index"
        docs_path = output_dir / "documents.json"

        retriever = FAISSRetriever(
            index_path=str(index_path), documents_path=str(docs_path), device="cpu"
        )

        # Load the index
        success = retriever.load_index()
        assert success

        # Test search
        results = retriever.search("dementia care", k=3)
        assert len(results) > 0

        # Verify result structure
        for doc, score in results:
            assert isinstance(doc, dict)
            assert "text" in doc
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
