import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from config import get_config
from client import EchoClient


class LoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""
    watched = {}
    def __init__(self, watched, ws):
        self.watched = watched
        self.ws = ws

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)
        if(event.src_path in self.watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)
        if(event.src_path in self.watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)
        if(event.src_path in self.watched.values()):
            what = 'directory' if event.is_directory else 'file'
            logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        if(event.src_path in self.watched.keys()):
            title = self.watched[event.src_path]
            with open(event.src_path, 'r') as f:
                f.seek (0, 2) 
                fsize = f.tell()   
                f.seek (max (fsize-1024, 0), 0)
                lines = f.readlines()
                line = lines[-1:]    
                #what = 'directory' if event.is_directory else 'file'
                ws.send("%s ::: %s" % (title, line[0]))
                #print("%s ::: %s" % (title, line[0]))




if __name__ == "__main__":

    files, folders = get_config()
    
    ws = EchoClient('http://localhost:8080/ws')
    ws.connect()

    logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s - %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = LoggingEventHandler(files, ws)
    observer = Observer()
    for f in folders:
        observer.schedule(event_handler, f, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        ws.close(reason='Canceled')
