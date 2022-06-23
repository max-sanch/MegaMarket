FROM python:3.9.5-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN apt-get update && apt-get install netcat -y

COPY ./ ./

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]