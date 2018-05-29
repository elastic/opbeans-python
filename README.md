# Opbeans for Ponies

This is an implementation of the [Opbeans Demo app](http://opbeans.com) in Django. It uses the same
database schema as the [Node](https://github.com/opbeat/opbeans) version.

The database settings are provided via environment variable, like so:

    DATABASE_URL=postgres://user:password@host:port/dbname ./manage.py runserver

## Installation

**Note**: We highly recommend to use Python 3.5+

Create a `virtualenv` with your preferred tooling, then install the requirements:

    python -m pip install -r requirements.txt
    
If you want to use Celery, you'll also need to set up a Redis instance.
The easiest way for local development is via docker:

    docker run -p 6379:6379 redis


## Demo Data

There's a compressed SQLite database in the `demo` directory. You can run it like this:

    bunzip2 -k demo/db.sql.bz2
    ./manage.py collectstatic
    DATABASE_URL=sqlite://./demo/db.sql ./manage.py runserver

There's an admin user, `barista`/`affogato`.