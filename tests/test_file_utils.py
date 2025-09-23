"""Unit tests for file_utils module."""

import pytest
from pathlib import Path
import sys

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.file_utils import delete_files_by_suffix


class TestDeleteFilesBySuffix:
    """Test cases for the delete_files_by_suffix function."""
    
    def test_delete_files_basic(self, temp_dir: Path):
        """Test basic file deletion functionality."""
        # Create test files
        (temp_dir / "file1.tmp").write_text("temp file 1")
        (temp_dir / "file2.tmp").write_text("temp file 2")
        (temp_dir / "file3.txt").write_text("text file")
        
        # Delete .tmp files
        deleted_files = delete_files_by_suffix(temp_dir, ".tmp")
        
        # Verify results
        assert len(deleted_files) == 2
        assert not (temp_dir / "file1.tmp").exists()
        assert not (temp_dir / "file2.tmp").exists()
        assert (temp_dir / "file3.txt").exists()  # Should not be deleted
    
    def test_delete_files_recursive(self, temp_dir: Path):
        """Test recursive deletion in subdirectories."""
        # Create nested structure
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()
        nested_dir = sub_dir / "nested"
        nested_dir.mkdir()
        
        # Create test files at different levels
        (temp_dir / "root.log").write_text("root log")
        (sub_dir / "sub.log").write_text("sub log")
        (nested_dir / "nested.log").write_text("nested log")
        (temp_dir / "keep.txt").write_text("keep this")
        
        # Delete .log files recursively
        deleted_files = delete_files_by_suffix(temp_dir, ".log")
        
        # Verify all .log files were deleted
        assert len(deleted_files) == 3
        assert not (temp_dir / "root.log").exists()
        assert not (sub_dir / "sub.log").exists()
        assert not (nested_dir / "nested.log").exists()
        assert (temp_dir / "keep.txt").exists()
    
    def test_delete_files_suffix_without_dot(self, temp_dir: Path):
        """Test that suffix without leading dot is handled correctly."""
        # Create test files
        (temp_dir / "file.bak").write_text("backup")
        (temp_dir / "file.txt").write_text("text")
        
        # Delete using suffix without dot
        deleted_files = delete_files_by_suffix(temp_dir, "bak")
        
        assert len(deleted_files) == 1
        assert not (temp_dir / "file.bak").exists()
        assert (temp_dir / "file.txt").exists()
    
    def test_dry_run_mode(self, temp_dir: Path):
        """Test dry run mode doesn't actually delete files."""
        # Create test files
        (temp_dir / "file1.tmp").write_text("temp file 1")
        (temp_dir / "file2.tmp").write_text("temp file 2")
        
        # Run in dry-run mode
        files_to_delete = delete_files_by_suffix(temp_dir, ".tmp", dry_run=True)
        
        # Verify files were identified but not deleted
        assert len(files_to_delete) == 2
        assert (temp_dir / "file1.tmp").exists()
        assert (temp_dir / "file2.tmp").exists()
    
    def test_no_matching_files(self, temp_dir: Path):
        """Test behavior when no files match the suffix."""
        # Create files with different suffixes
        (temp_dir / "file.txt").write_text("text")
        (temp_dir / "file.doc").write_text("document")
        
        # Try to delete files with non-existent suffix
        deleted_files = delete_files_by_suffix(temp_dir, ".xyz")
        
        assert len(deleted_files) == 0
    
    def test_nonexistent_directory(self):
        """Test error handling for non-existent directory."""
        with pytest.raises(FileNotFoundError):
            delete_files_by_suffix("/nonexistent/path", ".tmp")
    
    def test_file_instead_of_directory(self, temp_dir: Path):
        """Test error handling when path is a file, not directory."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        with pytest.raises(ValueError):
            delete_files_by_suffix(test_file, ".tmp")
    
    def test_empty_directory(self, temp_dir: Path):
        """Test behavior with empty directory."""
        deleted_files = delete_files_by_suffix(temp_dir, ".tmp")
        assert len(deleted_files) == 0