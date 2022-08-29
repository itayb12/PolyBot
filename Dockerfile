FROM python:3.8.12-slim-buster
COPY . /opt/app
WORKDIR /opt/app
ENV export AWS_DEFAULT_REGION=eu-west-1
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python3", "worker.py"]

