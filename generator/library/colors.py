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


def switch_rgb_channels(color: str, order: str = "BGR") -> str:
    """
    Reorder the RGB channels of a hex color.

    Supported formats:
        #RGB
        #RGBA
        #RRGGBB
        #RRGGBBAA

    Examples:
        switch_rgb_channels("#123456", "BGR")  -> "#563412"
        switch_rgb_channels("#123456", "GRB")  -> "#341256"
        switch_rgb_channels("#1234", "BGR")    -> "#3412"
    """
    color = color.strip().replace(" ", "")

    if not color.startswith("#"):
        raise ValueError("Color must start with '#'")

    hex_color = color[1:]

    if len(hex_color) not in (3, 4, 6, 8):
        raise ValueError("Color must be #RGB, #RGBA, #RRGGBB, or #RRGGBBAA")

    order = order.upper()

    if sorted(order) != ["B", "G", "R"]:
        raise ValueError("order must be a permutation of RGB, e.g. RGB, BGR, GRB")

    # Expand short format: RGB -> RRGGBB, RGBA -> RRGGBBAA
    short = len(hex_color) in (3, 4)
    if short:
        hex_color = "".join(c * 2 for c in hex_color)

    # Extract channels
    channels = {
        "R": hex_color[0:2],
        "G": hex_color[2:4],
        "B": hex_color[4:6],
    }

    # Preserve alpha if present
    alpha = hex_color[6:8] if len(hex_color) == 8 else ""

    result = "".join(channels[c] for c in order) + alpha

    # Return in the same short/long format
    if short:
        result = "".join(result[i] for i in range(0, 6, 2))
        if alpha:
            result += alpha[0]

    return "#" + result
