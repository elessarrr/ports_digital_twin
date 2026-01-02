import os
import sys
import json
from datetime import datetime, timedelta


def main():
    """Main function to trigger the data refresh."""
    # Add the project root to the Python path to allow for absolute imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    sys.path.insert(0, project_root)

    from hk_port_digital_twin.src.utils.data_loader import refresh_vessel_data

    # --- Guard Logic ---
    # Prevents the script from running too frequently.
    # Checks for a marker file (last_refresh.json) to determine if a refresh is needed.

    # Configuration from environment variables
    # Default to 20 hours to allow for slight variations in execution time if running daily
    max_age_hours = int(os.getenv("VESSEL_DATA_REFRESH_MAX_AGE_HOURS", 20))
    log_dir = os.path.join(project_root, "raw_data", "vessel_data", "logs")
    marker_file = os.path.join(log_dir, "last_refresh.json")

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Check if a recent refresh has already occurred
    if os.path.exists(marker_file):
        with open(marker_file, "r") as f:
            try:
                last_refresh_data = json.load(f)
                last_refresh_time = datetime.fromisoformat(last_refresh_data.get("timestamp"))
                if datetime.now() - last_refresh_time < timedelta(hours=max_age_hours):
                    print(f"{datetime.now().isoformat()}: Skipping refresh: A successful refresh occurred at {last_refresh_time}, which is within the {max_age_hours}-hour threshold.")
                    sys.exit(0)
            except (json.JSONDecodeError, KeyError):
                print("Warning: Could not read the last refresh marker file. Proceeding with refresh.")

    # --- Perform Refresh ---
    print(f"{datetime.now().isoformat()}: Starting vessel data refresh...")
    result = refresh_vessel_data()

    # --- Update Marker on Success ---
    if result.get("status") == "success":
        # Write a new marker file with the current timestamp
        with open(marker_file, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat()}, f)
        print(f"{datetime.now().isoformat()}: Refresh successful. Updated marker file: {marker_file}")
    else:
        print(f"{datetime.now().isoformat()}: Refresh failed. See logs for details. Error: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()