from pathlib import Path
import json
from typing import Any
from functools import wraps

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


def override_image(fn):
    extra_items = [
        cleanup_item(item)
        for item in override_items
        if (
            item.get("_type") == "features"
            and item.get("_feature") == "Image"
        )
    ]
    @wraps(fn)
    def inner(*args, space_id=None, **kwargs):
        result = fn(*args, space_id=space_id, **kwargs)
        if space_id:
            filtered_items = [
                item
                for item in extra_items
                if item.get("boundingbox", {}).get("space", {}).get("@id") == space_id
            ]
        else:
            filtered_items = extra_items
        return [*filtered_items, *result]
    return inner

def override_id():
    def outer(fn):
        @wraps(fn)
        def inner(id, *args, **kwargs):
            for item in override_items:
                if item.get("id") == id:
                    return item
            return fn(id, *args, **kwargs)
        return inner
    return outer