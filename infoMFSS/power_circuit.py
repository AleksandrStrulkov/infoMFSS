from __future__ import annotations

import json
import logging
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)
MAX_SCHEMA_BYTES = 2 * 1024 * 1024
MINE_DIR_PATTERN = re.compile(r"mine_[1-9][0-9]*\Z")
FILENAME_PATTERN = re.compile(r"[^/\\.][^/\\]*\.json\Z")


@dataclass(frozen=True)
class SchemaEntry:
    """One available power-circuit schema in its approved directory."""

    id: str
    mine: str
    name: str


class SchemaUnavailableError(Exception):
    """The requested schema cannot safely be served."""


def _root() -> Path:
    return Path(settings.POWERCIRCUITSCHEMASDIR).resolve()


def _schema_path(mine_dir: str, filename: str) -> Path:
    if not MINE_DIR_PATTERN.fullmatch(mine_dir) or not FILENAME_PATTERN.fullmatch(filename):
        raise SchemaUnavailableError
    if ".." in filename:
        raise SchemaUnavailableError
    root = _root()
    candidate = root / mine_dir / filename
    try:
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root) or not candidate.is_file() or candidate.is_symlink():
            raise SchemaUnavailableError
        if candidate.parent.is_symlink():
            raise SchemaUnavailableError
    except (OSError, RuntimeError) as error:
        logger.warning("power_circuit_schema_path_unavailable", exc_info=error)
        raise SchemaUnavailableError from error
    return resolved


def read_schema(mine_dir: str, filename: str) -> dict[str, object]:
    """Read one bounded JSON object without accepting paths outside the configured root."""
    candidate = _schema_path(mine_dir, filename)
    try:
        descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as schema_file:
            metadata = os.fstat(schema_file.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_SCHEMA_BYTES:
                raise SchemaUnavailableError
            payload = schema_file.read(MAX_SCHEMA_BYTES + 1)
        if len(payload) > MAX_SCHEMA_BYTES:
            raise SchemaUnavailableError
        parsed: object = json.loads(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        logger.warning("power_circuit_schema_unreadable", exc_info=error)
        raise SchemaUnavailableError from error
    if not isinstance(parsed, dict):
        raise SchemaUnavailableError
    return parsed


def list_schemas() -> list[SchemaEntry]:
    """List valid, readable JSON objects in approved mine directories only."""
    root = _root()
    if not root.is_dir():
        return []
    entries: list[SchemaEntry] = []
    try:
        directories = sorted(root.iterdir(), key=lambda entry: entry.name)
        for directory in directories:
            if not MINE_DIR_PATTERN.fullmatch(directory.name) or not directory.is_dir() or directory.is_symlink():
                continue
            for candidate in sorted(directory.iterdir(), key=lambda entry: entry.name):
                try:
                    schema = read_schema(directory.name, candidate.name)
                except SchemaUnavailableError:
                    continue
                raw_mine = schema.get("mine")
                mine = raw_mine.strip() if isinstance(raw_mine, str) and raw_mine.strip() else directory.name
                entries.append(SchemaEntry(id=f"{directory.name}/{candidate.name}", mine=mine, name=candidate.stem))
    except OSError as error:
        logger.warning("power_circuit_catalog_unreadable", exc_info=error)
        return []
    return entries
