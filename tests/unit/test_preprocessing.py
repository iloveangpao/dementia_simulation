"""Unit tests for preprocessing functionality."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from run_preprocessing import (
    chunk_text,
    clean_text,
    process_csv_file,
    process_document,
)


class TestCleanText:
    """Test text cleaning function."""

    def test_clean_excessive_whitespace(self):
        """Test removing excessive whitespace."""
        text = "This  is   a    test"
        result = clean_text(text)
        assert result == "This is a test"

    def test_clean_special_characters(self):
        """Test removing special characters."""
        text = "Test @ # $ % text"
        result = clean_text(text)
        assert "@" not in result
        assert "#" not in result

    def test_preserve_punctuation(self):
        """Test that punctuation is preserved."""
        text = "Hello, world! How are you?"
        result = clean_text(text)
        assert "," in result
        assert "!" in result
        assert "?" in result

    def test_strip_whitespace(self):
        """Test stripping leading/trailing whitespace."""
        text = "  test content  "
        result = clean_text(text)
        assert result == "test content"


class TestChunkText:
    """Test text chunking function."""

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        text = "This is a short sentence."
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_long_text(self):
        """Test chunking longer text."""
        # Create text with multiple sentences
        sentences = [
            "This is sentence one.",
            "This is sentence two.",
            "This is sentence three.",
            "This is sentence four.",
            "This is sentence five.",
        ]
        text = " ".join(sentences)
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        # Should create multiple chunks
        assert len(chunks) > 1

    def test_chunk_overlap(self):
        """Test that chunks have appropriate overlap."""
        text = (
            "First sentence here. Second sentence here. "
            "Third sentence here. Fourth sentence here."
        )
        chunks = chunk_text(text, chunk_size=5, overlap=2)
        # With overlap, there should be some shared content
        assert len(chunks) >= 2


class TestProcessCSVFile:
    """Test CSV file processing."""

    def test_process_valid_csv(self, tmp_path):
        """Test processing a valid CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age,condition\nJohn,65,dementia\nJane,70,alzheimers\n"
        csv_file.write_text(csv_content)

        result = process_csv_file(str(csv_file))

        assert "John" in result
        assert "Jane" in result
        assert "dementia" in result

    def test_process_invalid_csv(self, tmp_path):
        """Test handling invalid CSV file."""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("not,a,proper\ncsv")

        # Should not raise an error, but return text
        result = process_csv_file(str(csv_file))
        assert isinstance(result, str)

    def test_process_nonexistent_csv(self):
        """Test handling non-existent CSV file."""
        result = process_csv_file("nonexistent.csv")
        assert result == ""


class TestProcessDocument:
    """Test document processing function."""

    def test_process_csv_document(self, tmp_path):
        """Test processing a CSV document."""
        csv_file = tmp_path / "test.csv"
        csv_content = "name,info\nPatient,Has memory issues\n"
        csv_file.write_text(csv_content)

        result = process_document(str(csv_file))

        assert result is not None
        assert result["file_name"] == "test.csv"
        assert result["file_type"] == "csv"
        assert result["num_chunks"] > 0
        assert len(result["chunks"]) > 0

    def test_process_unsupported_file(self, tmp_path):
        """Test handling unsupported file types."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Some text content")

        result = process_document(str(txt_file))
        assert result is None

    def test_process_empty_file(self, tmp_path):
        """Test handling empty files."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        result = process_document(str(csv_file))
        # Should return None for empty content
        assert result is None


class TestIntegration:
    """Integration tests for preprocessing pipeline."""

    def test_full_preprocessing_workflow(self, tmp_path):
        """Test the complete preprocessing workflow."""
        # Create test CSV file
        csv_file = tmp_path / "care_guide.csv"
        csv_content = """topic,description,tips
Memory Care,Helping patients with memory issues,Use visual cues and reminders
Communication,Effective communication strategies,Speak slowly and clearly
Behavioral Management,Handling challenging behaviors,Stay calm and redirect attention"""
        csv_file.write_text(csv_content)

        # Process the document
        result = process_document(str(csv_file))

        # Verify structure
        assert result is not None
        assert "file_name" in result
        assert "file_type" in result
        assert "chunks" in result
        assert "text_length" in result
        assert "num_chunks" in result

        # Verify content
        assert result["file_type"] == "csv"
        assert result["num_chunks"] > 0
        assert len(result["chunks"]) == result["num_chunks"]

        # Verify chunks contain expected content
        all_text = " ".join(result["chunks"])
        assert "Memory Care" in all_text
        assert "Communication" in all_text

    def test_chunking_preserves_content(self, tmp_path):
        """Test that chunking preserves all content."""
        # Create a CSV with known content
        csv_file = tmp_path / "test.csv"
        csv_content = "text\nThis is a test sentence.\nAnother test sentence here."
        csv_file.write_text(csv_content)

        result = process_document(str(csv_file))

        assert result is not None
        # All chunks combined should contain the original text
        all_chunks = " ".join(result["chunks"])
        assert "test sentence" in all_chunks
