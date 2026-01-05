# Raw Data Update Guide

I've created a script that automates the entire process: consolidating the new data from your backups and pushing the updated historical CSV to GitHub.

### How to use it

1.  **Add your new data:**
    Place your new XML vessel activity files into the `raw_data/vessel_data/backups/` directory.

2.  **Run the update script:**
    Run the following command in your terminal:
    ```bash
    python3 hk_port_digital_twin/src/utils/update_and_push_history.py
    ```

### What the script does
*   **Consolidates Data:** It scans `raw_data/vessel_data/backups/`, finds the latest files for each day, and merges them into `data/vessel_data/historical_consolidated.csv`.
*   **Git Automation:** It automatically stages the updated CSV, commits it with a timestamp, and pushes it to GitHub.

Once the script finishes, your dashboard (if connected to the repo) will reflect the updated historical data.
