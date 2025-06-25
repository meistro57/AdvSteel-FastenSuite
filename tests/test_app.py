import json
import importlib
import pytest

import config
import app as app_module

TABLE_ROWS = [(1, "Alice"), (2, "Bob")]


def fake_connect_sql_server(database=config.DEFAULT_DATABASE):
    class MockCursor:
        def __init__(self):
            self.description = []
            self.results = []

        def execute(self, query, params=None):
            if "INFORMATION_SCHEMA.TABLES" in query:
                self.description = [("TABLE_NAME",)]
                self.results = [("MockTable",)]
            elif query.startswith("SELECT *"):
                self.description = [("id",), ("name",)]
                self.results = TABLE_ROWS
            elif query.startswith("DELETE"):
                TABLE_ROWS.clear()
                self.description = []
                self.results = []
            elif query.startswith("INSERT"):
                TABLE_ROWS.append(tuple(params))

        def fetchall(self):
            return self.results

    class MockConn:
        def close(self):
            pass

    return MockConn(), MockCursor()


def make_client(monkeypatch, read_only=True):
    monkeypatch.setattr(config, "READ_ONLY", read_only)
    importlib.reload(app_module)
    monkeypatch.setattr(app_module, "connect_sql_server", fake_connect_sql_server)

    client = app_module.app.test_client()
    return client, "ASTORBASE__MockTable.json"


@pytest.fixture
def client_ro(monkeypatch):
    return make_client(monkeypatch, read_only=True)


@pytest.fixture
def client_rw(monkeypatch):
    return make_client(monkeypatch, read_only=False)


def test_index_lists_files_and_read_only(client_ro):
    client, file_name = client_ro
    resp = client.get("/")
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert file_name in text
    assert "Read-only mode" in text


def test_view_table_displays_rows(client_ro):
    client, file_name = client_ro
    resp = client.get(f"/view/{file_name}")
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "Alice" in text


def test_search_endpoint(client_ro):
    client, file_name = client_ro
    resp = client.get(f"/search/{file_name}?q=Ali")
    assert resp.status_code == 200
    assert resp.get_json() == [{"id": 1, "name": "Alice"}]
    resp = client.get(f"/search/{file_name}?name=Bob")
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
    client, file_name = client_ro
    resp = client.post(f"/save/{file_name}", data={"json_data": "[]"})
    assert resp.status_code == 404


def test_save_updates_table_when_allowed(client_rw):
    client, file_name = client_rw
    new_rows = [{"id": 10, "name": "Test"}]
    resp = client.post(
        f"/save/{file_name}",
        data={"json_data": json.dumps(new_rows)},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    resp = client.get(f"/view/{file_name}")
    assert "Test" in resp.get_data(as_text=True)
