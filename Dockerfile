FROM node:latest as client

LABEL lastupdate="2018-05-30"
ENV ELASTIC_APM_JS_BASE_SERVICE_VERSION="v${lastupdate}"
ENV NODE_ENV=production
ENV ELASTIC_APM_JS_BASE_SERVICE_NAME=opbeans-python-react

RUN git clone -b master https://github.com/elastic/opbeans-frontend /client
RUN cd client && npm install && npm run-script build

FROM python:3.6

WORKDIR /app

COPY requirements*.txt /app/
RUN pip install -r requirements.txt && pip install -r requirements.molotov.txt

ADD . /app

RUN bunzip2 /app/demo/db.sql.bz2

COPY --from=client /client/build /app/opbeans/static/build

CMD ["honcho", "start"]
