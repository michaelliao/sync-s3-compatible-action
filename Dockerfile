FROM python:3.12-slim

WORKDIR /app

RUN pip install boto3 oss2 cos-python-sdk-v5 bce-python-sdk

COPY *.py /app/

CMD ["python", "/app/sync.py"]
