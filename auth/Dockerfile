FROM python:3.12-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential libpq-dev \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python3", "src/server.py"]