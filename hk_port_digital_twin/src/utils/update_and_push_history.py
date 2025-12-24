import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from hk_port_digital_twin.src.utils.process_history import HistoricalVesselDataProcessor

# Configure loggings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_git_command(command_list):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            command_list,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {' '.join(command_list)}")
        logger.error(f"Error output: {e.stderr}")
        raise

def main():
    logger.info("Starting historical data update process...")
    
    # 1. Run the consolidation process
    try:
        processor = HistoricalVesselDataProcessor()
        df = processor.consolidate_history()
        
        if df.empty:
            logger.warning("No data consolidated. Aborting update.")
            return
            
        logger.info(f"Successfully consolidated {len(df)} records.")
        
    except Exception as e:
        logger.error(f"Failed to consolidate history: {e}")
        return

    # 2. Git operations
    try:
        # Check for changes
        status = run_git_command(['git', 'status', '--porcelain'])
        
        if not status:
            logger.info("No changes detected in git status. Nothing to push.")
            return

        logger.info("Changes detected. Proceeding with git operations...")
        
        # Add the consolidated CSV
        csv_path = Path("data/vessel_data/historical_consolidated.csv")
        if csv_path.exists():
            run_git_command(['git', 'add', str(csv_path)])
        
        # Note: We do not automatically add raw_data/vessel_data/backups as it is likely gitignored.
        # The consolidated CSV is sufficient for the dashboard.
            
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Update historical vessel data: {timestamp}"
        run_git_command(['git', 'commit', '-m', commit_message])
        logger.info(f"Committed changes with message: '{commit_message}'")
        
        # Push
        logger.info("Pushing to remote repository...")
        run_git_command(['git', 'push'])
        logger.info("Successfully pushed changes to GitHub.")
        
    except Exception as e:
        logger.error(f"Git operation failed: {e}")
        logger.info("Please verify your git configuration and network connection.")

if __name__ == "__main__":
    main()
