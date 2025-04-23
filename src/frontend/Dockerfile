ARG BASE_IMAGE=python:3.13-slim
ARG STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}

# Stage: build
FROM ${BASE_IMAGE} AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        software-properties-common \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY src/frontend/requirements.txt /app/

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Stage: production
FROM ${BASE_IMAGE} AS production

WORKDIR /app

COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin/* /usr/local/bin/
COPY src/frontend/main.py /app/

EXPOSE ${STREAMLIT_SERVER_PORT}

HEALTHCHECK CMD curl --fail http://localhost:${STREAMLIT_SERVER_PORT}/_stcore/health

CMD ["streamlit", "run", "main.py"]
