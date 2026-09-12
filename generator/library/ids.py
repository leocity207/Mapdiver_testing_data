"""
Helpers for pulling the numeric part out of ids like "S-12" or "L-3".
"""
import re

_NUM_RE = re.compile(r"(\d+)\s*$")


def numeric_part(item_id):
    """
    'S-12' -> '12', 'L-3' -> '3'.

    Returns a *string* (not int) so that any leading zeros in your real
    ids ("S-007") are preserved in labels/urls instead of being silently
    dropped.
    """
    match = _NUM_RE.search(item_id)
    if not match:
        raise ValueError(
            f"Could not find a numeric suffix in id {item_id!r}. "
            "Expected something like 'S-12' or 'L-3'."
        )
    return match.group(1)
