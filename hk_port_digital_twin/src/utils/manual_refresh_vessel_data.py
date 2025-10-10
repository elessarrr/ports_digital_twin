import os
import sys


def main():
    """Main function to trigger the data refresh."""
    # Add the project root to the Python path to allow for absolute imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    sys.path.insert(0, project_root)

    from hk_port_digital_twin.src.utils.data_loader import refresh_vessel_data

    refresh_vessel_data()


if __name__ == "__main__":
    main()