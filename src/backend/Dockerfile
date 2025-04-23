ARG BASE_IMAGE=python:3.13-alpine
ARG API_SERVER_PORT=${API_SERVER_PORT:-8000}

FROM ${BASE_IMAGE} AS build

WORKDIR /app

COPY src/backend/requirements.txt /app/

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY src/backend/* /app/

EXPOSE ${API_SERVER_PORT}

CMD ["fastapi", "run", "main.py"]
