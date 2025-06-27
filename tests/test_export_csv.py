import csv
from pathlib import Path
from export_csv import export_table_to_csv


def fake_connect_sql_server(database):
    class Cur:
        def __init__(self):
            self.description = [("id",), ("name",)]
        def execute(self, query):
            pass
        def fetchall(self):
            return [(1, "A"), (2, "B")]
    class Conn:
        def close(self):
            pass
    return Conn(), Cur()


def test_export_table_to_csv(tmp_path, monkeypatch):
    monkeypatch.setattr("export_csv.connect_sql_server", fake_connect_sql_server)
    out = tmp_path / "rows.csv"
    export_table_to_csv("DB", "Table", out)
    content = out.read_text().splitlines()
    assert content[0] == "id,name"
    assert content[1] == "1,A"

