FROM python:3.9-alpine
MAINTAINER Sven Hergenhahn <svenxy@gmx.net>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./valheim_backup.py .

ENTRYPOINT [ "python", "./valheim_backup.py" ]
