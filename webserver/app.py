from flask import *
from flask_bootstrap import Bootstrap
from jinja2 import Template
import sqlite3 as db
import os
import hashlib
from time import strftime



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
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=(?)", (username,))
        user = cur.fetchone()
        cur.execute("SELECT * FROM Users WHERE email=(?)", (email,))
        userEmail = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM Users")
        row = cur.fetchone()
        numUsers = int(row[0])
        if (user is None and userEmail is None):
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            store_pass = salt + key
            userID = numUsers + 1
            cur.execute("INSERT INTO Users (id, password, username, email, role) VALUES((?), (?), (?), (?), (?));", (userID, store_pass, username, email, 'default'))  
            conn.commit()
            resp = make_response(redirect(url_for('home')))
            session['user_id'] = userID
            resp.set_cookie('user_id', str(numUsers+1))
            return resp
        else:
            flash('Signup failed')
            return render_template("signup.html")
    elif request.method == 'GET':
        return render_template("signup.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=(?)", (username,))
        user = cur.fetchone()
        if (user is None):
            flash('Login failed')
            return render_template("login.html")
        else:
            store_pass = user[1]
            salt = store_pass[:32]
            key = store_pass[32:]
            check_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            if key == check_key:
                resp = make_response(redirect(url_for('home')))
                flash('You were successfully logged in')
                print(user[0])
                print("log in success")
                session['user_id'] = user[0]
                return resp
            else:
                flash('Login failed')
                return render_template("login.html")
    elif request.method == 'GET':
        if request.args.get('logout'):
            flash("You were successfully logged out")
            resp = make_response(redirect(url_for('home')))
            session.pop('user_id',None)
            return resp
        return render_template("login.html")

@app.route("/logout")
def logout():
    if request.method == 'POST':
        session.pop('user_id', default=None)
        flash('You were successfully logged out')
        return redirect(url_for('home'))


@app.route("/popular-books")
def view_popular_books():
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM (SELECT id as thisID FROM BookStats ORDER BY copies_sold LIMIT 100) INNER JOIN Books ON id = thisID;")
    rows = cur.fetchall()
    print(rows[0])
    return render_template("view_popular.html", book_list=rows)


@app.route("/highly-rated-books")
def view_highly_rated_books():
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM BookRatings INNER JOIN Books ON book_id = Books.id")
    rows = cur.fetchall()
    return render_template("view_popular.html", book_list=rows)

@app.route("/view-book")
def view_book():
    bookID = int(request.args.get('bookID'))
    conn = create_connection()
    conn.row_factory = db.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books INNER JOIN AuthorWrites ON AuthorWrites.book_id = Books.id INNER JOIN Authors ON AuthorWrites.author_id = Authors.id WHERE Books.id = (?)", (bookID,))
    rows = cur.fetchall()
    if not rows:
        flash("Book not found")
        return redirect(url_for('home'))
    authors = []
    thisBook = dict(rows[0])
    for book in rows:
        authors.append(book['name'])
    thisBook['name'] = ", ".join(authors)
    cur.execute("SELECT id, first_name, last_name, score, content, Comments.timestamp, avg_rating FROM Comments INNER JOIN Customers ON Comments.user_id = Customers.user_id LEFT JOIN (SELECT AVG(Ratings.value) as avg_rating, comment_id FROM Ratings GROUP BY comment_id) ON Comments.id = comment_id WHERE book_id=(?) ", (bookID,))
    return render_template("view_book.html", book=thisBook, comments=cur.fetchall())

@app.route('/cart')
def cart():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Books INNER JOIN Cart ON Books.id = Cart.book_id WHERE Cart.user_id = (?)", (userID,))
        rows = cur.fetchall()
        return render_template('cart.html', book_list = rows)

