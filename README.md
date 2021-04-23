# Valheim backup utilities

## why?

Valheim itself offers no backup tools, but it has been reported that through a
bug lots of people have lost their world and their character. Taking a look at
the directory with the valheim files, there are already .old files for both
world and character, which in many cases is enough to restore. But there might
be the case where one wants to restore an older snapshot of his/her progress
through valheim.

This tool implements a watcher, that runs in the backgound, becomes active
every 5 minutes, then watches the valheim world and character files and creates
a backup right after the game itself has written the files (which also happens
periodically).

## Usage

Either build and use the docker container (see below) or do the following:

```bash
# open a terminal

git clone $URL
cd valheim-utils

# optional: create and/r activate a virtual environment
pip install requirements.txt

python valheim_backup.py --help

python valheim_backup.py \
    --source $HOME/.config/unity3d/IronGate/Valheim
    --destination $HOME//valheim_backup \
    --verbose

# do not close the terminal
```

You are done. Now start Valheim and enjoy playing.

ctrl-c stops the backup utility at any time.

## Docker container

This utility uses inotify which is not available for Windows and macOS, but at
least on macOS, where docker desktop runs docker through a transparent linux
VM, inotify can be used.

I've tested and it runs, but with no valheim installation available on my
macOS, I was not able to end-to-end test if it really works.  Maybe someone can
give me some clarification.

Depending on how docker runs on Windows, it might also work on Windows. Again -
comments if this is actually possible are greatly appreciated.

Important is to first pass the real (docker-external) source and destination to
the docker container as volumes, then set the docker-internal paths as source
and destination parameters as shown in the example below.

```bash
docker build -t valheim_backup:latest .

docker run run -it --rm \
    -v $(pwd)/testdir:/usr/src/app/valheim \
    -v $(pwd)/backup:/backup \
    --name valheim_bck valheim_backup:latest \
    --source /usr/src/app/valheim \
    --destination /backup \
    --verbose
```

## Restore

The backups contain either the world or the character files. To restore
whichever you need, just extract them from the tgz file of your choice and copy
them into the worlds or characters directory.

For safety precautions, create a backup of the files there before overwriting
them!

You do this at your own risk!

## Author

Sven Hergenhahn <svenxy@gmx.net>
