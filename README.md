### Opbeans for Ponies

This is an implementation of the [Opbeans Demo app](http://opbeans.com) in Django. It uses the same
database schema as the [Node](https://github.com/opbeat/opbeans) version.

The database settings are provided via environment variable, like so:

    DATABASE_URL=postgres://user:password@host:port/dbname ./manage.py runserver


## Demo Data

There's a compressed SQLite database in the `demo` directory. You can run it like this:

    bunzip2 -k demo/db.sql.bz2
    DATABASE_URL=sqlite://./demo/db.sql ./manage.py runserver

There's an admin user, `barista`/`affogato`.