from flask import Flask, request, redirect, url_for, session
import os, json, time, secrets, shutil
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Folders
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FILES_DIR = BASE_DIR / "user_files"
DATA_DIR.mkdir(exist_ok=True)
FILES_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

OWNER_USER = "ANIK SAIFI"
OWNER_PASS = "anik7860@@"

def load_users():
    if not USERS_FILE.exists(): return {}
    try: return json.loads(USERS_FILE.read_text())
    except: return {}

def save_users(data):
    USERS_FILE.write_text(json.dumps(data, indent=2))

# ========== ROUTES ==========
@app.route("/")
def home():
    if session.get("role") == "owner":
        return redirect(url_for("owner_dashboard"))
    if session.get("username"):
        return redirect(url_for("user_dashboard"))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ANIK VPS</title>
        <style>
            body { background: #000814; color: #e8f4ff; font-family: Arial; text-align: center; padding: 50px; }
            h1 { font-size: 48px; background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .btn { background: linear-gradient(135deg,#0088ff,#00ddff); color: #fff; padding: 12px 30px; border-radius: 10px; text-decoration: none; display: inline-block; margin: 10px; }
            .social { margin-top: 40px; }
            .social a { color: #6ab0e6; font-size: 30px; margin: 0 15px; text-decoration: none; }
            .made-by { color: #6ab0e6; margin-top: 20px; font-size: 14px; letter-spacing: 2px; }
            .made-by span { background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="made-by">⚡ MADE BY <span>ANIK</span> ⚡</div>
        <h1>🚀 ANIK VPS</h1>
        <p>Run your code on ANIK VPS in seconds</p>
        <div>
            <a href="/login" class="btn">Login →</a>
        </div>
        <div class="social">
            <a href="https://t.me/iowntmc" target="_blank">📱</a>
            <a href="https://instagram.com/anik.saif1" target="_blank">📸</a>
            <a href="#" target="_blank">👻</a>
        </div>
        <p style="color:#6ab0e6;margin-top:40px;">© 2026 ANIK VPS — Built with ❤️ by ANIK</p>
    </body>
    </html>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        if u == OWNER_USER and p == OWNER_PASS:
            session["role"] = "owner"
            session["username"] = u
            return redirect(url_for("owner_dashboard"))
        users = load_users()
        if u in users and users[u].get("password") == p:
            session["role"] = "user"
            session["username"] = u
            return redirect(url_for("user_dashboard"))
        error = "Invalid username or password"
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login | ANIK VPS</title>
        <style>
            body { background: #000814; color: #e8f4ff; font-family: Arial; text-align: center; padding: 50px; }
            .card { background: rgba(0,20,50,0.85); max-width: 400px; margin: auto; padding: 40px; border-radius: 16px; border: 1px solid rgba(0,150,255,0.25); }
            h2 { background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            input { width: 100%%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid rgba(0,150,255,0.25); background: rgba(0,10,30,0.8); color: #fff; }
            .btn { background: linear-gradient(135deg,#0088ff,#00ddff); color: #fff; padding: 12px 30px; border-radius: 10px; border: none; cursor: pointer; width: 100%%; font-size: 16px; }
            .error { color: #ff4466; }
            .made-by { color: #6ab0e6; margin-top: 20px; font-size: 12px; letter-spacing: 2px; }
            .made-by span { background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔐 Welcome to ANIK VPS</h2>
            ''' + (f'<p class="error">⚠ {error}</p>' if error else '') + '''
            <form method="post">
                <input name="username" placeholder="Username" required>
                <input name="password" type="password" placeholder="Password" required>
                <button class="btn" type="submit">Login →</button>
            </form>
            <p style="color:#6ab0e6;font-size:12px;">Owner & User accounts supported</p>
        </div>
        <div class="made-by">Made with ❤️ by <span>ANIK</span></div>
    </body>
    </html>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/owner")
def owner_dashboard():
    if session.get("role") != "owner":
        return redirect(url_for("login"))
    users = load_users()
    html = '<h1>👑 Owner Dashboard</h1><p>Welcome ANIK!</p><a href="/logout">Logout</a><hr>'
    html += '<h2>Users</h2><ul>'
    for u in users:
        html += f'<li>{u}</li>'
    html += '</ul>'
    return html

@app.route("/owner/create", methods=["POST"])
def owner_create():
    if session.get("role") != "owner":
        return redirect(url_for("login"))
    u = request.form.get("username", "").strip()
    p = request.form.get("password", "").strip()
    if u and p and u != OWNER_USER:
        users = load_users()
        users[u] = {"password": p, "created_at": time.time()}
        save_users(users)
        (FILES_DIR / u).mkdir(exist_ok=True)
    return redirect(url_for("owner_dashboard"))

@app.route("/owner/delete/<username>", methods=["POST"])
def owner_delete(username):
    if session.get("role") != "owner":
        return redirect(url_for("login"))
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        shutil.rmtree(FILES_DIR / username, ignore_errors=True)
    return redirect(url_for("owner_dashboard"))

@app.route("/dashboard")
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("login"))
    u = session["username"]
    return f'<h1>👤 User Dashboard</h1><p>Welcome {u}!</p><a href="/logout">Logout</a>'

@app.route("/upload", methods=["POST"])
def upload():
    if session.get("role") != "user":
        return redirect(url_for("login"))
    u = session["username"]
    udir = FILES_DIR / u
    for f in request.files.getlist("files"):
        if f.filename:
            name = secure_filename(f.filename)
            f.save(udir / name)
    return redirect(url_for("user_dashboard"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
