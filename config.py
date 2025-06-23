# config.py
"""Configuration for connecting to Advance Steel local databases."""

# Supported Advance Steel versions. Select the one installed on this machine.
ADVANCE_STEEL_VERSION = 2025  # choose from 2026, 2025, 2024, or 2023

SUPPORTED_VERSIONS = {2026, 2025, 2024, 2023}

if ADVANCE_STEEL_VERSION not in SUPPORTED_VERSIONS:
    raise ValueError(
        f"Unsupported Advance Steel version: {ADVANCE_STEEL_VERSION}. "
        f"Supported versions are: {sorted(SUPPORTED_VERSIONS)}"
    )

DB_CONFIG = {
    'server': rf'(LocalDB)\ADVANCESTEEL{ADVANCE_STEEL_VERSION}',
    'trusted_connection': 'yes',
    'driver': 'ODBC Driver 17 for SQL Server'
}

# Default database used by the web SQL interface
DEFAULT_DATABASE = 'ASTORBASE'

# Enable development read-only mode. When True, editing routes are disabled
# and the UI will not allow saving changes.
READ_ONLY = True
