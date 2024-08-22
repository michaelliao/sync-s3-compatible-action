FROM python:3.12-slim

WORKDIR /app

COPY *.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["python", "/app/sync.py"]
