FROM python:3.6

WORKDIR /app

COPY requirements*.txt /app/
RUN pip install -r requirements.txt

ADD . /app

COPY --from=opbeans/opbeans-frontend:latest /app /app/opbeans/static

RUN cp /app/opbeans/static/build/index.html /app/opbeans/templates/

EXPOSE 3000

CMD ["honcho", "start"]
