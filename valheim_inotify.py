from pathlib import Path
import inotify.adapters
import logging
from pytz import timezone
from datetime import datetime


#VALHEIM_PATH = Path('~/.config/valheim')
VALHEIM_PATH = Path('./testdir')
VALHEIM_WORLDS = VALHEIM_PATH / 'worlds'
VALHEIM_CHARS = VALHEIM_PATH / 'characters'
BACKUP_PATH = VALHEIM_PATH / 'backup'

EVENT='IN_MODIFY'

def _main():
    WORLDFILE = detect_state(VALHEIM_WORLDS, '.db')

def detect_state(path, suffix):
    i = inotify.adapters.Inotify()
    i.add_watch(str(path))

    for event in i.event_gen(yield_nones=False, timeout_s=60):
        (_, type_names, path, filename) = event

        logger.debug("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))

def start_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s' )
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    return logging.getLogger('_main_')

if __name__ == '__main__':
    logger = start_logging()
    _main()

