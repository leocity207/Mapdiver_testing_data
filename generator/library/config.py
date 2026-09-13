"""
Configuration for the transit data generator.

Everything here is a knob you're likely to want to change for your real
data set - naming/URL conventions, colors, etc. Nothing computational
lives in this file.
"""

# --- URL templates -----------------------------------------------------
# {num} is replaced with the numeric part of the id, e.g. "S-12" -> "12".
STATION_URL_TEMPLATE = "/station/{num}"
LINE_URL_TEMPLATE = "/line/{num}"

# --- Label templates -----------------------------------------------------
# Used only when there's no explicit override
# (station-naming-exception / line-naming-exception in info.json).
STATION_LABEL_TEMPLATE = "Station {num}"
LINE_LABEL_TEMPLATE = "Line {num}"

# --- Direction coding -----------------------------------------------------
# Pattern / direction ids look like "L-1_A_15":
DIRECTION_FORWARD = "F"
DIRECTION_REVERSE = "R"