"""Unit tests for directory_utils module."""

import pytest
import tempfile
from pathlib import Path
import sys

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fban_tools.directory_utils import (
    read_names_from_file,
    copy_directory_contents,
    create_directories_from_template,
    print_progress
)


class TestReadNamesFromFile:
    """Test cases for read_names_from_file function."""
    
    def test_read_simple_file(self, temp_dir: Path):
        """Test reading a simple names file."""
        names_file = temp_dir / "names.txt"
        names_file.write_text("LGA1\nLGA2\nLGA3\n")
        
        names = read_names_from_file(names_file)
        
        assert names == ["LGA1", "LGA2", "LGA3"]
    
    def test_read_file_with_empty_lines(self, temp_dir: Path):
        """Test reading file with empty lines and whitespace."""
        names_file = temp_dir / "names.txt"
        names_file.write_text("LGA1\n\n  LGA2  \n\nLGA3\n  \n")
        
        names = read_names_from_file(names_file)
        
        assert names == ["LGA1", "LGA2", "LGA3"]
    
    def test_read_nonexistent_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            read_names_from_file("nonexistent.txt")
    
    def test_read_empty_file(self, temp_dir: Path):
        """Test reading an empty file."""
        names_file = temp_dir / "empty.txt"
        names_file.write_text("")
        
        names = read_names_from_file(names_file)
        
        assert names == []


