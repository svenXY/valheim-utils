FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./valheim_backup.py .
COPY ./valheim_inotify.py .

CMD [ "python", "./valheim_backup.py" ]
#CMD [ "python", "./valheim_inotify.py" ]
