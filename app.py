from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, json, time, secrets, subprocess, shutil
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
    return render_template("landing.html")

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
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# --- Owner ---
@app.route("/owner")
def owner_dashboard():
    if session.get("role") != "owner":
        return redirect(url_for("login"))
    users = load_users()
    return render_template("owner.html", users=users, base_url=request.host_url)

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

# --- User ---
@app.route("/dashboard")
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("login"))
    u = session["username"]
    files = [f.name for f in (FILES_DIR / u).iterdir() if f.is_file()]
    return render_template("user.html", username=u, files=files)

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

# ========== MAIN ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
