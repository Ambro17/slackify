FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y nano git

COPY requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt

COPY . /app
WORKDIR /app

RUN python setup.py develop

CMD "/bin/bash"
