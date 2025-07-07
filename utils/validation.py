# utils/validation.py
"""Helpers for validating table rows before saving to SQL."""
from typing import Iterable, Dict, Any, Sequence


def validate_rows(rows: Iterable[Dict[str, Any]], reference_keys: Sequence[str] | None = None) -> None:
    """Validate rows ensuring consistent keys across all records.

    Parameters
    ----------
    rows:
        Iterable of row dictionaries.
    reference_keys:
        Optional sequence of keys that each row must contain. If not provided
        the keys from the first row are used.

    Raises
    ------
    ValueError
        If any row has missing or extra keys compared to ``reference_keys``.
    """
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration:
        return

    keys = set(reference_keys or first.keys())
    if reference_keys is None:
        reference_keys = list(keys)

    def check(row: Dict[str, Any]) -> None:
        row_keys = set(row.keys())
        if row_keys != keys:
            missing = keys - row_keys
            extra = row_keys - keys
            msg = []
            if missing:
                msg.append(f"missing keys: {sorted(missing)}")
            if extra:
                msg.append(f"extra keys: {sorted(extra)}")
            raise ValueError("; ".join(msg))

    check(first)
    for r in iterator:
        check(r)
