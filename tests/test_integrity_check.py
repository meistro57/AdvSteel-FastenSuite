from integrity_check import check_bolt_integrity


def fake_connect_sql_server(database):
    class Cur:
        def __init__(self):
            self.state = 0
        def execute(self, query):
            if "BoltDefinition" in query:
                self.state = 1
            else:
                self.state = 2
        def fetchall(self):
            if self.state == 1:
                return [(1,), (2,)]
            else:
                return [(1,), (3,)]
    class Conn:
        def close(self):
            pass
    return Conn(), Cur()


def test_check_bolt_integrity(monkeypatch):
    monkeypatch.setattr("integrity_check.connect_sql_server", fake_connect_sql_server)
    missing = check_bolt_integrity()
    assert missing == [3]

