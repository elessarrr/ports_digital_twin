
import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalVesselDataProcessor:
    """
    Processes historical vessel data from backup XML files.
    """
    
    def __init__(self, backups_dir: str = None, output_dir: str = None):
        """
        Initialize the processor.
        
        Args:
            backups_dir: Directory containing backup XML files.
            output_dir: Directory to save processed data.
        """
        if backups_dir:
            self.backups_dir = Path(backups_dir)
        else:
            # Default to relative path from this script
            self.backups_dir = (Path(__file__).parent.parent.parent.parent / "raw_data" / "vessel_data" / "backups").resolve()
            
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to data/vessel_data
            self.output_dir = (Path(__file__).parent.parent.parent.parent / "data" / "vessel_data").resolve()
            
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Regex to parse filename: Type_Date_Time.xml
        # e.g. Expected_departures_20251221_060015.xml
        self.filename_pattern = re.compile(r"(.+)_(\d{8})_(\d{6})\.xml")
        
    def scan_backups(self) -> Dict[str, Dict[str, Path]]:
        """
        Scan backup directory and identify the best file (latest timestamp) for each day and type.
        
        Returns:
            Dict[date_str, Dict[file_type, file_path]]
        """
        if not self.backups_dir.exists():
            logger.warning(f"Backups directory not found: {self.backups_dir}")
            return {}
            
        # Structure: { "20251221": { "Expected_departures": path, "Expected_arrivals": path, ... } }
        daily_files = {}
        
        for file_path in self.backups_dir.glob("*.xml"):
            match = self.filename_pattern.match(file_path.name)
            if match:
                file_type = match.group(1)
                date_str = match.group(2)
                time_str = match.group(3)
                
                if date_str not in daily_files:
                    daily_files[date_str] = {}
                
                # If we haven't seen this type for this day, or if this file is newer (lexicographically by time string)
                current_best = daily_files[date_str].get(file_type)
                
                if current_best is None:
                    daily_files[date_str][file_type] = (time_str, file_path)
                else:
                    current_time, _ = current_best
                    if time_str > current_time:
                        daily_files[date_str][file_type] = (time_str, file_path)
        
        # Clean up the dictionary to remove timestamp tuple, just keep the path
        cleaned_files = {}
        for date_str, types in daily_files.items():
            cleaned_files[date_str] = {k: v[1] for k, v in types.items()}
            
        logger.info(f"Found historical data for {len(cleaned_files)} days")
        return cleaned_files

    def parse_xml_to_df(self, file_path: Path, file_type: str) -> pd.DataFrame:
        """
        Parse a single XML file into a DataFrame.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            records = []
            
            # Identify the repeating element based on file type (heuristic)
            # Usually 'vessel', 'arrival', 'departure', or 'record'
            # We'll search for common tags
            
            for child in root:
                record = {}
                # Extract all text fields
                for subchild in child:
                    record[subchild.tag] = subchild.text
                
                # Add metadata
                record['source_file_type'] = file_type
                record['source_file_date'] = self.filename_pattern.match(file_path.name).group(2)
                records.append(record)
                
            return pd.DataFrame(records)
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return pd.DataFrame()

    def consolidate_history(self) -> pd.DataFrame:
        """
        Main execution method: Scan, Parse, and Consolidate.
        """
        daily_files = self.scan_backups()
        all_dfs = []
        
        for date_str, files_map in daily_files.items():
            for file_type, file_path in files_map.items():
                logger.info(f"Processing {date_str} - {file_type}")
                df = self.parse_xml_to_df(file_path, file_type)
                if not df.empty:
                    all_dfs.append(df)
        
        if not all_dfs:
            logger.warning("No data found to consolidate.")
            return pd.DataFrame()
            
        consolidated_df = pd.concat(all_dfs, ignore_index=True)
        
        # Save to CSV
        output_path = self.output_dir / "historical_consolidated.csv"
        consolidated_df.to_csv(output_path, index=False)
        logger.info(f"Saved consolidated history to {output_path} ({len(consolidated_df)} rows)")
        
        return consolidated_df

if __name__ == "__main__":
    processor = HistoricalVesselDataProcessor()
    processor.consolidate_history()
