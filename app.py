# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import MySQL
import hashlib

app = Flask(__name__)

# app.config['MYSQL_HOST'] = 'your-railway-mysql-host'
# app.config['MYSQL_USER'] = 'your-railway-mysql-user'
# app.config['MYSQL_PASSWORD'] = 'your-railway-mysql-password'
# app.config['MYSQL_DB'] = 'scheduler_db'
# app.secret_key = 'your-secret-key'
#
# mysql = MySQL(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user:
            if password == user[2]:
                session['logged_in'] = True
                session['username'] = username
                return "Login successful!" 
            else:
                flash('Invalid password')
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                       (username, password))
            mysql.connection.commit()
            session['logged_in'] = True
            session['username'] = username
            return "Account created and logged in!"
            
        cur.close()
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)