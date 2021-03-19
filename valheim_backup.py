import logging
from glob import glob
import tarfile
from pathlib import Path
from datetime import datetime
from pytz import timezone
import inotify.adapters
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

#VALHEIM_PATH = Path('~/.config/valheim')
VALHEIM_PATH = Path('./testdir')
VALHEIM_WORLDS = VALHEIM_PATH / 'worlds'
VALHEIM_CHARS = VALHEIM_PATH / 'characters'
BACKUP_PATH = VALHEIM_PATH / 'backup'

EVENT='IN_MODIFY'

def _main():
    lc = LoopingCall(backup_world)
    lc.start(600)

    lc2 = LoopingCall(backup_character)
    lc2.start(300)

    reactor.run()

def backup_world():
    WORLDFILE = detect_state(VALHEIM_WORLDS, '.db')
    backup('world', WORLDFILE, BACKUP_PATH)

def backup_character():
    CHARFILE = detect_state(VALHEIM_CHARS, '.fwl')
    backup('character', CHARFILE, BACKUP_PATH)

def detect_state(path, suffix):
    i = inotify.adapters.Inotify()
    i.add_watch(str(path))
    for event in i.event_gen(yield_nones=False, timeout_s=280):
        (_, type_names, path, filename) = event
        if EVENT in type_names and filename.endswith(suffix):
            return Path(path) / filename

def backup(kind, filepath, backup_path):
    item = filepath.stem
    now = datetime.now().astimezone().strftime("%Y-%m-%d_%H:%M:%S")
    zipdest = f'{backup_path}/{item}-{kind}-{now}.tgz'
    with tarfile.open(zipdest, "w:gz") as tar:
        for i in glob(f'{filepath.parent}/{item}.*'):
            tar.add(i, arcname=Path(i).name)

def start_logging():
    logging.basicConfig(level=logging.DEBUG)
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    return logging.getLogger('_main_')

if __name__ == '__main__':
    logger = start_logging()
    _main()

