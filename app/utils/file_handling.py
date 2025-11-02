"""File handling utilities"""
from pathlib import Path
import os


def ensure_directory(path: str):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)


def is_valid_file(file_path: str, max_size: int = 50 * 1024 * 1024) -> bool:
    """Check if file is valid"""
    if not os.path.exists(file_path):
        return False
    if get_file_size(file_path) > max_size:
        return False
    return True

