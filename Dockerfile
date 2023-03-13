FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update \
    && apt-get install -y netcat

RUN pip install --upgrade pip
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code/

CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT