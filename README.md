# Secure User Authentication (Flask)

This is a minimal Flask application providing secure user registration, login, session management, and a protected admin area.

Quickstart

1. Create a Python virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the server:

```powershell
python app.py
```

4. Open http://127.0.0.1:5000 in your browser.

Default admin user (created automatically if none exists):
- username: `admin`
- password: `admin123`

Change `app.config['SECRET_KEY']` in `app.py` before deploying to production.
