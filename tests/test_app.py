import json
import importlib
import pytest

import config
import app as app_module


def fake_connect_sql_server(database=config.DEFAULT_DATABASE):
    class MockCursor:
        def __init__(self):
            self.description = []
            self.results = []

        def execute(self, query):
            if "INFORMATION_SCHEMA.TABLES" in query:
                self.description = [("TABLE_NAME",)]
                self.results = [("MockTable",)]
            else:
                self.description = [("id",), ("name",)]
                self.results = [(1, "Alice"), (2, "Bob")]

        def fetchall(self):
            return self.results

    class MockConn:
        def close(self):
            pass

    return MockConn(), MockCursor()


def make_client(tmp_path, monkeypatch, read_only=True):
    monkeypatch.setattr(config, "READ_ONLY", read_only)
    monkeypatch.setattr(config, "SQL_DIRECT_MODE", False)
    importlib.reload(app_module)
    monkeypatch.setattr(app_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(app_module, "connect_sql_server", fake_connect_sql_server)

    sample_data = {"data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    file_path = tmp_path / "ASTORBASE__Sample.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    client = app_module.app.test_client()
    return client, file_path


@pytest.fixture
def client_ro(tmp_path, monkeypatch):
    return make_client(tmp_path, monkeypatch, read_only=True)


@pytest.fixture
def client_rw(tmp_path, monkeypatch):
    return make_client(tmp_path, monkeypatch, read_only=False)


def test_index_lists_files_and_read_only(client_ro):
    client, file_path = client_ro
    resp = client.get("/")
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert file_path.name in text
    assert "Read-only mode" in text


def test_view_table_displays_rows(client_ro):
    client, file_path = client_ro
    resp = client.get(f"/view/{file_path.name}")
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "Alice" in text


def test_search_endpoint(client_ro):
    client, file_path = client_ro
    resp = client.get(f"/search/{file_path.name}?q=Ali")
    assert resp.status_code == 200
    assert resp.get_json() == [{"id": 1, "name": "Alice"}]
    resp = client.get(f"/search/{file_path.name}?name=Bob")
    assert resp.get_json() == [{"id": 2, "name": "Bob"}]


def test_sql_routes_use_mock_db(client_ro):
    client, _ = client_ro
    resp = client.get("/sql")
    assert resp.status_code == 200
    assert "MockTable" in resp.get_data(as_text=True)
    resp = client.post("/sql/MockTable", data={"query": "SELECT * FROM MockTable"})
    assert resp.status_code == 200
    assert "Alice" in resp.get_data(as_text=True)


def test_save_route_disabled_in_read_only(client_ro):
    client, file_path = client_ro
    resp = client.post(f"/save/{file_path.name}", data={"json_data": "[]"})
    assert resp.status_code == 404


def test_save_updates_file_when_allowed(client_rw):
    client, file_path = client_rw
    new_rows = [{"id": 10}]
    resp = client.post(
        f"/save/{file_path.name}",
        data={"json_data": json.dumps(new_rows)},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["data"] == new_rows
