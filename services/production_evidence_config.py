from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvidenceConfigStatus:
    channel: str
    configured: bool
    loaded: bool
    record_count: int = 0
    source_count: int = 0
    error: str | None = None
    configuration_origin: str | None = None


def _read_payload(*, json_env: str, path_env: str) -> tuple[Any | None, str | None]:
    inline = os.getenv(json_env, "").strip()
    if inline:
        return json.loads(inline), f"env:{json_env}"

    path_value = os.getenv(path_env, "").strip()
    if path_value:
        path = Path(path_value).expanduser()
        if not path.is_file():
            raise ValueError(f"Configured evidence path does not exist or is not a file: {path}")
        return json.loads(path.read_text(encoding="utf-8")), f"path:{path}"

    return None, None


def load_channel_payload(channel: str) -> tuple[Any | None, EvidenceConfigStatus]:
    normalized = channel.strip().upper()
    json_env = f"{normalized}_EVIDENCE_JSON"
    path_env = f"{normalized}_EVIDENCE_PATH"

    try:
        payload, origin = _read_payload(json_env=json_env, path_env=path_env)
    except Exception as exc:
        return None, EvidenceConfigStatus(
            channel=channel.lower(),
            configured=True,
            loaded=False,
            error=f"{type(exc).__name__}: {exc}",
            configuration_origin=f"{json_env}|{path_env}",
        )

    if payload is None:
        return None, EvidenceConfigStatus(
            channel=channel.lower(),
            configured=False,
            loaded=False,
        )

    return payload, EvidenceConfigStatus(
        channel=channel.lower(),
        configured=True,
        loaded=False,
        configuration_origin=origin,
    )


def bool_env(name: str, *, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
