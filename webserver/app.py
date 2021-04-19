from flask import *
from flask_bootstrap import Bootstrap
from jinja2 import Template
import sqlite3 as db


DB_Pathname = r".\..\SQLite_bookstore.db"
# create a connection to the SQLite Database
# @param {Pathname} db_file: The filename to connect to or create.
# @return {SQLite3 Connection Object} conn: the database connection.
def create_connection():
    conn = None
    try:
        conn = db.connect(DB_Pathname)
        return conn
    except Error as e:
        print(e)
        return e


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("template.html")

@app.route("/popular-books")
def view_popular_books():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM (SELECT * FROM BookStats ORDER BY copies_sold LIMIT 100) INNER JOIN Books;")

    rows = cur.fetchall()
    return render_template("view_popular.html", top100=rows)


@app.route("/recommended-books")
def view_recommended_books():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM (SELECT * FROM BookStats ORDER BY copies_sold LIMIT 100) INNER JOIN Books;")

    rows = cur.fetchall()
    return render_template("view_popular.html", top100=rows)
    
if __name__ == "__main__":
    #conn = create_connection()
    app.run(debug=True)