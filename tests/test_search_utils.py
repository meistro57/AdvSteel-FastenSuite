import pytest

from utils.search_utils import filter_data, query_data


sample_rows = [
    {"id": 1, "name": "Bolt", "size": "M10"},
    {"id": 2, "name": "Nut", "size": "M12"},
    {"id": 3, "name": "Washer", "size": "M10"},
]


def test_filter_data_single_match():
    result = filter_data(sample_rows, id=1)
    assert result == [{"id": 1, "name": "Bolt", "size": "M10"}]


def test_filter_data_multiple_criteria():
    result = filter_data(sample_rows, size="M10", name="Washer")
    assert result == [{"id": 3, "name": "Washer", "size": "M10"}]


def test_filter_data_no_match():
    result = filter_data(sample_rows, name="Screw")
    assert result == []


def test_query_data_finds_term_case_insensitive():
    result = query_data(sample_rows, "nu")
    assert result == [{"id": 2, "name": "Nut", "size": "M12"}]


def test_query_data_returns_multiple_rows():
    result = query_data(sample_rows, "m10")
    assert result == [
        {"id": 1, "name": "Bolt", "size": "M10"},
        {"id": 3, "name": "Washer", "size": "M10"},
    ]

