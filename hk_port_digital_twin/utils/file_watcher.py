import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hk_port_digital_twin.src.utils.data_loader import VesselDataLoader
from hk_port_digital_twin.src.utils.redis_utils import get_redis_connection

logger = logging.getLogger(__name__)

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, data_dir: Path, redis_conn):
        self.data_dir = data_dir
        self.vessel_loader = VesselDataLoader(data_dir)
        self.redis_conn = redis_conn

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".xml"):
            logger.info(f"New file detected: {event.src_path}")
            self.process_new_file(Path(event.src_path))

    def process_new_file(self, file_path: Path):
        try:
            records = self.vessel_loader.load_single_vessel_file(file_path)
            if records:
                # In a real application, you would push this to a message queue
                # or a real-time processing pipeline.
                # For this demo, we'll just log the records.
                logger.info(f"Processed {len(records)} records from {file_path.name}")
                # Here you could update a real-time dashboard component
                # For example, by publishing a message to a Redis channel
                self.redis_conn.publish("vessel_updates", f"New data from {file_path.name}")
        except Exception as e:
            logger.error(f"Error processing file {file_path.name}: {e}")

def start_file_watcher(data_dir: Path):
    redis_conn = get_redis_connection()
    event_handler = NewFileHandler(data_dir, redis_conn)
    observer = Observer()
    observer.schedule(event_handler, str(data_dir), recursive=False)
    observer.start()
    logger.info(f"Started watching directory: {data_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # This allows running the file watcher as a standalone script
    # You would configure the path to your vessel data directory
    # For example: /path/to/your/project/data/vessel_arrivals
    data_directory = Path(__file__).parent.parent.parent / "data" / "vessel_arrivals"
    start_file_watcher(data_directory)