@app.route('/updateItem', methods = ['POST'])
def updateItem():
        if request.method == 'POST':
            bookID = request.form['bookID']
            if bookID is None:
                return redirect(url_for('cart'))
            quantity = int(request.form['quantity'])
            if not session.get('user_id'):
                return redirect(url_for('login'))
            userID = session['user_id']
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Cart WHERE book_id = (?) AND user_id = (?)", (bookID, userID))
            row = cur.fetchone()
            if row is None:
                if quantity == 0:
                    return redirect(url_for('cart'))
                else:
                    cur.execute("INSERT INTO Cart (book_id, user_id, quantity) VALUES ((?), (?), (?))", (bookID, userID, 1))
            else:
                if quantity == 0:
                    cur.execute("DELETE FROM Cart WHERE book_id = (?) AND user_id = (?)", (bookID, userID))
                else:
                    cur.execute("UPDATE Cart SET quantity = (?) WHERE book_id = (?) AND user_id = (?)", (quantity, bookID, userID))
            conn.commit()
            return redirect(url_for('cart'))

@app.route('/trusts', methods = ['POST', 'GET'])
def trusts():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT value, username FROM Trusts INNER JOIN Users ON Trusts.trusts = Users.id WHERE Trusts.user_id = (?)", (userID,))
        rows = cur.fetchall()
        return render_template("trustedUsers.html", trustedUsers = rows)

@app.route('/updateRating', methods = ['POST'])
def updateRating():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        commentID = request.form['comment_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Ratings WHERE user_id = (?) AND comment_id = (?);", (userID, commentID))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO Ratings (user_id, comment_id, value, timestamp) Values((?), (?), (?), (?));", (userID, commentID, request.form['value'], strftime("%Y-%m-%d %H:%M:%S")))
        else:
            cur.execute("UPDATE Ratings SET value = (?), timestamp = (?) WHERE user_id = (?) AND comment_id = (?);", (request.form['value'], strftime("%Y-%m-%d %H:%M:%S"), userID, commentID))
        conn.commit()
        flash("Rating updated.")
        return redirect(request.referrer)


@app.route('/myOrders', methods = ['POST', 'GET'])
def myOrders():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session.get('user_id')
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Orders INNER JOIN Addresses ON Orders.ships_to = Addresses.id INNER JOIN Customers ON Customers.user_id = Addresses.user_id INNER JOIN OrderItems ON OrderItems.order_id = Orders.id INNER JOIN Books ON OrderItems.book_id = Books.id WHERE Customers.user_id = (?);", (userID,))
        rows = cur.fetchall()
        return render_template('orders.html', orders = rows)

@app.route('/addresses', methods = ['POST', 'GET'])
def updateAddress():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()


@app.route('/rating', methods = ['POST', 'GET'])
def rating():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))

# ACCESS FOR EMPLOYEES ONLY
@app.route('/orders', methods = ['POST', 'GET'])
def orders():
    if not session.get('user_id'):
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        conn = create_connection()
        conn.row_factory = db.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE id = (?)", (userID,))
        row = cur.fetchone()
        if row is None:
            flash("You must be logged in!")
            return redirect(url_for('login'))
        elif row['role'] == "default":
            flash("You do not have permission!")
            return redirect(url_for('login'))
        elif row['role'] == "employee" or row['role'] == "manager":
            cur.execute("SELECT * FROM Orders INNER JOIN Addresses ON Orders.ships_to = Addresses.id INNER JOIN Customers ON Customers.user_id = Addresses.user_id INNER JOIN OrderItems ON OrderItems.order_id = Orders.id INNER JOIN Books ON OrderItems.book_id = Books.id WHERE time_fulfilled IS NULL;")
            rows = cur.fetchall()
            flash("Viewing unfulfilled Orders")
            return render_template('orders.html', orders = rows)

# ACCESS FOR MANAGERS ONLY
""" @app.route('/addBook', methods = ['POST', 'GET'])
def addBook():

@app.route('/modifyBook', methods = ['POST', 'GET'])
def modifyBook():

@app.route('/usefulUsers', methods = ['GET'])
def usefulUsers():

@app.route('/sales', methods = ['GET'])
def sales():

@app.route('/discounts', methods = ['GET'])
def discounts(): """
    
if __name__ == "__main__":
    app.secret_key = 'SECRETKEYDONTLOSE'
    app.run(debug=True)