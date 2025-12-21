import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os
import xml.etree.ElementTree as ET

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hk_port_digital_twin.src.utils.process_history import HistoricalVesselDataProcessor

class TestHistoricalVesselDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = HistoricalVesselDataProcessor(
            backups_dir="mock_backups",
            output_dir="mock_output"
        )

    def test_scan_backups_filename_parsing(self):
        """Test that filenames are parsed correctly and latest daily file is selected."""
        # Mock glob to return specific files
        mock_files = [
            Path("mock_backups/vessel_arrivals_20231025_100000.xml"),
            Path("mock_backups/vessel_arrivals_20231025_120000.xml"),
            Path("mock_backups/vessel_departures_20231025_100000.xml")
        ]
        
        # We need to mock exists() to return True
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.glob', return_value=mock_files):
                daily_files = self.processor.scan_backups()
                
                # Check 20231025 exists
                self.assertIn('20231025', daily_files)
                
                # Check arrivals selected the later one (120000)
                # The value is Path object
                self.assertEqual(daily_files['20231025']['vessel_arrivals'].name, "vessel_arrivals_20231025_120000.xml")
                
                # Check departures selected the only one
                self.assertEqual(daily_files['20231025']['vessel_departures'].name, "vessel_departures_20231025_100000.xml")

    @patch('xml.etree.ElementTree.parse')
    def test_parse_xml_to_df(self, mock_parse):
        """Test XML parsing logic."""
        # Create a mock XML structure
        # <root>
        #   <vessel>
        #     <vessel_name>Vessel A</vessel_name>
        #     <call_sign>CALLA</call_sign>
        #   </vessel>
        # </root>
        
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_parse.return_value = mock_tree
        mock_tree.getroot.return_value = mock_root
        
        # Create a child element (vessel)
        mock_child = MagicMock()
        mock_root.__iter__.return_value = [mock_child]
        
        # Create subchildren (fields)
        subchild1 = MagicMock()
        subchild1.tag = 'vessel_name'
        subchild1.text = 'Vessel A'
        
        subchild2 = MagicMock()
        subchild2.tag = 'call_sign'
        subchild2.text = 'CALLA'
        
        mock_child.__iter__.return_value = [subchild1, subchild2]
        
        file_path = Path("mock_backups/vessel_arrivals_20231025_100000.xml")
        df = self.processor.parse_xml_to_df(file_path, "vessel_arrivals")
        
        self.assertFalse(df.empty)
        self.assertEqual(df.iloc[0]['vessel_name'], 'Vessel A')
        self.assertEqual(df.iloc[0]['call_sign'], 'CALLA')
        self.assertEqual(df.iloc[0]['source_file_type'], 'vessel_arrivals')
        self.assertEqual(df.iloc[0]['source_file_date'], '20231025')

    @patch('hk_port_digital_twin.src.utils.process_history.HistoricalVesselDataProcessor.scan_backups')
    @patch('hk_port_digital_twin.src.utils.process_history.HistoricalVesselDataProcessor.parse_xml_to_df')
    @patch('pandas.DataFrame.to_csv')
    def test_consolidate_history(self, mock_to_csv, mock_parse, mock_scan):
        """Test consolidation of multiple days/files."""
        # Mock scan results
        mock_scan.return_value = {
            '20231025': {'vessel_arrivals': Path('arrivals.xml')}
        }
        
        # Mock parse results
        mock_df = pd.DataFrame({
            'vessel_name': ['Vessel A'],
            'call_sign': ['CALLA'],
            'timestamp': [datetime(2023, 10, 25, 12, 0, 0)]
        })
        mock_parse.return_value = mock_df
        
        df = self.processor.consolidate_history()
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['vessel_name'], 'Vessel A')
        
        # Verify to_csv was called
        mock_to_csv.assert_called_once()

if __name__ == '__main__':
    unittest.main()
