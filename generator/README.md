# Transit data generator

Turns `info.json` (+ a line-icon SVG template) into one JSON file per
station and one JSON file per line. Fully deterministic — same input,
same output, every time.

## Layout

```
transit_gen/            the actual logic, one concern per file
    config.py            all the knobs: URL/label templates, colors, tiers
    ids.py                "S-12" -> "12"
    labels.py             label/url helpers
    colors.py              deterministic per-line color assignment
    schedule.py            segment times, pattern timing, timetable expansion
    io_utils.py             load info.json/svg, write JSON
    line_builder.py          combines the above into one "line" object
                              (shared by both scripts below)
generate_lines.py        CLI: one JSON file per line + embedded SVG icon
generate_stations.py     CLI: one JSON file per station
generate_all.py          convenience wrapper, runs both in one process
sample_data/             a small synthetic info.json + svg to try things on
```

## Usage

```bash
# both at once
python generate_all.py info.json line_label_template.svg output/

# or separately
python generate_lines.py info.json line_label_template.svg output/lines
python generate_stations.py info.json output/stations
```

Try it on the bundled sample first:

```bash
python generate_all.py sample_data/info.json sample_data/line_label_template.svg output
```

## How scheduling works

- **`interstation-plan`** is read as a lookup of travel time between
  *adjacent* stations. It's assumed symmetric (A→B takes as long as
  B→A) — tell me if that's wrong and I'll key it by direction instead.
- **Direction**: `line-definition[line]` is the forward/"Aller" (`A`)
  order; reversed is "Retour" (`R`). Pattern/direction ids look like
  `L-1_A_15` (line, direction, time_interval).
- **Skipping stops**: each `Line-info-<tier>[line]` may optionally carry
  `"skipped_station": ["S-3", ...]`. A skipped station gets no dwell
  time — the travel time across it is just the sum of the surrounding
  `interstation-plan` segments, per your instructions.
- **A pattern's own `arrival_times`/`departure_times`** are relative
  minute offsets from `0` at the first stop's departure (not clock
  times) — this is the generic timing "shape" of the pattern. The first
  stop's arrival and the last stop's departure are `null` (a train
  doesn't "arrive" at its origin or "depart" from its terminus).
- **`timetables`** are the concrete missions: every departure from
  `first_departure` to `last_departure`, stepped by `time_interval`, with the
  pattern's relative offsets converted into absolute `HH:MM:SS` clock
  times for that specific run.
- A station's `directions` map lists, for every pattern that stops
  there, the terminus of that pattern — except at the terminus itself
  (a station doesn't point to itself).

## Assumptions I had to make (things info.json doesn't specify)

These are all centralized in `config.py` / `colors.py` so they're easy
to change without touching the logic:

1. **Line colors**: info.json has no color data, so each line gets a
   deterministic color hashed from its id (`colors.py`). If you add a
   `"line-color": {"L-1": "#RRGGBB", ...}` map to info.json, that's used
   instead — no code changes needed.
2. **Line labels**: stations use `"Station {N}"` per your spec; I used
   the same convention for lines (`"Line {N}"`), overridable via an
   optional `"line-naming-exception"` map in info.json (same shape as
   `station-naming-exception`). Change `LINE_LABEL_TEMPLATE` in
   `config.py` if you want something else (e.g. `"Ligne {N}"`).
3. **`color` field shape**: the spec describes it as a keys/values
   mapping rather than a bare string, so it's written as
   `{"default": "#RRGGBB"}`. Change `COLOR_KEY` in `config.py` if your
   front end expects a different key name.
4. **`calendar_pattern`**: info.json carries no service-calendar data,
   so every mission is tagged `"daily"` (`DEFAULT_CALENDAR_PATTERN` in
   `config.py`).
5. **`departure_time`** (the int field on a pattern, distinct from
   `first_departure`/`last_departure`): interpreted as the phase offset
   in minutes — `starting time mod time_interval` — i.e. which minute of each
   cycle trains depart on.
6. **`landmark-id`** isn't used by either output yet since neither
   spec'd file references landmarks. Let me know what it should feed
   into and I'll wire it in.

## Extending

- Real skip data, real colors, line labels → just add the optional keys
  described above to your actual `info.json`; no script changes needed.
- Want per-station override URLs, or a different id/number scheme?
  Edit `ids.py` / `config.py`.
