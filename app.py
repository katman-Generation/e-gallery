from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import base64
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'bezel'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Katman'
app.config['MYSQL_PASSWORD'] = 'Katman?1997'
app.config['MYSQL_DB'] = 'Users'

mysql = MySQL(app)


@app.route('/')
def  openingPage():
    """
    this page should include the sell out,
    its the page that tell our visitors about the app.
    and give the options to signin or signup.
    """
    return render_template('index.html')

@app.route('/dispay')
def display():
    msg = ''
    if 'loggedin' in session:
        email = login.email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userData WHERE email = %s', (email))
        data = cursor.fetchall() #{[id:1], [email: admin@example.com],[photo:palace.jpg],[bio: xxxxxxxxx]}
        for row in data:
            bio = row[3]
            image = (row[2])
            return render_template('uploading.html', image = image, bio = bio)
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'fullname' in request.form and 'dateOfBirth' in request.form  and 'email' in request.form and 'password' in request.form and 'repassword' in request.form:
        fullname = request.form['fullname']
        dateOfBirth = request.form['dateOfBirth']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE email = %s', (email, ))
        user = cursor.fetchone()
        
        if user:
            msg = 'account already exist !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', fullname):
            msg = 'Username must contain only characters and numbers !'
        elif not fullname or not password or not email or not dateOfBirth or not repassword:
            msg = 'please fill out the form'
        else:
            if password == repassword:
                password= password
                cursor.execute('INSERT INTO account VALUES (NULL, % s, % s, % s, % s)', (fullname, dateOfBirth, email, password))
                mysql.connection.commit()
                msg =  'you have successfully registered'
                return redirect(url_for('display'))
            else:
                msg = 'The passwords does not match'
    elif request.method == 'POST':
        msg = 'please fill out the form!'
    return render_template('register.html', msg = msg)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            msg = 'logged in successfully !'
            login.email = user['email']
            return redirect(url_for('uploads'))
        else:
            msg = 'Incorrect email / password, please try again !'
    return render_template('sign_in.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))


  
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads', methods=['POST', 'GET'])
def uploads ():
    msg = ''
    if request.method == 'POST':
        file = request.files['file']
        bio = request.form['bio']
        if file.filename == '':
            msg = 'No file selected to upload'
        if bio == '':
            msg = 'please write the bio !'
        if file and allowed_file(file.filename):
            photo = secure_filename(file.filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO userData VALUES(NULL, %s, %s, %s)', (login.email, photo, bio))
            mysql.connection.commit()
            msg = 'you have successful added a memory!'
            return render_template('profile.html', msg = msg)
        else:
            msg = "Allowed image types are - png, jpg, jpeg, gif"
    elif request.method == 'POST':
        msg = 'please select file to be uploaded and write the bio'
    msg = 'please select the file and write the bio'
    return render_template('profile.html', msg = msg)
 
    
    
if __name__ == "__main__":
    app.run(debug=True)