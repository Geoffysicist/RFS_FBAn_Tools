"""Directory setup utilities for operational workflows.

This module provides utilities for setting up directory structures from templates,
particularly useful for operational setups like fire season preparations.
"""

from pathlib import Path
from typing import List, Optional, Union, Callable
import shutil
import filecmp
import time

from .logging_utils import get_logger, log_function_call, log_operation_result

logger = get_logger(__name__)


def read_names_from_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> List[str]:
    """Read a list of names from a text file.
    
    Args:
        file_path: Path to the text file containing names (one per line)
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of names (empty lines and whitespace stripped)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Names file not found: {file_path}")
    
    logger.debug(f"Reading names from: {path}")
    
    with path.open('r', encoding=encoding) as file:
        names = [line.strip() for line in file.readlines() if line.strip()]
    
    logger.info(f"Read {len(names)} names from file")
    return names


def copy_directory_contents(
    source_dir: Union[str, Path],
    destination_dir: Union[str, Path],
    overwrite: bool = False,
    skip_existing: bool = True
) -> tuple[int, int]:
    """Copy contents of source directory to destination directory.
    
    Args:
        source_dir: Source directory to copy from
        destination_dir: Destination directory to copy to
        overwrite: If True, overwrite existing files/directories
        skip_existing: If True, skip existing items when overwrite=False
        
    Returns:
        Tuple of (copied_count, skipped_count)
        
    Raises:
        FileNotFoundError: If source directory doesn't exist
        PermissionError: If insufficient permissions
    """
    source_path = Path(source_dir)
    dest_path = Path(destination_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_dir}")
    
    # Ensure destination directory exists
    dest_path.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    for item in source_path.iterdir():
        dest_item = dest_path / item.name
        
        try:
            if item.is_dir():
                if dest_item.exists():
                    if overwrite:
                        logger.debug(f"Removing existing directory: {dest_item}")
                        shutil.rmtree(dest_item)
                        shutil.copytree(item, dest_item)
                        copied_count += 1
                    elif skip_existing:
                        logger.debug(f"Skipping existing directory: {dest_item}")
                        skipped_count += 1
                    else:
                        # Merge directories by recursively copying contents
                        sub_copied, sub_skipped = copy_directory_contents(
                            item, dest_item, overwrite, skip_existing
                        )
                        copied_count += sub_copied
                        skipped_count += sub_skipped
                else:
                    shutil.copytree(item, dest_item)
                    copied_count += 1
            else:  # Regular file
                if dest_item.exists():
                    if overwrite:
                        logger.debug(f"Overwriting existing file: {dest_item}")
                        shutil.copy2(item, dest_item)
                        copied_count += 1
                    elif skip_existing:
                        logger.debug(f"Skipping existing file: {dest_item}")
                        skipped_count += 1
                    else:
                        # Check if files are different before copying
                        if not filecmp.cmp(item, dest_item, shallow=False):
                            shutil.copy2(item, dest_item)
                            copied_count += 1
                        else:
                            skipped_count += 1
                else:
                    shutil.copy2(item, dest_item)
                    copied_count += 1
                    
        except Exception as e:
            logger.error(f"Error copying {item} to {dest_item}: {e}")
            raise
    
    return copied_count, skipped_count


def create_directories_from_template(
    base_directory: Union[str, Path],
    template_directory: Union[str, Path],
    directory_names: Union[List[str], str, Path],
    update_mode: str = 'skip',
    dry_run: bool = False,
    progress_callback: Optional[Callable[[str, int, int], None]] = None
) -> dict:
    """Create directories from a template for each name in the list.
    
    Args:
        base_directory: Base directory where new directories will be created
        template_directory: Template directory to copy contents from
        directory_names: List of directory names, or path to file containing names
        update_mode: How to handle existing directories ('skip', 'update', 'overwrite')
        dry_run: If True, only show what would be done without actually doing it
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Dictionary with operation statistics
        
    Raises:
        FileNotFoundError: If template directory or names file doesn't exist
        ValueError: If invalid update_mode specified
        
    Example:
        # From list of names
        stats = create_directories_from_template(
            base_directory='/path/to/base',
            template_directory='/path/to/template',
            directory_names=['LGA1', 'LGA2', 'LGA3'],
            update_mode='update'
        )
        
        # From file
        stats = create_directories_from_template(
            base_directory='/path/to/base',
            template_directory='/path/to/template',
            directory_names='lgas.txt',
            dry_run=True
        )
    """
    # Validate update mode
    valid_modes = ['skip', 'update', 'overwrite']
    if update_mode not in valid_modes:
        raise ValueError(f"Invalid update_mode '{update_mode}'. Must be one of: {valid_modes}")
    
    # Log function call
    log_function_call(
        logger, 
        "create_directories_from_template",
        base_directory=str(base_directory),
        template_directory=str(template_directory),
        update_mode=update_mode,
        dry_run=dry_run
    )
    
    # Convert paths
    base_path = Path(base_directory)
    template_path = Path(template_directory)
    
    # Validate template directory
    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found: {template_directory}")
    
    if not template_path.is_dir():
        raise ValueError(f"Template path is not a directory: {template_directory}")
    
    # Get directory names
    if isinstance(directory_names, (str, Path)):
        names = read_names_from_file(directory_names)
    else:
        names = directory_names
    
    if not names:
        logger.warning("No directory names provided")
        return {'total_names': 0, 'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    
    # Ensure base directory exists
    if not dry_run:
        base_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize statistics
    stats = {
        'total_names': len(names),
        'created': 0,
        'updated': 0, 
        'skipped': 0,
        'errors': 0,
        'total_files_copied': 0,
        'total_files_skipped': 0
    }
    
    logger.info(f"Processing {len(names)} directories with update_mode='{update_mode}'")
    
    # Process each directory name
    for i, name in enumerate(names):
        try:
            dir_path = base_path / name
            
            if progress_callback:
                progress_callback(name, i + 1, len(names))
            
            if dir_path.exists():
                if update_mode == 'skip':
                    logger.debug(f"Skipping existing directory: {name}")
                    stats['skipped'] += 1
                    continue
                elif update_mode == 'update':
                    if dry_run:
                        logger.info(f"DRY RUN: Would update directory: {name}")
                        stats['updated'] += 1
                    else:
                        logger.info(f"Updating directory: {name}")
                        copied, skipped = copy_directory_contents(
                            template_path, dir_path, 
                            overwrite=False, skip_existing=True
                        )
                        stats['updated'] += 1
                        stats['total_files_copied'] += copied
                        stats['total_files_skipped'] += skipped
                elif update_mode == 'overwrite':
                    if dry_run:
                        logger.info(f"DRY RUN: Would overwrite directory: {name}")
                        stats['updated'] += 1
                    else:
                        logger.info(f"Overwriting directory: {name}")
                        shutil.rmtree(dir_path)
                        dir_path.mkdir()
                        copied, skipped = copy_directory_contents(
                            template_path, dir_path,
                            overwrite=True, skip_existing=False
                        )
                        stats['updated'] += 1
                        stats['total_files_copied'] += copied
            else:
                if dry_run:
                    logger.info(f"DRY RUN: Would create directory: {name}")
                    stats['created'] += 1
                else:
                    logger.info(f"Creating directory: {name}")
                    dir_path.mkdir()
                    copied, skipped = copy_directory_contents(
                        template_path, dir_path,
                        overwrite=False, skip_existing=False
                    )
                    stats['created'] += 1
                    stats['total_files_copied'] += copied
                    
        except Exception as e:
            logger.error(f"Error processing directory '{name}': {e}")
            stats['errors'] += 1
    
    # Log operation result
    success = stats['errors'] == 0
    details = f"created={stats['created']}, updated={stats['updated']}, skipped={stats['skipped']}, errors={stats['errors']}"
    
    log_operation_result(
        logger,
        "directory template setup",
        success=success,
        details=details,
        count=stats['total_names']
    )
    
    return stats


def print_progress(name: str, current: int, total: int) -> None:
    """Simple progress callback function.
    
    Args:
        name: Current item name being processed
        current: Current item number (1-based)
        total: Total number of items
    """
    percentage = (current / total) * 100
    print(f"[{current:3d}/{total:3d}] ({percentage:5.1f}%) Processing: {name}")