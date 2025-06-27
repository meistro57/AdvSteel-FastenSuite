import os
from pathlib import Path
import shutil
import datetime

from config import ADVANCE_STEEL_VERSION

DEFAULT_DATA_DIR = Path(
    f"C:/ProgramData/Autodesk/Advance Steel {ADVANCE_STEEL_VERSION}/USA/Steel/Data"
)


def get_data_dir() -> Path:
    """Return the Advance Steel data directory."""
    return Path(os.environ.get("ADVSTEEL_DATA_DIR", DEFAULT_DATA_DIR))


def backup_database(data_dir: Path | None = None, out_dir: str | Path = "backups") -> Path:
    """Backup AstorBase MDF and LDF files to a timestamped folder.

    Parameters
    ----------
    data_dir:
        Directory containing AstorBase.mdf and AstorBase.ldf. If None, uses
        ``get_data_dir()``.
    out_dir:
        Directory where backups are created.

    Returns
    -------
    Path
        Path to the created backup directory.
    """
    data_dir = Path(data_dir) if data_dir else get_data_dir()
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(out_dir) / f"{ADVANCE_STEEL_VERSION}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    for name in ["AstorBase.mdf", "AstorBase.ldf"]:
        src = data_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
        else:
            print(f"Warning: {src} not found")

    return backup_dir


if __name__ == "__main__":
    path = backup_database()
    print(f"Backup created at: {path}")
