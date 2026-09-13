from collections import defaultdict

from . import line_builder, labels

def build_stations(info, seg_times):
    naming_exceptions = info.get("station-naming-exception", {})

    lines_by_station = defaultdict(set)
    directions_by_station = defaultdict(dict)

    for line_id in info["lines-id"]:
        for station_id in info["line-definition"].get(line_id, []):
            lines_by_station[station_id].add(line_id)

        _line_json, patterns = line_builder.build_line(
            line_id, info, seg_times, template_svg=None, include_icon=False
        )
        for pattern in patterns:
            stops = pattern["_stops"]
            terminus = stops[-1]
            # Every stop except the terminus itself gets a "here's where
            # this pattern is headed" entry. The terminus doesn't point
            # to itself.
            for station_id in stops[:-1]:
                directions_by_station[station_id][pattern["id"]] = terminus
    stations = {}
    for station_id in info["stations-id"]:
        stations[station_id] = {
            "label": labels.station_label(station_id, naming_exceptions),
            "url": labels.station_url(station_id),
            "id": station_id,
            "lines": sorted(lines_by_station.get(station_id, set())),
            "directions": directions_by_station.get(station_id, {}),
        }
    return stations
