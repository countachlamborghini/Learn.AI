from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


DATA_DIR = Path(os.getenv("API_DATA_DIR", "/workspace/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_FILE = DATA_DIR / "events.jsonl"


def log_event(name: str, properties: Dict[str, Any] | None = None) -> None:
    try:
        with EVENTS_FILE.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "event": name,
                        "properties": properties or {},
                    }
                )
                + "\n"
            )
    except Exception:
        # Best-effort only
        pass

