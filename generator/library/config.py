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

# --- Service tiers -----------------------------------------------------
# The generator looks for "Line-info-<tier>" for each of these. A line
# does not need to appear in all three - a line missing from "Line-info-
# rapid", for instance, simply gets no rapid patterns.
SERVICE_TIERS = ["local", "express", "rapid"]

# --- Direction coding -----------------------------------------------------
# Pattern / direction ids look like "L-1_A_15":
#   A = "Aller"  = stations taken in line-definition order (forward)
#   R = "Retour" = stations taken in reverse order
DIRECTION_FORWARD = "A"
DIRECTION_REVERSE = "R"

# --- Color -----------------------------------------------------
# info.json has no per-line color data by default. If you add a
# "line-color": {"L-1": "#RRGGBB", ...} map to info.json it will be used
# as-is. Otherwise each line gets a deterministic color picked from the
# palette below, keyed off a hash of its id (same info.json -> same
# colors, every time, no randomness).
#
# The line output's "color" field is written as an object
# ({COLOR_KEY: "#RRGGBB"}) since the schema describes it as a
# keys/values mapping rather than a bare string. Replace COLOR_KEY with
# whatever your front-end actually expects as the key.
COLOR_KEY = "default"

COLOR_PALETTE = [
    "#E4002B", "#0072CE", "#00A650", "#F7A600", "#7B2D8E",
    "#00AEEF", "#EE7203", "#8DC63F", "#EC008C", "#6D6E71",
]

# --- Calendar -----------------------------------------------------
# info.json carries no service-calendar information, so every generated
# mission is tagged with this constant. Change this (or extend
# schedule.build_timetables_for_pattern) if/when you add real calendar
# data.
DEFAULT_CALENDAR_PATTERN = "daily"
