import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:XHHsPjdJNQFegeeImwAGJuMPbEIgkLBD@junction.proxy.rlwy.net:35186/railway'
db = SQLAlchemy(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/calender')
def calender():
  return render_template('calender.html')

if __name__ == '__main__':
  app.run(port=5000)