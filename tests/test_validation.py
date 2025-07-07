from utils.validation import validate_rows
import pytest


def test_validate_rows_passes_when_keys_match():
    rows = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    validate_rows(rows)


def test_validate_rows_raises_on_mismatch():
    rows = [{"id": 1, "name": "A"}, {"id": 2, "nom": "B"}]
    with pytest.raises(ValueError):
        validate_rows(rows)

