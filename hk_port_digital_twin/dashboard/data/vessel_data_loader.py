"""
This module provides a dedicated class for loading and processing vessel data.
"""
import pandas as pd
from pathlib import Path
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class VesselDataLoader:
    """A class to handle loading and processing of vessel data."""
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    def load_vessel_data(self) -> pd.DataFrame:
        """Loads and processes vessel data from the data directory."""
        all_vessel_records = []
        for xml_file in self.data_dir.glob('*.xml'):
            try:
                records = self.load_single_vessel_file(xml_file)
                all_vessel_records.extend(records)
            except ET.ParseError as e:
                logger.error(f"Error parsing {xml_file.name}: {e}")

        if not all_vessel_records:
            return pd.DataFrame()

        df = pd.DataFrame(all_vessel_records)
        df['arrival_time'] = pd.to_datetime(df['arrival_time'], errors='coerce')
        df['departure_time'] = pd.to_datetime(df['departure_time'], errors='coerce')
        logger.info(f"Loaded {len(df)} vessel records from {len(list(self.data_dir.glob('*.xml')))} files.")
        return df

    def load_single_vessel_file(self, xml_file: Path) -> list[dict]:
        """Loads and processes a single vessel data XML file."""
        records = []
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for vessel_element in root.findall('vessel'):
            record = {
                'vessel_name': vessel_element.findtext('name'),
                'imo_number': vessel_element.findtext('imo'),
                'arrival_time': vessel_element.findtext('arrival_time_utc'),
                'departure_time': vessel_element.findtext('departure_time_utc'),
                'berth': vessel_element.findtext('berth'),
                'status': xml_file.stem
            }
            records.append(record)
        return records