"""RFS FBAn Tools package.

A collection of tools and utilities for file management and analysis.
"""

__version__ = "0.1.0"

# Import main utilities for easy access
from .file_utils import delete_files_by_suffix
from .logging_utils import setup_logging, get_logger
from .directory_utils import create_directories_from_template, read_names_from_file

__all__ = [
    "delete_files_by_suffix",
    "setup_logging", 
    "get_logger",
    "create_directories_from_template",
    "read_names_from_file"
]