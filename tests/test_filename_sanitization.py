import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import load_table_data, save_table_data


def test_load_table_data_blocks_parent_path():
    with pytest.raises(ValueError):
        load_table_data("../secret.json")


def test_save_table_data_blocks_parent_path():
    with pytest.raises(ValueError):
        save_table_data("../secret.json", "[]")
