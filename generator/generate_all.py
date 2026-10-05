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


from library import io_utils, schedule, line_builder, station_builder, template_copy

def main():
    if len(sys.argv) != 1:
        print(
            "Usage: python generate_all.py"
        )
        sys.exit(1)

    out_dir = Path(__file__).parent.parent

    info = io_utils.load_info(Path(__file__).parent / "info.json")
    template_svg = io_utils.load_svg_template(Path(__file__).parent / "line_label_template.svg")
    seg_times = schedule.build_segment_times(info["interstation-plan"])

    # Line builder
    for line_id in info["lines-id"]:
        line_json, _patterns = line_builder.build_line(
            line_id, info, seg_times, template_svg, include_icon=True
        )
        io_utils.write_json(out_dir / "data" / "lines" / f"{line_id}.json", line_json)
    print(f"wrote {len(info['lines-id'])} line file(s) to {out_dir / 'data' / 'lines'}")

    # Station builder
    stations = station_builder.build_stations(info, seg_times)
    for station_id, station_json in stations.items():
        io_utils.write_json(out_dir / "data" / "stations" / f"{station_id}.json", station_json)
    print(f"wrote {len(stations)} station file(s) to {out_dir / 'data' / 'stations'}")

    # Copy template files
    template_copy.copy_template_files(out_dir)
    
    #write station and line meta files
    io_utils.write_json(out_dir / "data" / "stations.json",{ "stations": info["stations-id"] })
    io_utils.write_json(out_dir / "data" / "lines.json", { "lines": info["lines-id"] })
if __name__ == "__main__":
    main()
