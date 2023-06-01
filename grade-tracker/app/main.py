from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from passlib.hash import bcrypt
import os
import functools
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def get_db_connection():
    conn = sqlite3.connect('grade-tracker/grades.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_cursor(connection):
    return connection.cursor()


def create_users_table():
    conn = get_db_connection()
    c = get_db_cursor(conn)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    c.close()
    conn.close()


create_users_table()


def add_user(username, password):
    conn = get_db_connection()
    c = get_db_cursor(conn)

    hashed_password = bcrypt.hash(password)

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
              (username, hashed_password))
    conn.commit()

    c.close()
    conn.close()


add_user('admin', 'admin')


def enumerate_filter(values):
    return zip(range(1, len(values) + 1), values)


def average_filter(values):
    return sum(values) / len(values)


app.jinja_env.filters['enumerate'] = enumerate_filter
app.jinja_env.filters['average'] = average_filter


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session or not session.get('logged_in'):
            return redirect('/login')
        return view(**kwargs)

    return wrapped_view


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = get_db_cursor(conn)

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        c.close()
        conn.close()

        if user and bcrypt.verify(password, user['password']):
            session['username'] = user['username']
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        subject = request.form['subject']
        grade = float(request.form['grade'])

        conn = get_db_connection()
        c = get_db_cursor(conn)

        c.execute("INSERT INTO grades (subject, grade) VALUES (?, ?)", (subject, grade))
        conn.commit()

        c.close()
        conn.close()

    conn = get_db_connection()
    c = get_db_cursor(conn)

    c.execute("SELECT subject, grade FROM grades")
    rows = c.fetchall()
    subjects = {}
    for row in rows:
        subject = row['subject']
        grade = row['grade']
        if subject in subjects:
            subjects[subject].append(grade)
        else:
            subjects[subject] = [grade]

    c.close()
    conn.close()

    return render_template('index.html', subjects=subjects)


@app.route('/remove', methods=['POST'])
@login_required
def remove():
    subject = request.form['subject']
    selected_grade = request.form['grade']
    grade, index = selected_grade.split('_')
    grade = float(grade)

    conn = get_db_connection()
    c = get_db_cursor(conn)

    c.execute("SELECT rowid FROM grades WHERE subject=? AND grade=?", (subject, grade))
    row = c.fetchone()

    if row:
        rowid = row['rowid']

        c.execute("DELETE FROM grades WHERE rowid=?", (rowid,))
        conn.commit()

    c.execute("SELECT subject, grade FROM grades")
    rows = c.fetchall()
    subjects = {}
    for row in rows:
        subject = row['subject']
        grade = row['grade']
        if subject in subjects:
            subjects[subject].append(grade)
        else:
            subjects[subject] = [grade]

    c.close()
    conn.close()

    return render_template('index.html', subjects=subjects)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
