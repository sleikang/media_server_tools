FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN pip install --index-url https://nexus3.smwap.top:88/repository/python/simple network
RUN pip install --index-url https://nexus3.smwap.top:88/repository/python/simple system

CMD ["python", "main.py"]
