FROM python:3.13.0

WORKDIR /app

RUN python -m venv /app/venv
COPY requirements.txt /app
RUN /app/venv/bin/pip install -U pip setuptools && \
    /app/venv/bin/pip install -r requirements.txt

FROM python:3.13.0-slim
COPY . /app
COPY --from=0 /app/venv /app/venv
RUN mkdir -p /app/opbeans/static/
COPY --from=opbeans/opbeans-frontend:latest /app/build /app/opbeans/static/build
## To get the client name/version from package.json
COPY --from=opbeans/opbeans-frontend:latest /app/package.json /app/opbeans/static/package.json

WORKDIR /app
ENV PATH="/app/venv/bin:$PATH"

## curl is required for healthcheck, bzip2 to unzip the sqlite database
RUN apt-get -qq update \
 && apt-get -qq install -y \
    bzip2 \
    curl \
	--no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

RUN sed 's/<head>/<head>{% block head %}{% endblock %}/' /app/opbeans/static/build/index.html | sed 's/<script type="text\/javascript" src="\/rum-config.js"><\/script>//' > /app/opbeans/templates/base.html

# init demo database
RUN mkdir -p /app/demo \
    && DATABASE_URL="sqlite:////app/demo/db.sql" python ./manage.py migrate

ENV ENABLE_JSON_LOGGING=True
ENV ELASTIC_APM_USE_STRUCTLOG=True

EXPOSE 3000

LABEL \
    org.label-schema.schema-version="1.0" \
    org.label-schema.vendor="Elastic" \
    org.label-schema.name="opbeans-python" \
    org.label-schema.version="6.23.0" \
    org.label-schema.url="https://hub.docker.com/r/opbeans/opbeans-python" \
    org.label-schema.vcs-url="https://github.com/elastic/opbeans-python" \
    org.label-schema.license="MIT"

CMD ["honcho", "start", "--no-prefix"]
