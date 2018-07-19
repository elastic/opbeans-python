FROM python:3.6

WORKDIR /app

COPY requirements*.txt /app/
RUN pip install -r requirements.txt

ADD . /app

RUN bunzip2 /app/demo/db.sql.bz2

COPY --from=opbeans/opbeans-frontend:latest /app/build /app/opbeans/static/build

RUN cp /app/opbeans/static/build/index.html /app/opbeans/templates/

CMD ["honcho", "start"]
