from pathlib import Path
import json
from typing import Any

from api.siibra_api_config import SIIBRA_API_INSTANCES_OVERRIDES

override_items = []

override_dir = Path(SIIBRA_API_INSTANCES_OVERRIDES)

if override_dir.exists() and override_dir.is_dir():
    for f in Path(SIIBRA_API_INSTANCES_OVERRIDES).glob("*.json"):
        if f.name == "example.json":
            continue
        override_items.extend(
            json.loads(f.read_text())
        )

def cleanup_item(obj: dict[str, Any]):
    return {
        k: v
        for k, v in obj.items()
        if not k.startswith("_")
    }
