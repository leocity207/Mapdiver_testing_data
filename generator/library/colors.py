"""
Deterministic (non-random) color assignment for lines.
"""
import hashlib

from . import config


def line_color(line_id, overrides=None):
    """
    Priority:
      1. an explicit "line-color" map in info.json (`overrides`), if the
         line id is present there.
      2. a stable pick from config.COLOR_PALETTE, indexed by a hash of
         the line id. This is deterministic (sha256 is not randomized
         between runs/machines) but is only a *placeholder* until you
         supply real colors - see config.py for details.
    """
    overrides = overrides or {}
    if line_id in overrides:
        return overrides[line_id]

    digest = hashlib.sha256(line_id.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(config.COLOR_PALETTE)
    return config.COLOR_PALETTE[index]
