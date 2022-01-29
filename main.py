import verification
import aesEncryption
from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'secureChatProject'

mysql = MySQL(app)
account_true = False

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        details = request.form
        useremail = details['email']
        
        cur = mysql.connection.cursor()

        useremailTrue = cur.execute("SELECT email FROM login_credentials WHERE email = %s;", [useremail])
        if useremailTrue == 1:
            return redirect(url_for('login'))

        username = details['username']
        usermobile = details['mobile']
        password = details['password']
        
        errorStatus = verification.verifyRegister(username, usermobile, useremail, password)

        clear = errorStatus.count(True)

        if clear != 4:
            message = ['Please enter a valid name!!','Please enter a 10 digit valid mobile number!!', 'Please enter a valid email address!!', 'Please enter a password with min 4 characters or max 15 characters!!']

            for i in range(0,4):
                if errorStatus[i] == True:
                    message[i] = ''

            return render_template('register.html',
                nameError = message[0],
                mobileError = message[1],
                emailError = message[2],
                passwordError = message[3]
            )

        cur.execute("INSERT INTO login_credentials(username, email, mobile, password) VALUES (%s, %s, %s, %s)", (username, useremail, usermobile, password))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('login'))

    return render_template('register.html',
        nameError = '',
        mobileError = '',
        emailError = '',
        passwordError = ''
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        details = request.form
        session['username'] = details['username']

        if len(details['username']) == 0: 
            nameError = 'Please enter a valid User Name'
            
            return render_template('login.html',
                nameError = nameError,
                error = ''
            )

        cur = mysql.connection.cursor()
        usernameTrue = cur.execute("SELECT username FROM login_credentials WHERE username = %s;", [details['username']])
        passwordTrue = cur.execute("SELECT password FROM login_credentials WHERE password = %s;", [details['password']])
        mysql.connection.commit()
        cur.close()
        
        if usernameTrue != 1 and passwordTrue != 1:
            return redirect(url_for('register'))

        error = 'This user is already registered, if you have forgot your password, kindly reset the password by clicking on the Forgot Password button!!'
        if usernameTrue == 1 and passwordTrue != 1:
            return render_template('login.html',
                nameError = '',
                error = error
            )
        
        global account_true
        account_true = True
        
        return redirect(url_for('main'))

    return render_template('login.html',
        nameError = '',
        error = ''
    )

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == "POST":
        details = request.form
        
        cur = mysql.connection.cursor()

        useremail = details['email']
        password = details['password']
        
        errorStatus = verification.verifyChange(useremail, password)
        useremailTrue = cur.execute("SELECT email FROM login_credentials WHERE email = %s;", [useremail])

        if useremailTrue != 1:
            errorStatus[0] = False

        clear = errorStatus.count(True)

        if clear != 2:
            message = ['Please enter a valid and registered email address!!', 'Please enter a password with min 4 characters or max 15 characters!!']

            for i in range(0,2):
                if errorStatus[i] == True:
                    message[i] = ''

            return render_template('forgot_password.html',
                emailError = message[0],
                passwordError = message[1]
            )

        cur.execute("UPDATE login_credentials SET password=%s WHERE email=%s;", (password, useremail))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('login'))

    return render_template('forgot_password.html',
        emailError = '',
        passwordError = ''
    )

app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

aes = aesEncryption.AESCipher('vnkdjnfjknfl1232#')

@app.route('/')
def main():
    if account_true == True:
        username = session['username']
        return render_template('session.html', username=username)

    return redirect(url_for('login'))

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    
    if len(json.keys()) == 2:
        print('message: ' + json['message'])
        enc = aes.encrypt(json['message'])
        json['enc'] = str(enc)
        dec = aes.decrypt(enc)
        json['message'] = dec
        print('encrypted: ' + str(enc))
        print('decrypted: ' + dec)

    socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    socketio.run(app, debug=True)