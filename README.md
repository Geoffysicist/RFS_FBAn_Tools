# RFS FBAn Tools

A collection of file management tools and CLI scripts with comprehensive logging for operational workflows.

## Current Tools

### File Deletion Utility

Recursively searches a directory for files with a specified suffix and deletes them.

**Module:** `fban_tools.file_utils.delete_files_by_suffix()`

**CLI Script:** `cli_scripts/delete_files.py`

#### Usage

```python
from fban_tools.file_utils import delete_files_by_suffix

# Delete all .tmp files in a directory
deleted_files = delete_files_by_suffix('/path/to/search', '.tmp')

# Preview what would be deleted (dry run)
files_to_delete = delete_files_by_suffix('/path/to/search', '.log', dry_run=True)
```

#### CLI Usage

```bash
# Delete all .tmp files
python cli_scripts/delete_files.py /path/to/search .tmp

# Preview what would be deleted
python cli_scripts/delete_files.py /path/to/search .log --dry-run

# Verbose output with file logging disabled
python cli_scripts/delete_files.py /path/to/search .bak --verbose --no-log-file
```

### Directory Setup Utility

Creates directories from templates for operational setups like fire seasons. Reads directory names from a file and copies template contents to each directory.

**Module:** `fban_tools.directory_utils.create_directories_from_template()`

**CLI Script:** `cli_scripts/setup_directories.py`

#### Features

- Create directories from template with customizable update modes
- Read directory names from text files or use lists
- Multiple update modes: skip, update, or overwrite existing directories
- Dry-run capability to preview operations
- Progress tracking for large operations
- Comprehensive error handling and logging

#### Usage

```python
from fban_tools.directory_utils import create_directories_from_template

# Create directories from a list
stats = create_directories_from_template(
    base_directory='/path/to/base',
    template_directory='/path/to/template', 
    directory_names=['LGA1', 'LGA2', 'LGA3'],
    update_mode='update'
)

# Create from names file
stats = create_directories_from_template(
    base_directory='/path/to/base',
    template_directory='/path/to/template',
    directory_names='examples/LGAs.txt',
    update_mode='skip',
    dry_run=True
)
```

#### CLI Usage

```bash
# Basic fire season setup
python cli_scripts/setup_directories.py "O:/Operations/2425Fires/Fire Mapping" "O:/Templates/District_Template" examples/LGAs.txt

# Update existing directories with new template content
python cli_scripts/setup_directories.py base_dir template_dir LGAs.txt --update-mode update

# Preview what would be done
python cli_scripts/setup_directories.py base_dir template_dir LGAs.txt --dry-run

# Verbose output with progress
python cli_scripts/setup_directories.py base_dir template_dir LGAs.txt --verbose
```

#### Update Modes

- **skip** (default): Skip existing directories, only create new ones
- **update**: Add new files from template to existing directories, preserve existing files
- **overwrite**: Completely replace existing directories with template contents

### Logging Utilities

Provides standardized logging to both console and YAML-formatted log files with date-based filenames.

**Module:** `fban_tools.logging_utils`

**Demo Script:** `cli_scripts/demo_logging.py`

#### Features

- Logs to both console and file by default
- YAML-formatted log files with structured data
- Date-based log file naming (log_YYYYMMDD.yaml)
- Different log levels for console vs file output
- Helper functions for logging function calls and operation results

#### Usage

```python
from fban_tools.logging_utils import setup_logging, get_logger

# Basic setup
logger = setup_logging()
logger.info("This goes to both console and file")

# Custom configuration
logger = setup_logging(
    log_to_file=True,
    log_directory="my_logs",
    console_level="WARNING",
    file_level="DEBUG"
)

# Get a named logger (after setup_logging has been called)
module_logger = get_logger(__name__)
```

#### Demo Script

```bash
# Run logging demo
python cli_scripts/demo_logging.py

# Verbose console output, no file logging
python cli_scripts/demo_logging.py --verbose --no-log-file

# Custom log directory
python cli_scripts/demo_logging.py --log-dir custom_logs
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```
RFS_FBAn_Tools/
├── cli_scripts/              # Command-line interface scripts
│   ├── delete_files.py       # File deletion utility
│   ├── setup_directories.py  # Directory setup from templates
│   └── demo_logging.py       # Logging demo script
├── fban_tools/              # Core tools and utilities package
│   ├── file_utils.py        # File management utilities
│   ├── directory_utils.py   # Directory setup utilities  
│   └── logging_utils.py     # Logging utilities
├── tests/                   # Unit tests using pytest
├── examples/                # Example files
│   └── LGAs.txt            # Sample Local Government Areas list
├── logs/                    # Default log file directory (created when needed)
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Examples

### Fire Season Setup

```bash
# Set up fire season directories for all Victorian LGAs
python cli_scripts/setup_directories.py \
    "O:/Operations/2425Fires/Fire Mapping" \
    "O:/Templates/District_Template" \
    examples/LGAs.txt \
    --update-mode update \
    --verbose

# Preview the setup without making changes
python cli_scripts/setup_directories.py \
    "O:/Operations/2425Fires/Fire Mapping" \
    "O:/Templates/District_Template" \
    examples/LGAs.txt \
    --dry-run
```