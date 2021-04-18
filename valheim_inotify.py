from pathlib import Path
import inotify.adapters
import logging
from pytz import timezone
from datetime import datetime


VALHEIM_PATH = Path('/home/svh/.config/unity3d/IronGate/Valheim')
#VALHEIM_PATH = Path('./testdir')
VALHEIM_WORLDS = VALHEIM_PATH / 'worlds'
VALHEIM_CHARS = VALHEIM_PATH / 'characters'
BACKUP_PATH = VALHEIM_PATH / 'backup'

EVENT='IN_MOVED_TO'

def _main():
    WORLDFILE = detect_state([VALHEIM_WORLDS, VALHEIM_CHARS], '.db')

def detect_state(paths, suffix):
    i = inotify.adapters.Inotify()
    for p in paths:
        i.add_watch(str(p))

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        logger.debug("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))
        if EVENT in type_names:
            logger.info("%s: %s", filename, type_names)

def start_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s' )
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    return logging.getLogger('_main_')

if __name__ == '__main__':
    logger = start_logging()
    _main()

