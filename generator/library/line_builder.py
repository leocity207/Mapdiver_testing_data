"""
Turns info.json + the line-icon SVG template into the fully-built "line"
object described in the project brief. Shared by generate_lines.py and
generate_stations.py so both output types are always derived from
exactly the same computation - stations never disagree with lines about
which trains stop where.
"""
from . import config, ids, labels, colors as Colors , schedule


def build_line(line_id, info, seg_times, template_svg=None, include_icon=True):
    """
    Returns (line_json, raw_patterns).

    line_json: the final dict for this line, ready for json.dump.

    raw_patterns: the same patterns but keeping the internal "_stops"
    and "_tier" helper keys (stripped from line_json), for callers that
    need the actual per-pattern stop list - e.g. generate_stations.py
    building each station's "directions".
    """
    base_stations = info["line-definition"].get(line_id, [])
    stop_time_map = info["station-stop-time"]
    naming_exceptions = info.get("line-naming-exception", {})
    colors = info["line-colors"]
    line_info = info["Line-info"].get(line_id, {})

    patterns = schedule.build_line_patterns(line_id, base_stations, line_info, seg_times, stop_time_map)

    line_color = colors.get(line_id, "#000")
    easy_color = Colors.switch_rgb_channels(line_color, "BGR")

    icon_svg = ""
    if include_icon:
        if template_svg is None:
            raise ValueError("include_icon=True requires template_svg")
        icon_svg = template_svg.replace("{COLOR}", line_color).replace(
            "{NUMBER}", ids.numeric_part(line_id)
        )

    line_label_text = labels.line_label(line_id, naming_exceptions)

    timetables = []
    for pattern in patterns:
        timetables.extend(schedule.build_timetables_for_pattern(pattern, line_label_text))

    clean_patterns = [
        {k: v for k, v in p.items() if not k.startswith("_")} for p in patterns
    ]

    line_json = {
        "id": line_id,
        "label": line_label_text,
        "url": labels.line_url(line_id),
        "color": { "default": line_color, "easy": easy_color },
        "info_messages": [],
        "icon": icon_svg,
        "stations": base_stations,
        "patterns": clean_patterns,
        "timetables": timetables,
    }

    return line_json, patterns
