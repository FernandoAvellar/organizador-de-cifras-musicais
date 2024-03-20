from flask import flash
from flask import redirect, session, flash
from functools import wraps
import os
import psycopg2
from psycopg2 import Error


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/index")
        return f(*args, **kwargs)

    return decorated_function


class DatabaseUtility:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
            )
            self.cursor = self.connection.cursor()

        except (Exception, Error) as err:
            flash("Error while connecting to database", 'error')
            print("Error while connecting to database:", err)
            self.cursor = None
            self.connection = None

        print("Opened database connection")

    def close(self):
        if self.connection and self.cursor:
            self.cursor.close()
            self.connection.close()
            print("Closed database connection")
        else:
            print("No active database connection")
