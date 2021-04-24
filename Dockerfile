FROM python:3.7.3-slim

ENV PYTHONBUFFERED 1
ENV DATABASE /data/db.sqlite
ENV LOGFILE /data/prod.log

WORKDIR /app

COPY init.sql .
COPY main.py .
COPY requirements.txt .

EXPOSE 443

RUN pip3 install -r requirements.txt

ENTRYPOINT ["gunicorn", "-w", "2", "--keyfile", "/tls/privkey.pem", "--certfile", "/tls/cert.pem", "--ca-certs",  "/tls/chain.pem", "--threads", "2", "-b",  "0.0.0.0:443", "main:app"]
