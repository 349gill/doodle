from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

import os
import logging

from scheduler import MultilevelQueue

scheduler = MultilevelQueue()

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:LeReZjBFlNIWHjKXeankgAcOcKzTFyGR@junction.proxy.rlwy.net:43241/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    details = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.name,
            'start': self.start_time.isoformat() if self.start_time else None,
            'end': self.end_time.isoformat() if self.end_time else None,
            'extendedProps': {
                'details': self.details,
                'priority': self.priority,
                'duration': self.duration
            }
        }
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('calendar'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('calendar'))

    flash('Invalid username or password')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get_or_404(session['user_id'])
    return render_template('calendar.html', username=user.username)


# API Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.json
        name = data['name']
        priority = int(data['priority'])
        due_date = datetime.fromisoformat(data['deadline'])
        duration = float(data['duration'])

        scheduler.add_task(name=name, priority=priority, due_date=due_date, duration=duration)

        scheduled_tasks = scheduler.execute_tasks()

        Task.query.filter_by(user_id=session['user_id']).delete()

        for task in scheduled_tasks[0]:
            db_task = Task(
                id=task.id,
                name=task.name,
                priority=task.priority,
                duration=task.duration,
                start_time=task.arrival_time,
                end_time=task.due_date,
                deadline=task.due_date,
                user_id=session['user_id']
            )
            db.session.add(db_task)

        db.session.commit()

        return jsonify([t.to_dict() for t in Task.query.filter_by(user_id=session['user_id']).all()])

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


logging.basicConfig(level=logging.DEBUG)

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        data = request.json
        task.name = data.get('name', task.name)
        task.priority = int(data.get('priority', task.priority))
        task.details = data.get('details', task.details)

        if 'duration' in data:
            task.duration = float(data.get('duration', task.duration))
            task.start_time = task.deadline - timedelta(hours=task.duration)

        if 'deadline' in data:
            task.start_time = task.start_time + (data.get('deadline', task.deadline) - task.end_date)
            task.end_time = data.get('deadline', task.deadline)

        db.session.commit()
        return jsonify(task.to_dict())

    except Exception as e:
        db.session.rollback()
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task: return jsonify({'error': 'Task not found'}), 404

    try:
        task_removed = scheduler.remove_task(task_id)

        db.session.delete(task)
        db.session.commit()

        if task_removed: return jsonify({'message': 'Task deleted successfully from both the queue and database'})
        else: return jsonify({'message': 'Task deleted from database, but it was not found in the queue'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)
