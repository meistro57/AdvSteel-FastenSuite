import json
from utils.json_handler import load_json, save_json


def test_load_save_round_trip(tmp_path):
    data = {"foo": 123, "bar": [1, 2, 3]}
    json_string = json.dumps(data)
    file_path = tmp_path / "sample.json"

    save_json(file_path, json_string)
    loaded = load_json(file_path)

    assert loaded == data
