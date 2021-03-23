import sys
import logging
from glob import glob
import tarfile
from pathlib import Path
from datetime import datetime
from pytz import timezone
import inotify.adapters
from twisted.internet.task import LoopingCall
from twisted.internet import reactor, defer
from twisted.python import log

#VALHEIM_PATH = Path('~/.config/valheim')
VALHEIM_PATH = Path('./testdir')
VALHEIM_WORLDS = VALHEIM_PATH / 'worlds'
VALHEIM_CHARS = VALHEIM_PATH / 'characters'
BACKUP_PATH = VALHEIM_PATH / 'backup'
SUFFIXES = ['db', 'fwl', 'fff']
LOOP_TIME = 300 # seconds

#EVENT='IN_WRITE_CLOSE'
EVENT='IN_MODIFY'

def _main():
    #log.startLogging(sys.stdout)
    observer = log.PythonLoggingObserver()
    observer.start()

    lc = LoopingCall(backup_loop)
    d = lc.start(LOOP_TIME)
    d.addErrback(errback)

    reactor.run()

def errback(message):
    log.msg('Nothing found %s' % message)

def backup_loop():
    modified = detect_state([VALHEIM_WORLDS, VALHEIM_CHARS], SUFFIXES)
    if modified:
        backup(modified, BACKUP_PATH)

def detect_state(paths, suffixes=SUFFIXES):
    i = inotify.adapters.Inotify()
    for path in paths:
        i.add_watch(str(path))
    for event in i.event_gen(yield_nones=False, timeout_s=LOOP_TIME - 10):
        (_, type_names, path, filename) = event
        if EVENT in type_names and filename.split('.')[-1] in suffixes:
            logger.info('Found event %s and will start backup of %s' % (','.join(type_names), filename))
            return Path(path) / filename

def backup(filepath, backup_path):
    log.msg('Starting backup for %s' % filepath)
    item = filepath.stem
    kind = filepath.parent.stem
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

