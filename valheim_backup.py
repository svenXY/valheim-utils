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

VALHEIM_PATH = Path('/home/svh/.config/unity3d/IronGate/Valheim')
#VALHEIM_PATH = Path('./testdir')
VALHEIM_WORLDS = VALHEIM_PATH / 'worlds'
VALHEIM_CHARS = VALHEIM_PATH / 'characters'
BACKUP_PATH = '/media/work/valheim'
SUFFIXES = ['db', 'fch']
LOOP_TIME = 300 # seconds

EVENT='IN_MOVED_TO'
NONEEVENT= ['IN_ACCESS']

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
    logger.warning('Nothing found %s' % message)

def backup_loop():
    logger.info('Entering loop...')
    modified = detect_save_cycle([VALHEIM_WORLDS, VALHEIM_CHARS], SUFFIXES)
    if modified:
        backup(modified, BACKUP_PATH)

def detect_save_cycle(paths, suffixes=SUFFIXES):
    logger.info('Entering detect...')
    savefiles = []
    i = inotify.adapters.Inotify()
    for path in paths:
        i.add_watch(str(path))
    for event in i.event_gen(yield_nones=False, timeout_s=LOOP_TIME - 10):
        (_, type_names, path, filename) = event
        suffix = filename.split('.')[-1]
        if EVENT not in NONEEVENT:
            logger.info('Event detected: %s on %s', ','.join(type_names), filename)
            logger.info("Suffix: %s", filename.split('.')[-1])
        if EVENT in type_names and suffix in suffixes:
            logger.info('Found event %s and will consider %s' % (','.join(type_names), filename))
            savefiles.append(Path(path) / filename)
            if suffix == 'db':
                return savefiles
    logger.info('timeout to find active files')
    return None

def backup(files, backup_path):
    for filepath in files:
        log.msg('Starting backup for %s' % filepath)
        logger.info('Starting backup for %s' % filepath)
        item = filepath.stem
        kind = filepath.parent.stem
        now = datetime.now().astimezone().strftime("%Y-%m-%d_%H:%M:%S")
        zipdest = f'{backup_path}/{item}-{kind}-{now}.tgz'
        with tarfile.open(zipdest, "w:gz") as tar:
            for i in glob(f'{filepath.parent}/{item}.*'):
                tar.add(i, arcname=Path(i).name)

def start_logging():
    logging.basicConfig(level=logging.INFO)
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    return logging.getLogger('_main_')

if __name__ == '__main__':
    logger = start_logging()
    _main()

