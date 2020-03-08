FROM python:3.7.6-slim-buster
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y iputils-ping git
RUN pip install --no-cache-dir -r ./requirements.txt
CMD ["python", "./src/main/stock/main/stock_client.py"]