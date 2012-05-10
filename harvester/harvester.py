import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""
    
    def __init__(self, watched = {}):
        self.watched = watched

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)
        if(event.src_path in watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)
        if(event.src_path in watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)
        if(event.src_path in watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        if(event.src_path in watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Modified %s: %s", what, event.src_path)




if __name__ == "__main__":

    watched = {
        'test' : '/tmp/test.txt'
    }

    logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s - %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = LoggingEventHandler(watched)
    observer = Observer()
    observer.schedule(event_handler, path=sys.argv[1], recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
