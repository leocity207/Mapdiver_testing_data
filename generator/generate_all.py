#!/usr/bin/env python3
"""
Convenience wrapper: runs both generators against the same info.json in
one process (a little cheaper than calling the two scripts separately,
since line data is only computed once).

Usage:
    python generate_all.py output_dir
"""
import sys
from pathlib import Path
from collections import defaultdict

from library import io_utils, schedule, line_builder, labels

def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python generate_all.py "
            "<output_dir>"
        )
        sys.exit(1)

    out_dir = Path(sys.argv[1])

    info = io_utils.load_info("info.json")
    template_svg = io_utils.load_svg_template("line_label_template.svg")
    seg_times = schedule.build_segment_times(info["interstation-plan"])

    # Line builder
    for line_id in info["lines-id"]:
        line_json, _patterns = line_builder.build_line(
            line_id, info, seg_times, template_svg, include_icon=True
        )
        io_utils.write_json(out_dir / "lines" / f"{line_id}.json", line_json)
    print(f"wrote {len(info['lines-id'])} line file(s) to {out_dir / 'lines'}")

    # Station builder
    stations = build_stations(info, seg_times)
    for station_id, station_json in stations.items():
        io_utils.write_json(out_dir / "stations" / f"{station_id}.json", station_json)
    print(f"wrote {len(stations)} station file(s) to {out_dir / 'stations'}")

def build_stations(info, seg_times):
    naming_exceptions = info.get("station-naming-exception", {})

    lines_by_station = defaultdict(set)
    directions_by_station = defaultdict(dict)

    for line_id in info["lines-id"]:
        for station_id in info["line-definition"][line_id]:
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

if __name__ == "__main__":
    main()