class TestCopyDirectoryContents:
    """Test cases for copy_directory_contents function."""
    
    def test_copy_simple_contents(self, temp_dir: Path):
        """Test copying simple directory contents."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "dest"
        
        # Create source structure
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        subdir = source_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")
        
        copied, skipped = copy_directory_contents(source_dir, dest_dir)
        
        assert copied == 3  # 2 files + 1 directory
        assert skipped == 0
        assert (dest_dir / "file1.txt").read_text() == "content1"
        assert (dest_dir / "file2.txt").read_text() == "content2"
        assert (dest_dir / "subdir" / "file3.txt").read_text() == "content3"
    
    def test_copy_with_existing_files_skip(self, temp_dir: Path):
        """Test copying with existing files using skip mode."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "dest"
        
        # Create source and destination
        source_dir.mkdir()
        dest_dir.mkdir()
        
        (source_dir / "file1.txt").write_text("new content")
        (dest_dir / "file1.txt").write_text("old content")
        (source_dir / "file2.txt").write_text("content2")
        
        copied, skipped = copy_directory_contents(
            source_dir, dest_dir, 
            overwrite=False, skip_existing=True
        )
        
        assert copied == 1  # Only file2.txt
        assert skipped == 1  # file1.txt was skipped
        assert (dest_dir / "file1.txt").read_text() == "old content"
        assert (dest_dir / "file2.txt").read_text() == "content2"
    
    def test_copy_with_overwrite(self, temp_dir: Path):
        """Test copying with overwrite enabled."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "dest"
        
        # Create source and destination
        source_dir.mkdir()
        dest_dir.mkdir()
        
        (source_dir / "file1.txt").write_text("new content")
        (dest_dir / "file1.txt").write_text("old content")
        
        copied, skipped = copy_directory_contents(
            source_dir, dest_dir, 
            overwrite=True, skip_existing=False
        )
        
        assert copied == 1
        assert skipped == 0
        assert (dest_dir / "file1.txt").read_text() == "new content"
    
    def test_copy_nonexistent_source(self, temp_dir: Path):
        """Test error when source directory doesn't exist."""
        dest_dir = temp_dir / "dest"
        
        with pytest.raises(FileNotFoundError):
            copy_directory_contents("nonexistent", dest_dir)
    
    def test_copy_creates_destination(self, temp_dir: Path):
        """Test that destination directory is created if it doesn't exist."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "nested" / "dest"
        
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content")
        
        copied, skipped = copy_directory_contents(source_dir, dest_dir)
        
        assert dest_dir.exists()
        assert (dest_dir / "file1.txt").exists()


class TestCreateDirectoriesFromTemplate:
    """Test cases for create_directories_from_template function."""
    
    def test_create_from_list(self, temp_dir: Path):
        """Test creating directories from a list of names."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        template_subdir = template_dir / "template_subdir"
        template_subdir.mkdir()
        (template_subdir / "nested_file.txt").write_text("nested content")
        
        names = ["LGA1", "LGA2", "LGA3"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="skip"
        )
        
        assert stats['created'] == 3
        assert stats['skipped'] == 0
        assert stats['errors'] == 0
        
        # Verify directories were created with template contents
        for name in names:
            lga_dir = base_dir / name
            assert lga_dir.exists()
            assert (lga_dir / "template_file.txt").read_text() == "template content"
            assert (lga_dir / "template_subdir" / "nested_file.txt").read_text() == "nested content"
    
    def test_create_from_file(self, temp_dir: Path):
        """Test creating directories from a names file."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        names_file = temp_dir / "names.txt"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        
        # Create names file
        names_file.write_text("LGA1\nLGA2\nLGA3\n")
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names_file,
            update_mode="skip"
        )
        
        assert stats['created'] == 3
        assert (base_dir / "LGA1" / "template_file.txt").exists()
        assert (base_dir / "LGA2" / "template_file.txt").exists()
        assert (base_dir / "LGA3" / "template_file.txt").exists()
    
    def test_update_mode_skip(self, temp_dir: Path):
        """Test skip mode with existing directories."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        
        # Create existing directory
        base_dir.mkdir()
        existing_dir = base_dir / "LGA1"
        existing_dir.mkdir()
        (existing_dir / "existing_file.txt").write_text("existing content")
        
        names = ["LGA1", "LGA2"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="skip"
        )
        
        assert stats['created'] == 1  # Only LGA2
        assert stats['skipped'] == 1  # LGA1 was skipped
        
        # Verify existing directory was not modified
        assert (existing_dir / "existing_file.txt").exists()
        assert not (existing_dir / "template_file.txt").exists()
    
    def test_update_mode_update(self, temp_dir: Path):
        """Test update mode with existing directories."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        (template_dir / "new_file.txt").write_text("new content")
        
        # Create existing directory
        base_dir.mkdir()
        existing_dir = base_dir / "LGA1"
        existing_dir.mkdir()
        (existing_dir / "existing_file.txt").write_text("existing content")
        (existing_dir / "template_file.txt").write_text("old template content")
        
        names = ["LGA1"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="update"
        )
        
        assert stats['updated'] == 1
        
        # Verify directory was updated (new files added, existing preserved)
        assert (existing_dir / "existing_file.txt").exists()
        assert (existing_dir / "template_file.txt").read_text() == "old template content"  # Not overwritten
        assert (existing_dir / "new_file.txt").read_text() == "new content"  # Added
    
    def test_update_mode_overwrite(self, temp_dir: Path):
        """Test overwrite mode with existing directories."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        
        # Create existing directory
        base_dir.mkdir()
        existing_dir = base_dir / "LGA1"
        existing_dir.mkdir()
        (existing_dir / "existing_file.txt").write_text("existing content")
        
        names = ["LGA1"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="overwrite"
        )
        
        assert stats['updated'] == 1
        
        # Verify directory was completely replaced
        assert not (existing_dir / "existing_file.txt").exists()
        assert (existing_dir / "template_file.txt").read_text() == "template content"
    
    def test_update_mode_merge(self, temp_dir: Path):
        """Test merge mode overwrites template files but keeps other files."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template with two files
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("new template content")
        (template_dir / "shared_file.txt").write_text("template shared content")
        
        # Create existing directory with overlapping and unique files
        base_dir.mkdir()
        existing_dir = base_dir / "LGA1"
        existing_dir.mkdir()
        (existing_dir / "template_file.txt").write_text("old template content")  # Will be overwritten
        (existing_dir / "shared_file.txt").write_text("old shared content")     # Will be overwritten
        (existing_dir / "unique_file.txt").write_text("unique content")         # Will be kept
        
        names = ["LGA1"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="merge"
        )
        
        assert stats['updated'] == 1
        
        # Verify template files were overwritten
        assert (existing_dir / "template_file.txt").read_text() == "new template content"
        assert (existing_dir / "shared_file.txt").read_text() == "template shared content"
        # Verify unique files were preserved
        assert (existing_dir / "unique_file.txt").read_text() == "unique content"
    
    def test_dry_run_mode(self, temp_dir: Path):
        """Test dry run mode doesn't create actual directories."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "template_file.txt").write_text("template content")
        
        names = ["LGA1", "LGA2"]
        
        stats = create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            update_mode="skip",
            dry_run=True
        )
        
        assert stats['created'] == 2
        
        # Verify no actual directories were created
        assert not (base_dir / "LGA1").exists()
        assert not (base_dir / "LGA2").exists()
    
    def test_invalid_update_mode(self, temp_dir: Path):
        """Test error with invalid update mode."""
        with pytest.raises(ValueError, match="Invalid update_mode"):
            create_directories_from_template(
                base_directory=temp_dir,
                template_directory=temp_dir,
                directory_names=["test"],
                update_mode="invalid"
            )
    
    def test_nonexistent_template(self, temp_dir: Path):
        """Test error when template directory doesn't exist."""
        with pytest.raises(FileNotFoundError):
            create_directories_from_template(
                base_directory=temp_dir,
                template_directory="nonexistent",
                directory_names=["test"]
            )
    
    def test_progress_callback(self, temp_dir: Path):
        """Test that progress callback is called."""
        base_dir = temp_dir / "base"
        template_dir = temp_dir / "template"
        
        # Create template
        template_dir.mkdir()
        (template_dir / "file.txt").write_text("content")
        
        # Track progress calls
        progress_calls = []
        
        def track_progress(name, current, total):
            progress_calls.append((name, current, total))
        
        names = ["LGA1", "LGA2"]
        
        create_directories_from_template(
            base_directory=base_dir,
            template_directory=template_dir,
            directory_names=names,
            progress_callback=track_progress
        )
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == ("LGA1", 1, 2)
        assert progress_calls[1] == ("LGA2", 2, 2)


class TestPrintProgress:
    """Test cases for print_progress function."""
    
    def test_print_progress(self, capsys):
        """Test print_progress function output."""
        print_progress("TestLGA", 1, 5)
        
        captured = capsys.readouterr()
        assert "TestLGA" in captured.out
        assert "[  1/  5]" in captured.out
        assert "20.0%" in captured.out