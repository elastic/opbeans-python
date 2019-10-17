FROM python:3.6-slim

WORKDIR /app

## Required as the slim version is too tiny
RUN apt-get -qq update \
 && apt-get -qq install -y \
	gcc \
    libc-dev \
    bzip2 \
    curl \
	--no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

COPY requirements*.txt /app/
RUN pip install -r requirements.txt

COPY . /app

COPY --from=opbeans/opbeans-frontend:latest /app /app/opbeans/static

RUN sed 's/<head>/<head>{% block head %}{% endblock %}/' /app/opbeans/static/build/index.html | sed 's/<script type="text\/javascript" src="\/rum-config.js"><\/script>//' > /app/opbeans/templates/base.html

# init demo database
RUN mkdir /app/demo \
    && DATABASE_URL="sqlite:////app/demo/db.sql" python ./manage.py migrate

ENV ENABLE_JSON_LOGGING=True
ENV ELASTIC_APM_USE_STRUCTLOG=True

EXPOSE 3000

CMD ["honcho", "start", "--no-prefix"]
