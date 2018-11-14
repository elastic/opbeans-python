FROM python:3.6

WORKDIR /app

COPY requirements*.txt /app/
RUN pip install -r requirements.txt

ADD . /app

COPY --from=opbeans/opbeans-frontend:latest /app /app/opbeans/static

RUN sed 's/<head>/<head>{% block head %}{% endblock %}/' /app/opbeans/static/build/index.html | sed 's/<script type="text\/javascript" src="\/rum-config.js"><\/script>//' > /app/opbeans/templates/base.html

EXPOSE 3000

CMD ["honcho", "start"]
