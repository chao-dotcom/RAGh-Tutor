"""Validation utilities"""
from typing import List, Optional


def validate_query(query: str, min_length: int = 3, max_length: int = 1000) -> bool:
    """Validate query"""
    if not query or not isinstance(query, str):
        return False
    if len(query.strip()) < min_length:
        return False
    if len(query) > max_length:
        return False
    return True


def validate_top_k(top_k: int, max_k: int = 100) -> bool:
    """Validate top_k parameter"""
    return isinstance(top_k, int) and 1 <= top_k <= max_k

