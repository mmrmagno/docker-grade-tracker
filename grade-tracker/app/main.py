from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('grade-tracker/grades.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_db_cursor(connection):
    return connection.cursor()

@app.template_filter('enumerate')
def enumerate_filter(values):
    return zip(range(1, len(values) + 1), values)

@app.template_filter('average')
def average_filter(numbers):
    if numbers:
        return sum(numbers) / len(numbers)
    return 0

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        subject = request.form['subject']
        grade = float(request.form['grade'])

        conn = get_db_connection()
        c = get_db_cursor(conn)

        c.execute("INSERT INTO grades VALUES (?, ?)", (subject, grade))
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



if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
