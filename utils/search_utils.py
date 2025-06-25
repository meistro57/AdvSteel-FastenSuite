"""Utility functions for filtering and searching data tables."""

from typing import Any, Dict, Iterable, List


def filter_data(
    rows: Iterable[Dict[str, Any]],
    case_insensitive: bool = False,
    partial: bool = False,
    **filters: Any,
) -> List[Dict[str, Any]]:
    """Return a list of rows that match all given key/value filters.

    Parameters
    ----------
    rows:
        Iterable of dictionaries representing table rows.
    case_insensitive:
        Perform case-insensitive comparison for string values.
    partial:
        Allow partial substring matches for string values.
    **filters:
        Key/value pairs to match. Equality is performed as strings for
        convenience. Numeric comparisons can be expressed using ``__gt``,
        ``__lt``, ``__gte`` and ``__lte`` suffixes.
    """

    result = []
    for row in rows:
        match = True
        for key, value in filters.items():
            # Handle comparison operators for numeric values
            if "__" in key:
                field, op = key.rsplit("__", 1)
                row_value = row.get(field)
                try:
                    row_num = float(row_value)
                    filter_num = float(value)
                except (TypeError, ValueError):
                    match = False
                    break

                if op == "gt" and not (row_num > filter_num):
                    match = False
                    break
                if op == "lt" and not (row_num < filter_num):
                    match = False
                    break
                if op == "gte" and not (row_num >= filter_num):
                    match = False
                    break
                if op == "lte" and not (row_num <= filter_num):
                    match = False
                    break
                continue

            row_value = row.get(key)
            if row_value is None:
                match = False
                break

            # Compare as strings for convenience
            row_str = str(row_value)
            filter_str = str(value)
            if case_insensitive:
                row_str = row_str.lower()
                filter_str = filter_str.lower()

            if partial:
                if filter_str not in row_str:
                    match = False
                    break
            else:
                if row_str != filter_str:
                    match = False
                    break

        if match:
            result.append(row)

    return result


def query_data(
    rows: Iterable[Dict[str, Any]],
    term: str,
) -> List[Dict[str, Any]]:
    """Return a list of rows containing the search term in any value."""
    term_lower = str(term).lower()
    result = []
    for row in rows:
        for value in row.values():
            if value is not None and term_lower in str(value).lower():
                result.append(row)
                break
    return result
