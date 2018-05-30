FROM python:3.6

WORKDIR /app

COPY requirements*.txt /app/
RUN pip install -r requirements.txt && pip install -r requirements.molotov.txt

ADD . /app

RUN bunzip2 /app/demo/db.sql.bz2

COPY --from=opbeans/opbeans-frontend:latest /app/build /app/opbeans/static/build

CMD ["honcho", "start"]
