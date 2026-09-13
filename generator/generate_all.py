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


from library import io_utils, schedule, line_builder, station_builder,  labels

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
    stations = station_builder.build_stations(info, seg_times)
    for station_id, station_json in stations.items():
        io_utils.write_json(out_dir / "stations" / f"{station_id}.json", station_json)
    print(f"wrote {len(stations)} station file(s) to {out_dir / 'stations'}")

if __name__ == "__main__":
    main()
