import sys
import os
import logging
import argparse
from glob import glob
import tarfile
from pathlib import Path
from datetime import datetime
from pytz import timezone
import inotify.adapters
from twisted.internet.task import LoopingCall
from twisted.internet import reactor, defer
from twisted.python import log

LOOP_TIME = 300 # seconds
SUFFIXES = ['db', 'fch']
EVENT='IN_MOVED_TO'
NONEEVENT= ['IN_ACCESS']
FORMAT = '%(asctime)s %(levelname)s %(message)s'

def parse_args(args):
    parser = argparse.ArgumentParser(
            description='Regularly backup valheim world and character files after changes',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source', '-s',
            default=f"{os.environ['HOME']}/.config/unity3d/IronGate/Valheim",
            help='Your valheim data directory')
    parser.add_argument('--destination', '-D',
            default='.',
            help='Where to write the bckup files')
    parser.add_argument('--time', '-t',
            default=LOOP_TIME,
            dest='loop_time',
            help='Time after which the loop is restarted')
    parser.add_argument('--verbose', '-v',
            dest='loglevel', action='store_const',
            const=logging.INFO,
            default=logging.WARNING,)
    parser.add_argument('--debug', '-d',
            dest='loglevel',
            action='store_const',
            const=logging.DEBUG,)
    return parser.parse_args()

def errback(message):
    logger.warning('Nothing found %s' % message)

def backup_loop():
    logger.debug('Entering loop...')
    modified = detect_save_cycle([VALHEIM_WORLDS, VALHEIM_CHARS], SUFFIXES)
    if modified:
        backup(modified, BACKUP_PATH)

def detect_save_cycle(paths, suffixes=SUFFIXES):
    logger.debug('Entering detect...')
    savefiles = []
    i = inotify.adapters.Inotify()
    for path in paths:
        i.add_watch(str(path))
    for event in i.event_gen(yield_nones=False, timeout_s=LOOP_TIME - 10):
        (_, type_names, path, filename) = event
        suffix = filename.split('.')[-1]
        if EVENT not in NONEEVENT:
            logger.debug('Event detected: %s on %s', ','.join(type_names), filename)
        if EVENT in type_names and suffix in suffixes:
            logger.info('Found event %s and will consider %s' % (','.join(type_names), filename))
            savefiles.append(Path(path) / filename)
            if suffix == 'db':
                logger.info('World has ben updated, starting backup for all detected modified files')
                return savefiles
    logger.info('End of cycle reached without detecting relevant file changes, waiting for next cycle to start')
    return None

def backup(files, backup_path):
    for filepath in files:
        try:
            item = filepath.stem
            kind = filepath.parent.stem
            now = datetime.now().astimezone().strftime("%Y-%m-%d_%H:%M:%S")
            zipdest = f'{backup_path}/{item}-{kind}-{now}.tgz'
            with tarfile.open(zipdest, "w:gz") as tar:
                for i in glob(f'{filepath.parent}/{item}.*'):
                    tar.add(i, arcname=Path(i).name)
            logger.info('Backup written to %s' % zipdest)
        except Exception:
            logger.exception('Failed to write backup to %s', zipdest)

def start_logging(level):
    logging.basicConfig(
            level=level,
            format=FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S')
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Berlin')).timetuple()
    return logging.getLogger('valheimBackup')

if __name__ == '__main__':

    # configure...
    args = parse_args(sys.argv[1:])
    VALHEIM_WORLDS = Path(args.source) / 'worlds'
    VALHEIM_CHARS  = Path(args.source) / 'characters'
    BACKUP_PATH = Path(args.destination)

    # make sure all logging output properly
    logger = start_logging(args.loglevel)
    observer = log.PythonLoggingObserver()
    observer.start()
    logger.info('Background backup process started in %s', args.source)

    # start the loop
    lc = LoopingCall(backup_loop)
    d = lc.start(args.loop_time)
    d.addErrback(errback)

    reactor.run()
