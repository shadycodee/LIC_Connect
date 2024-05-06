from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask import jsonify

app = Flask(__name__)

# Set a secret key for the application when using 'flash'
app.secret_key = 'qWer#123ty'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'records'

mysql = MySQL(app)

#admin login credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Define a list of routes that do not require authentication
# You can add more routes if needed
NO_AUTH_REQUIRED_ROUTES = ['admin_login', 'student_login']

def convert_minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}:00"

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']


        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin_login.html', message='Invalid Credentials')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('authenticated', None)
    return redirect(url_for('admin_login'))

@app.route('/record', methods=['GET']) 
def showhistory():

    studentid = session.get('studentid')
    cur = mysql.connection.cursor()
    cur.execute("SELECT studentid, login_time, logout_time, consumed_time FROM login_sessions WHERE studentid = %s", (studentid,))
    login_sessions = cur.fetchall()
    cur.close()


    login_sessions = [(record[0], record[1].strftime('%Y-%m-%d %H:%M:%S') if record[1] else None, record[2].strftime('%Y-%m-%d %H:%M:%S') if record[2] else None, record[3]) for record in login_sessions]
    return render_template('history.html', login_sessions=login_sessions)
@app.route('/history', methods=['POST'])
def handle_request():
    data = request.get_json()
    id = str(data.get('get'))
    session['studentid'] = id
    print("studentid in handle_request = " + id)
    return redirect(url_for('dashboard', studentid = id))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():    

    if request.method == 'POST':
        studentid = request.form['studentid']
        name = request.form['name']
        password = request.form['password']
        course = request.form['course']

        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (studentid, name, password, course) VALUES (%s, %s, %s, %s)",
                    (studentid, name, password, course))
        mysql.connection.commit()
        cur.close()
        # Flash a success message after successful registration
        flash('Student registered successfully!', 'success')
        # Redirect to the 'manage' route (GET) after successful registration
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT studentid, name, course, time_left FROM students")
    students = cur.fetchall()
    cur.close()

    students = [(student[0], student[1], student[2], convert_minutes_to_time(student[3])) for student in students]

    # studentid = session.get('studentid')
    studentid = 'test'
    print("studentid in dashboard = " + studentid)
    cur = mysql.connection.cursor()
    cur.execute("SELECT studentid, login_time, logout_time, consumed_time FROM login_sessions WHERE studentid = %s", (studentid,))
    login_sessions = cur.fetchall()
    cur.close()

    login_sessions = [(record[0], record[1].strftime('%Y-%m-%d %H:%M:%S') if record[1] else None, record[2].strftime('%Y-%m-%d %H:%M:%S') if record[2] else None, record[3]) for record in login_sessions]

    return render_template('dashboard.html', students=students, login_sessions=login_sessions)




# @app.route('/process_student_id', methods=['POST'])
# def process_student_id():
#     data = request.get_json()
#     student_id =data['student_id']

@app.route('/login')
def student_login():
    return render_template('student_login.html')

@app.before_request
def require_auth():
    # Check if the user is trying to access a route that does not require authentication
    if request.endpoint in ['admin_login']:
        return

    # Check if the user is authenticated
    if not session.get('authenticated'):
        # If not authenticated, redirect to the admin login page
        return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(debug=True)