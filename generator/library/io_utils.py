"""
Loading info.json / the SVG template, and writing JSON output files.
"""
import json
from pathlib import Path


REQUIRED_KEYS = [
    "lines-id",
    "stations-id",
    "line-definition",
    "interstation-plan",
    "station-stop-time",
]


def load_info(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ValueError(f"info.json is missing required key(s): {missing}")

    return data


def load_svg_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
