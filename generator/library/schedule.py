"""
Core, side-effect-free scheduling logic:

  - turning interstation-plan into a lookup table of travel times
  - building the ordered stop list + relative timing profile for one
    pattern (one line x one service tier x one direction)
  - expanding a pattern into concrete "timetables" missions

Nothing here reads/writes files - see io_utils.py and line_builder.py for
that.
"""
from . import config

# ---------------------------------------------------------------------
# interstation-plan lookup
# ---------------------------------------------------------------------

def build_segment_times(interstation_plan):
    """
    interstation-plan is a list of [station_a, station_b, minutes].
    Travel time is assumed symmetric (A->B takes as long as B->A), which
    is why this is keyed by an unordered pair.
    """
    seg = {}
    for a, b, minutes in interstation_plan:
        seg[frozenset((a, b))] = minutes
    return seg


def segment_time(seg_times, a, b):
    try:
        return seg_times[frozenset((a, b))]
    except KeyError:
        raise ValueError(
            f"No interstation-plan entry between {a!r} and {b!r}. "
            "interstation-plan must contain an entry for every pair of "
            "stations that are adjacent in some line-definition."
        )


# ---------------------------------------------------------------------
# time parsing / formatting
# ---------------------------------------------------------------------

def parse_hms_to_seconds(hms):
    parts = [int(p) for p in hms.split(":")]
    while len(parts) < 3:
        parts.append(0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def parse_hms_to_minutes(hms):
    return parse_hms_to_seconds(hms) // 60


def format_seconds_as_hms(total_seconds):
    total_seconds = int(round(total_seconds)) % 86400
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ---------------------------------------------------------------------
# direction / stop-skipping
# ---------------------------------------------------------------------

def direction_order(base_stations, is_reversed):
    """line-definition order is the forward ("Aller") direction."""
    return list(reversed(base_stations)) if is_reversed else list(base_stations)


def build_pattern_profile(ordered_stations, skip_set, seg_times, stop_time_map):
    """
    ordered_stations: the FULL station list for this line, in the
        direction of travel (already reversed if needed) - i.e. what
        "local" (no skips) would stop at.
    skip_set: station ids to skip for this particular tier.

    Returns (stops, arrival_offsets, departure_offsets):
      - stops: ordered_stations with skipped stations removed
      - arrival_offsets / departure_offsets: ints (minutes) or None,
        relative to t=0 at the first stop's departure.

    Travel time across a skipped station is just the sum of the
    surrounding interstation-plan segments - no dwell time is added for
    a station a given tier doesn't stop at.
    """
    kept_indices = [i for i, s in enumerate(ordered_stations) if s not in skip_set]
    if len(kept_indices) < 2:
        raise ValueError(
            "A pattern needs at least two stops once skipped_station is "
            "applied - check your skipped_station list."
        )

    stops = [ordered_stations[i] for i in kept_indices]
    arrival = [None] * len(stops)
    departure = [None] * len(stops)

    departure[0] = 0  # reference zero point: the train leaving the first stop
    last = len(stops) - 1
    for pos in range(1, len(stops)):
        prev_idx = kept_indices[pos - 1]
        this_idx = kept_indices[pos]
        travel = sum(
            segment_time(seg_times, ordered_stations[i], ordered_stations[i + 1])
            for i in range(prev_idx, this_idx)
        )
        arrival[pos] = departure[pos - 1] + travel
        if pos != last:
            departure[pos] = arrival[pos] + stop_time_map.get(stops[pos], 0)
        # else: terminus - no further departure, stays None

    return stops, arrival, departure


# ---------------------------------------------------------------------
# patterns for a whole line
# ---------------------------------------------------------------------

def build_line_patterns(line_id, base_stations, line_infos, seg_times, stop_time_map):
    """
    line_info: [{"time_interval": int, "starting": "H:MM:SS",
                   "ending": "H:MM:SS",
                   "skipped_station": [optional],
                   "stop_pattern":str
                   "calendar_pattern": str}]
                   

    Returns a list of pattern dicts. Each dict carries two internal
    helper keys, "_stops" and "_tier", used by line_builder.py /
    generate_stations.py; strip them before writing a pattern to disk.
    """
    patterns = []
    seen_stop_patterns = {}
    
    if len(base_stations) == 0: # line with no stations
        return []

    for data in line_infos:
        time_interval = data["time_interval"]
        skip_set = set(data.get("skipped_station", []))
        orders = [True, False] if data.get("is_reversed", None) is None else [True] if data["is_reversed"] else [False]
        stop_pattern = data["stop_pattern"]
        calendar_patterns = data["calendar_patterns"]
        starting_text= data["starting"]
        start_minutes = parse_hms_to_minutes(data["starting"])
        seen_stop_patterns[stop_pattern] = 1 if seen_stop_patterns.get(stop_pattern, None) is None else seen_stop_patterns[stop_pattern] + 1

        for is_reversed in orders:
            direction_letter = config.DIRECTION_REVERSE if is_reversed else config.DIRECTION_FORWARD
            
            ordered = direction_order(base_stations, is_reversed)
            stops, arrival, departure = build_pattern_profile( ordered, skip_set, seg_times, stop_time_map)

            pattern_id = f"{line_id}_{direction_letter}_{time_interval}_{stop_pattern}_{starting_text}"
            phase = start_minutes % time_interval
            
            patterns.append({
                "id": pattern_id,
                "label": f"{stop_pattern.capitalize()}_{direction_letter}_{seen_stop_patterns[stop_pattern]}",
                "interval_time": time_interval,
                "departure_time": phase,
                "first_departure": data["starting"],
                "last_departure": data["ending"],
                "stop_pattern": stop_pattern,
                "calendar_patterns": calendar_patterns,
                "is_reversed": is_reversed,
                "info_messages": [],
                "arrival_times": arrival,
                "departure_times": departure,
                "_stops": stops,
            })
    return patterns


# ---------------------------------------------------------------------
# concrete missions ("timetables") from a pattern
# ---------------------------------------------------------------------

def build_timetables_for_pattern(pattern, line_label_text):
    """
    Expands one pattern's generic (relative-minute) profile into actual
    trains: every departure from first_departure to last_departure,
    stepped by interval_time, each with absolute clock times per stop.
    """
    start_s = parse_hms_to_seconds(pattern["first_departure"])
    end_s = parse_hms_to_seconds(pattern["last_departure"])
    time_interval_s = pattern["interval_time"] * 60

    missions = []
    t = start_s
    n = 0
    while t <= end_s:
        arrival_strs = [
            None if off is None else (t + off * 60)
            for off in pattern["arrival_times"]
        ]
        departure_strs = [
            None if off is None else (t + off * 60)
            for off in pattern["departure_times"]
        ]
        missions.append({
            "id": f"{pattern['id']}_{n:03d}",
            "label": f"{line_label_text} {pattern['label']} {format_seconds_as_hms(t)}",
            "stop_pattern": pattern["stop_pattern"],
            "calendar_patterns": pattern["calendar_patterns"],
            "info_messages": [],
            "arrival_times": arrival_strs,
            "departure_times": departure_strs,
        })
        t += time_interval_s
        n += 1

    return missions
