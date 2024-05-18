from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask import jsonify
from flask_login import login_required, LoginManager
from flask import flash

app = Flask(__name__)

# Set a secret key for the application when using 'flash'
app.secret_key = 'qWer#123ty'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'vlackhole'
app.config['MYSQL_DB'] = 'records'

mysql = MySQL(app)

# Define a list of routes that do not require authentic

def convert_minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}:00"


## for admin settingss
def update_admin_password(new_password):
    # Create a cursor object
    cur = mysql.connection.cursor()

    cur.execute("UPDATE admin SET password = %s WHERE username = 'admin'", (new_password,))
    mysql.connection.commit()
    cur.close()


# Route to check current password
@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data.get('password')
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM admin WHERE username = 'admin'")
    result = cur.fetchone()
    cur.close()

    if result is None:
        return jsonify({'correct': False}), 400

    stored_password = result[0]

    if password == stored_password:
        return jsonify({'correct': True})
    else:
        return jsonify({'correct': False}), 400

# Settings route
@app.route('/admin_settings', methods=['GET', 'POST'])
def admin_settings():
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM admin WHERE username = 'admin'")
        result = cur.fetchone()
        cur.close()

        if result is None:
            flash('Invalid Credentials', 'error')
            return redirect(url_for('admin_settings'))

        stored_password = result[0]

        if current_password != stored_password:
            flash('Incorrect Current Password', 'error')
            return redirect(url_for('admin_settings'))

        if new_password != confirm_password:
            flash('New Password and Confirm Password do not match', 'error')
            return redirect(url_for('admin_settings'))

        cur = mysql.connection.cursor()
        cur.execute("UPDATE admin SET password = %s WHERE username = 'admin'", (new_password,))
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully', 'success')
        return redirect(url_for('admin_settings'))

    return render_template('adminSettings.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']

        # Create a cursor object
        cur = mysql.connection.cursor()

        # Execute a query to retrieve the admin credentials
        cur.execute("SELECT username, password FROM admin WHERE username=%s", (username,))
        result = cur.fetchone()
        cur.close()

        if result is None:
            return render_template('admin_login.html', message='Invalid Credentials')

        ADMIN_USERNAME, ADMIN_PASSWORD = result

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