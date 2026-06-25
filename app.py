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

# ========== HTML PAGES (Direct in Python) ==========
LANDING_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ANIK VPS</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000814;
            color: #e8f4ff;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: radial-gradient(1200px 700px at 10% -10%, rgba(0,136,255,0.2), transparent 60%),
                        radial-gradient(1000px 600px at 100% 0%, rgba(0,187,255,0.15), transparent 60%),
                        linear-gradient(180deg,#000814,#001233);
        }
        .made-by {
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            letter-spacing: 3px;
            color: #6ab0e6;
            border-bottom: 1px solid rgba(0,150,255,0.2);
            width: 100%;
            max-width: 600px;
            margin-bottom: 30px;
        }
        .made-by span {
            background: linear-gradient(135deg,#0088ff,#00ddff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        h1 {
            font-size: 48px;
            background: linear-gradient(135deg,#0088ff,#00ddff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
        }
        .subtitle {
            color: #6ab0e6;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg,#0088ff,#00ddff);
            color: #fff;
            padding: 14px 40px;
            border-radius: 12px;
            text-decoration: none;
            display: inline-block;
            margin: 5px 10px;
            font-weight: 600;
            font-size: 16px;
            transition: 0.3s;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,136,255,0.4);
        }
        .btn-ghost {
            background: rgba(0,136,255,0.1);
            border: 1px solid rgba(0,150,255,0.3);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            max-width: 800px;
            margin: 40px 0;
            width: 100%;
        }
        .feature-card {
            background: rgba(0,20,50,0.7);
            border: 1px solid rgba(0,150,255,0.15);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .feature-card h3 { color: #66ccff; margin-bottom: 8px; }
        .feature-card p { color: #6ab0e6; font-size: 14px; }
        .social {
            margin-top: 30px;
            display: flex;
            gap: 25px;
        }
        .social a {
            color: #6ab0e6;
            font-size: 28px;
            transition: 0.3s;
            text-decoration: none;
        }
        .social a:hover {
            color: #66ccff;
            transform: translateY(-3px);
        }
        .footer {
            color: #6ab0e6;
            margin-top: 40px;
            font-size: 13px;
            border-top: 1px solid rgba(0,150,255,0.1);
            padding-top: 20px;
            width: 100%;
            text-align: center;
        }
        @media (max-width: 600px) {
            h1 { font-size: 32px; }
            .features { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="made-by">⚡ MADE BY <span>ANIK</span> ⚡</div>
    <h1>🚀 ANIK VPS</h1>
    <p class="subtitle">Run your code on ANIK VPS in seconds</p>
    <div>
        <a href="/login" class="btn">🔐 Login</a>
        <a href="/login" class="btn btn-ghost">📋 Get Started</a>
    </div>
    <div class="features">
        <div class="feature-card"><h3>⚡ Instant Deploy</h3><p>Upload and run any script</p></div>
        <div class="feature-card"><h3>📦 Module Install</h3><p>pip / npm install</p></div>
        <div class="feature-card"><h3>📜 Live Logs</h3><p>Real-time streaming</p></div>
        <div class="feature-card"><h3>🔐 Owner Control</h3><p>User management</p></div>
    </div>
    <div class="social">
        <a href="https://t.me/iowntmc" target="_blank" title="Telegram"><i class="fa-brands fa-telegram"></i></a>
        <a href="https://instagram.com/anik.saif1" target="_blank" title="Instagram"><i class="fa-brands fa-instagram"></i></a>
        <a href="#" target="_blank" title="Snapchat"><i class="fa-brands fa-snapchat"></i></a>
    </div>
    <div class="footer">© 2026 ANIK VPS — Built with ❤️ by ANIK</div>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login | ANIK VPS</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000814;
            color: #e8f4ff;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: radial-gradient(1200px 700px at 10% -10%, rgba(0,136,255,0.2), transparent 60%),
                        linear-gradient(180deg,#000814,#001233);
        }
        .card {
            background: rgba(0,20,50,0.85);
            max-width: 400px;
            width: 100%;
            padding: 40px;
            border-radius: 20px;
            border: 1px solid rgba(0,150,255,0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .logo {
            text-align: center;
            margin-bottom: 25px;
        }
        .logo h2 {
            background: linear-gradient(135deg,#0088ff,#00ddff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 28px;
        }
        .logo p { color: #6ab0e6; font-size: 14px; }
        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border-radius: 12px;
            border: 1px solid rgba(0,150,255,0.2);
            background: rgba(0,10,30,0.8);
            color: #fff;
            font-size: 15px;
            transition: 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #0088ff;
            box-shadow: 0 0 20px rgba(0,136,255,0.1);
        }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg,#0088ff,#00ddff);
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,136,255,0.3); }
        .error {
            color: #ff4466;
            background: rgba(255,68,102,0.1);
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 15px;
            text-align: center;
            border: 1px solid rgba(255,68,102,0.2);
        }
        .footer-text {
            text-align: center;
            color: #6ab0e6;
            font-size: 12px;
            margin-top: 20px;
        }
        .footer-text span {
            background: linear-gradient(135deg,#0088ff,#00ddff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .social-login {
            text-align: center;
            margin-top: 20px;
        }
        .social-login a {
            color: #6ab0e6;
            font-size: 24px;
            margin: 0 12px;
            transition: 0.3s;
            text-decoration: none;
        }
        .social-login a:hover { color: #66ccff; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <h2>🔐 ANIK VPS</h2>
            <p>Sign in to your account</p>
        </div>
        {error_html}
        <form method="post">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password" placeholder="Password" required>
            <button class="btn" type="submit">Login →</button>
        </form>
        <div class="footer-text">Made with ❤️ by <span>ANIK</span></div>
        <div class="social-login">
            <a href="https://t.me/iowntmc" target="_blank"><i class="fa-brands fa-telegram"></i></a>
            <a href="https://instagram.com/anik.saif1" target="_blank"><i class="fa-brands fa-instagram"></i></a>
            <a href="#" target="_blank"><i class="fa-brands fa-snapchat"></i></a>
        </div>
    </div>
</body>
</html>
'''

# ========== ROUTES ==========
@app.route("/")
def home():
    if session.get("role") == "owner":
        return redirect(url_for("owner_dashboard"))
    if session.get("username"):
        return redirect(url_for("user_dashboard"))
    return LANDING_HTML

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
    
    error_html = f'<div class="error">⚠ {error}</div>' if error else ''
    return LOGIN_HTML.format(error_html=error_html)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/owner")
def owner_dashboard():
    if session.get("role") != "owner":
        return redirect(url_for("login"))
    users = load_users()
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Owner Dashboard</title>
    <style>
        body { background: #000814; color: #e8f4ff; font-family: Arial; padding: 40px; }
        h1 { background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .card { background: rgba(0,20,50,0.85); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,150,255,0.2); margin: 20px 0; }
        .btn { background: linear-gradient(135deg,#0088ff,#00ddff); color: #fff; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; }
        .btn-danger { background: #ff4466; }
        input { padding: 10px; border-radius: 8px; border: 1px solid rgba(0,150,255,0.2); background: rgba(0,10,30,0.8); color: #fff; margin: 5px; }
        ul { list-style: none; padding: 0; }
        li { padding: 10px; border-bottom: 1px solid rgba(0,150,255,0.1); display: flex; justify-content: space-between; align-items: center; }
    </style>
    </head>
    <body>
        <h1>👑 Owner Dashboard</h1>
        <p>Welcome ANIK!</p>
        <a href="/logout" class="btn" style="text-decoration:none;">Logout</a>
        
        <div class="card">
            <h2>➕ Create User</h2>
            <form method="post" action="/owner/create">
                <input name="username" placeholder="Username" required>
                <input name="password" placeholder="Password" required>
                <button class="btn" type="submit">Create</button>
            </form>
        </div>
        
        <div class="card">
            <h2>👥 Users</h2>
            <ul>
    '''
    for u in users:
        html += f'''
        <li>
            <span>{u}</span>
            <form method="post" action="/owner/delete/{u}" style="display:inline;">
                <button class="btn btn-danger" type="submit">Delete</button>
            </form>
        </li>
        '''
    html += '''
            </ul>
        </div>
    </body>
    </html>
    '''
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
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>User Dashboard</title>
    <style>
        body {{ background: #000814; color: #e8f4ff; font-family: Arial; padding: 40px; }}
        h1 {{ background: linear-gradient(135deg,#0088ff,#00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .card {{ background: rgba(0,20,50,0.85); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,150,255,0.2); margin: 20px 0; }}
        .btn {{ background: linear-gradient(135deg,#0088ff,#00ddff); color: #fff; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; text-decoration: none; display: inline-block; }}
        input {{ padding: 10px; border-radius: 8px; border: 1px solid rgba(0,150,255,0.2); background: rgba(0,10,30,0.8); color: #fff; margin: 5px; }}
    </style>
    </head>
    <body>
        <h1>👤 User Dashboard</h1>
        <p>Welcome {u}!</p>
        <a href="/logout" class="btn">Logout</a>
        
        <div class="card">
            <h2>📤 Upload Files</h2>
            <form method="post" action="/upload" enctype="multipart/form-data">
                <input type="file" name="files" multiple required>
                <button class="btn" type="submit">Upload</button>
            </form>
        </div>
    </body>
    </html>
    '''

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
