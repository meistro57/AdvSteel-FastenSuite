"""Utility functions for filtering and searching data tables."""

from typing import Any, Dict, Iterable, List


def filter_data(rows: Iterable[Dict[str, Any]], **filters: Any) -> List[Dict[str, Any]]:
    """Return a list of rows that match all given key/value filters.

    Parameters
    ----------
    rows:
        Iterable of dictionaries representing table rows.
    **filters:
        Key/value pairs to match exactly. Comparison is performed as strings
        for convenience.
    """
    result = []
    for row in rows:
        match = True
        for key, value in filters.items():
            if str(row.get(key)) != str(value):
                match = False
                break
        if match:
            result.append(row)
    return result


def query_data(rows: Iterable[Dict[str, Any]], term: str) -> List[Dict[str, Any]]:
    """Return a list of rows containing the search term in any value."""
    term_lower = str(term).lower()
    result = []
    for row in rows:
        for value in row.values():
            if value is not None and term_lower in str(value).lower():
                result.append(row)
                break
    return result
