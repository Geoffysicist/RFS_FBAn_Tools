"""Test configuration and fixtures for the test suite."""

import pytest
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.
    
    Yields:
        Path object for the temporary directory
    """
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)