# Schedule Daily Vessel Data Refresh with launchd (macOS)

Comments for context
- Goal: run `hk_port_digital_twin.src.utils.manual_refresh_vessel_data` once per day on macOS without keeping the app open.
- Approach: use a user LaunchAgent (`launchd`) that calls your project’s virtualenv Python and runs the module via `-m`.
- Safety: no sensitive data is logged; outputs go to project log files. Configuration (like pipeline enable/interval) is read from environment variables.

## Overview
- Creates a LaunchAgent `com.hkport.manualrefresh.plist` in `~/Library/LaunchAgents`.
- Runs daily at a set time (now: 20:00 / 8 pm).
- Adds a 6-hour fallback trigger to catch missed daily runs.
- Logs to `raw_data/vessel_data/logs/` inside your repo.

## Plan Update (8 pm + fallback)
- Change the scheduled time to 20:00 (8 pm) via `StartCalendarInterval`.
- Add `StartInterval=21600` (6 hours) so the agent also runs every 6 hours.
- Add a simple guard in the script (next step) to skip work if the last successful refresh is within 24 hours (configurable), so extra triggers don’t cause redundant downloads.
- Keep `RunAtLoad=true` so you get an immediate run when logging in, useful if the Mac was asleep at 20:00.

## Prerequisites
- macOS with a user account that owns the repo.
- Your project virtualenv exists at `~/Documents/GitHub/ports_digital_twin/hk_port_digital_twin/.venv/`.
- Module path works: `python -m hk_port_digital_twin.src.utils.manual_refresh_vessel_data` (verified earlier).

## Step 1 — Create log directory (if missing)
```bash
mkdir -p ~/Documents/GitHub/ports_digital_twin/raw_data/vessel_data/logs
```

## Step 2 — Create the LaunchAgent plist
Create `~/Library/LaunchAgents/com.hkport.manualrefresh.plist` with the content below. Adjust paths if needed.

Important: When saving the file, paste only the XML content (do not include Markdown code fences like ```xml). The file must begin with `<?xml version="1.0" ...>`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.hkport.manualrefresh</string>

    <key>ProgramArguments</key>
    <array>
      <string>/Users/Bhavesh/Documents/GitHub/ports_digital_twin/hk_port_digital_twin/.venv/bin/python</string>
      <string>-m</string>
      <string>hk_port_digital_twin.src.utils.manual_refresh_vessel_data</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/Bhavesh/Documents/GitHub/ports_digital_twin</string>

    <!-- Set env vars needed by the fetcher -->
    <key>EnvironmentVariables</key>
    <dict>
      <key>VESSEL_DATA_PIPELINE_ENABLED</key>
      <string>true</string>
      <!-- Optional: override the base URL if desired -->
      <!-- <key>HK_VESSEL_DATA_BASE_URL</key>
      <string>https://data.gov.hk/en-data/dataset/hk-md-mardep-vessel-arrivals-and-departures</string> -->
    </dict>

    <!-- Run daily at 20:00 (8 pm) -->
    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key>
      <integer>20</integer>
      <key>Minute</key>
      <integer>0</integer>
    </dict>

    <!-- Fallback: also trigger every 6 hours (21600 seconds) -->
    <key>StartInterval</key>
    <integer>21600</integer>

    <!-- Persist across reboots -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Logs -->
    <key>StandardOutPath</key>
    <string>/Users/Bhavesh/Documents/GitHub/ports_digital_twin/raw_data/vessel_data/logs/manual_refresh.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/Bhavesh/Documents/GitHub/ports_digital_twin/raw_data/vessel_data/logs/manual_refresh.err.log</string>
  </dict>
  </plist>
```

Validate the plist:
```bash
plutil -lint ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
```

## Step 3 — Load and start the agent
Use one of the following (modern vs. classic `launchctl`):

```bash
# Modern (recommended)
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
launchctl enable gui/$UID/com.hkport.manualrefresh

# Classic (still works)
launchctl load ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
```

Optionally run an immediate test:
```bash
launchctl kickstart -k gui/$UID/com.hkport.manualrefresh
# or
launchctl start com.hkport.manualrefresh
```

## Step 4 — Verify
- Check agent is listed:
```bash
launchctl list | grep com.hkport.manualrefresh
```
- Tail logs:
```bash
tail -f ~/Documents/GitHub/ports_digital_twin/raw_data/vessel_data/logs/manual_refresh.out.log \
        ~/Documents/GitHub/ports_digital_twin/raw_data/vessel_data/logs/manual_refresh.err.log
```
- Confirm downloaded files in `~/Documents/GitHub/ports_digital_twin/raw_data/`:
  - `Arrived_in_last_36_hours.xml`
  - `Departed_in_last_36_hours.xml`
  - `Expected_arrivals.xml`
  - `Expected_departures.xml`

## Fallback Behavior and Guard (planned)
- Goal: ensure a refresh happens at the next opportunity if the Mac is asleep at 20:00.
- Mechanism: the agent runs at 20:00 daily and every 6 hours. The refresh script will add a small guard at the start that checks a marker (e.g., `raw_data/vessel_data/logs/last_refresh.json`) and only performs a download if the last successful refresh is older than 24 hours.
- Configuration: we will support environment variables so you can tune behavior without code changes:
  - `VESSEL_DATA_REFRESH_MAX_AGE_HOURS` (default `24`) — threshold to decide if a refresh is needed.
  - `VESSEL_DATA_FALLBACK_INTERVAL_HOURS` (default `6`) — reflected in the plist via `StartInterval`.
- Result: if the 20:00 run is missed, the next 6-hour trigger will run and, if needed, perform the refresh.

Note: This guard will be implemented in `hk_port_digital_twin/src/utils/manual_refresh_vessel_data.py` in the next step. It will write/update `last_refresh.json` after a successful refresh, and never log sensitive data.

## Maintenance
- Change schedule: edit `Hour`/`Minute` in the plist, and/or the `StartInterval` value, then reload:
```bash
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
```
- Disable:
```bash
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
# or
launchctl unload ~/Library/LaunchAgents/com.hkport.manualrefresh.plist
```
- Update Python path: edit `ProgramArguments[0]` if venv moves.

- Update fallback interval: change `<integer>21600</integer>` to your preferred value (e.g., 10800 for 3 hours); remember to reload the agent.

## Troubleshooting
- Permissions: ensure the plist file is owned by your user and lives under `~/Library/LaunchAgents`.
- Plist validity: `plutil -lint` must return `OK`.
- Python not found: verify the venv path exists, or replace with your system Python.
- Pipeline disabled: make sure `VESSEL_DATA_PIPELINE_ENABLED=true` is set in `EnvironmentVariables`.
- External network errors: check `manual_refresh.err.log` and the daily pipeline log `raw_data/vessel_data/logs/vessel_pipeline_YYYYMMDD.log`.

- Copied backticks into plist: if `plutil -lint` shows an "Unexpected character`" near line 1, open the file and remove any leading/trailing Markdown code fences (```xml / ```), then re-run the lint.

## Alternative: Built‑in Daily Interval (no OS scheduler)
If your app stays running, set env vars and let the scheduler handle it:
```bash
export VESSEL_DATA_PIPELINE_ENABLED=true
export VESSEL_DATA_FETCH_INTERVAL=1440  # minutes (24 hours)
python hk_port_digital_twin/run_demo.py
```
This uses `VesselDataScheduler` to fetch daily, but requires the app to remain running.