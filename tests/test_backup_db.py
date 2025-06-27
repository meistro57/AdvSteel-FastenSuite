import os
import datetime
from pathlib import Path

import backup_db


def test_get_data_dir_env(monkeypatch):
    monkeypatch.setenv("ADVSTEEL_DATA_DIR", "/tmp/custom")
    assert backup_db.get_data_dir() == Path("/tmp/custom")


def test_backup_database(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "AstorBase.mdf").write_text("mdf")
    (data_dir / "AstorBase.ldf").write_text("ldf")

    class FixedDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2020, 1, 1, 12, 0, 0)

    monkeypatch.setattr(backup_db.datetime, "datetime", FixedDatetime)
    backup_path = backup_db.backup_database(data_dir=data_dir, out_dir=tmp_path)
    expected = tmp_path / f"{backup_db.ADVANCE_STEEL_VERSION}_20200101_120000"
    assert backup_path == expected
    assert (backup_path / "AstorBase.mdf").read_text() == "mdf"
    assert (backup_path / "AstorBase.ldf").read_text() == "ldf"
