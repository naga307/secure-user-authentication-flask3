from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-a-secure-random-value'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                flash('Access denied', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def setup_db():
    # Initialize DB using a direct sqlite connection (works without app context)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    conn.commit()
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role='admin'")
    row = cur.fetchone()
    if row and row[0] == 0:
        try:
            cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        ('admin', generate_password_hash('admin123'), 'admin'))
            conn.commit()
            print('Created default admin user: admin / admin123')
        except sqlite3.IntegrityError:
            pass
    conn.close()


# Ensure DB and default admin exist on startup
setup_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form.get('role', 'user')
        if not username or not password:
            flash('Username and password required', 'warning')
            return redirect(url_for('register'))
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                        (username, generate_password_hash(password), role))
            db.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'))


@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, username, role FROM users')
    users = cur.fetchall()
    return render_template('admin.html', users=users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
