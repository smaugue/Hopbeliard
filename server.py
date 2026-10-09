from flask import Flask, send_from_directory, render_template, redirect,session, request, Response, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import threading
import time
import random
import re
import hashlib, hmac, secrets
import argparse
import string

from db_manager import Database
from schema import metadata
from config import config
from utils import init, konsol, is_granted, Droit, navbar_generator

konsol("INFO", "Starting")

def args_parser():
    parser = argparse.ArgumentParser(description='Hopbéliard Webapp Server')
    parser.add_argument('--reset_db', action="store_true", help='Reset Database')
    parser.add_argument('--disabeled_admin', action="store_true", help='Disable default admin user')
    parser.add_argument('--reset_admin', action="store_true", help='Disable default admin user')
    parser.add_argument('--reset_admin_password', type=str, help="Définire mot de passe admin")
    global args
    args = parser.parse_args()

app = Flask(__name__)
app.debug = True
app.template_folder = "webapp/templates"
app.static_folder = "webapp/static"
app.secret_key = config.APP_SECRET

#set cors = ["*"] in socketio to allow all origins (for blumap proxy)
socketio = SocketIO(app, manage_session=False,) # cors_allowed_origins="*")

args_parser()
db: Database = init(config, args)

konsol('INFO', "Started")

CHALLENGES = {}                         # login -> (challenge, expiration)                     # secondes
 # pour les logins inexistants

#
# DEFAULT ROUTE
#

@app.route("/")
def index():
    if session.get('login'):
        if session['need_change']:
            return render_template('account.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
        return render_template('index.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
    return render_template("login.html")

#
# PAGES ROUTES
#

@app.route("/account")
def account():
    if session.get('login'):
        return render_template('account.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
    return render_template("login.html")

@app.route("/logs_pannel", methods=["GET"])
def logs_pannel():
    if session.get('login') and is_granted(Droit.ADMIN, session['access_level']):
            return render_template('logs_pannel.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
    return redirect("/")

@app.route("/users_administration")
def users_administration_pannel():
    if session.get('login') and is_granted(Droit.USERS_GESTION, session['access_level']):
                konsol('INFO', f"{session['login']} access users administration pannel")
                return render_template('users_administration_pannel.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
    return redirect("/")

@app.route("/patients")
def patients_pannel():
    if session.get('login') and is_granted(Droit.PATIENT_LECTURE, session['access_level']):
                konsol('INFO', f"{session['login']} access patients pannel")
                return render_template('patients.html', VERSION=config.VERSION.VERSION, NAVE_BARE=navbar_generator(session['access_level']))
    return redirect("/")

#
# ASSETS ROUTES
#

@app.route('/script/<path:path>')
def send_static(path):
    return send_from_directory('webapp/script', path)

#
# API ROUTES
#

# SUB/LOGIN

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = str(data.get("login", "")).strip()
    if not user:
        konsol('WARN', f"{request.remote_addr} requette login sans données")
        return jsonify(ok=False, error="Login manquant"), 400
    access = db.fetch_one("SELECT access_level, active FROM users WHERE login = :login", login=user)
    row = db.fetch_one("SELECT psswd, salt, need_change FROM login WHERE login = :login", login=user)
    reponse = data.get("reponse")
    if reponse is None:
        if access.active:
            konsol('INFO', f"{request.remote_addr} login try with {user}")
            challenge = secrets.token_hex(32)
            sel = row[1] if row else hmac.new(secrets.token_bytes(32), user.encode(), hashlib.sha256).hexdigest()[:32]
            CHALLENGES[user] = (challenge, time.time() + config.CHALLENGE_TTL)
            return jsonify(sel=sel, challenge=challenge)
        konsol('WARN', f"{request.remote_addr} login try with inactive user {user}")
        challenge = secrets.token_hex(32)
        sel = hmac.new(secrets.token_bytes(32), user.encode(), hashlib.sha256).hexdigest()[:32]
        CHALLENGES[user] = (challenge, time.time() + config.CHALLENGE_TTL)
        return jsonify(sel=sel, challenge=challenge)
    challenge, expiration = CHALLENGES.pop(user, (None, 0))
    if row is None or challenge is None or time.time() > expiration:
        konsol('WARN', f"{request.remote_addr} Identifiants invalides")
        return jsonify(ok=False, error="Identifiants invalides"), 401
    attendu = hmac.new(bytes.fromhex(row[0]), challenge.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(attendu, str(reponse)):
        konsol('WARN', f"{request.remote_addr} Identifiants invalides")
        return jsonify(ok=False, error="Identifiants invalides"), 401
    session["login"] = user
    session["access_level"] = int(access.access_level)
    session["need_change"] = row[2]
    konsol('INFO', f"{request.remote_addr} user {user} login successfuly")
    return jsonify(ok=True)

@app.route("/api/change_password", methods=["POST"])
def change_password():
    user = session.get("login")
    if not user:
        konsol('WARN', f"{request.remote_addr} not login")
        return jsonify(ok=False, error="Non connecté"), 401
    data = request.get_json(silent=True) or {}
    reponse = data.get("reponse")
    cle = "chg:" + user
    row = db.fetch_one("SELECT psswd, salt FROM login WHERE login = :login", login=user)
    if row is None:
        konsol('WARN', f"{request.remote_addr} user not in DB")
        return jsonify(ok=False, error="Utilisateur introuvable"), 404
    if reponse is None:
        challenge = secrets.token_hex(32)
        nouveau_sel = secrets.token_hex(16)
        CHALLENGES[cle] = (challenge, nouveau_sel, time.time() + config.CHALLENGE_TTL)
        return jsonify(sel=row.salt, challenge=challenge, nouveau_sel=nouveau_sel)
    challenge, nouveau_sel, expiration = CHALLENGES.pop(cle, (None, None, 0))
    if challenge is None or time.time() > expiration:
        return jsonify(ok=False, error="Challenge expiré"), 401
    attendu = hmac.new(bytes.fromhex(row.psswd), challenge.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(attendu, str(reponse)):
        return jsonify(ok=False, error="Ancien mot de passe incorrect"), 401
    nouveau_hash = str(data.get("nouveau", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", nouveau_hash):
        return jsonify(ok=False, error="Nouveau mot de passe invalide"), 400
    db.execute("UPDATE login SET psswd = :p, salt = :s, need_change = :nc WHERE login = :l",
               p=nouveau_hash, s=nouveau_sel, l=user, nc=False)
    konsol('INFO', f"{request.remote_addr} {session.get('login')} change password")
    return jsonify(ok=True)

@app.route("/api/logout", methods=["GET"])
def logout():
    konsol('INFO', f"{request.remote_addr} user {session.get('login', 'None')} logout")
    session.clear()
    return redirect('/')


# SUB/USERS MANAGEMENT

@app.route("/api/get_users", methods=['POST'])
def get_users():
    if session.get('login') and is_granted(Droit.USERS_GESTION, session['access_level']):
        data = request.get_json(silent=True) or {}
        page = int(data.get("page", 1))
        offset = (page -1) * 3
        rows = db.fetch_all("SELECT * FROM users ORDER BY id LIMIT :l OFFSET :o", l=3, o=offset)
        users = [dict(r._mapping) for r in rows]
        print(users)
        return jsonify(ok=True, users=users)
    return redirect('/')

@app.route("/api/add_user", methods=["POST"])
def add_user():
    if not (session.get("login") and is_granted(Droit.USERS_GESTION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    login = str(data.get("login", "")).strip()
    if not login:
        return jsonify(ok=False, error="Login obligatoire"), 400
    try:
        access_level = int(data.get("access_level", 0))
    except (TypeError, ValueError):
        return jsonify(ok=False, error="access_level invalide"), 400
    if access_level & Droit.ADMIN and not is_granted(Droit.ADMIN, session["access_level"]):
        return jsonify(ok=False, error="Seul un admin peut donner le droit ADMIN"), 403
    if db.fetch_one("SELECT id FROM users WHERE login = :login", login=login):
        return jsonify(ok=False, error="Utilisateur déjà existant"), 409
    db.execute(
        "INSERT INTO users (name, lastname, login, access_level, active) VALUES (:name, :lastname, :login, :access_level, :active)",
        name=str(data.get("name", "")).strip(),
        lastname=str(data.get("lastname", "")).strip(),
        login=login,
        access_level=access_level,
        active=True,
    )
    sel = secrets.token_hex(16)
    rdmpsswd = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
    psswd = hashlib.sha256(( rdmpsswd + sel).encode()).hexdigest()
    db.execute("INSERT INTO login (login, psswd, salt, need_change) VALUES (:user, :passwd, :salt, :need_change)",
                   user=login,
                   passwd=psswd,
                   salt=sel,
                   need_change=True
                )
    return jsonify(ok=True, psswd=rdmpsswd)

@app.route('/api/reset_user_password', methods=["POST"])
def reset_user_password():
    if not (session.get("login") and is_granted(Droit.USERS_GESTION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    login = str(data.get("login", "")).strip()
    if not login:
        return jsonify(ok=False, error="Login obligatoire"), 400
    access_level = db.fetch_one("SELECT access_level FROM users WHERE login = :l", l=login)[0]
    if access_level & Droit.ADMIN and not is_granted(Droit.ADMIN, session["access_level"]):
            return jsonify(ok=False, error="Seul un admin peut reset un mdp admin"), 403
    sel = secrets.token_hex(16)
    rdmpsswd = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
    psswd = hashlib.sha256(( rdmpsswd + sel).encode()).hexdigest()
    db.execute("UPDATE login SET psswd = :p, salt = :s, need_change = :nc WHERE login = :l",
                l=login,
                p=psswd,
                s=sel,
                nc=True
                )
    return jsonify(ok=True, psswd=rdmpsswd)

@app.route('/api/user_access_status', methods=["POST"])
def user_access_status():
    if not (session.get("login") and is_granted(Droit.USERS_GESTION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    login = str(data.get("login", "")).strip()
    access_level = db.fetch_one("SELECT access_level FROM users WHERE login = :l", l=login)[0]
    if access_level & Droit.ADMIN and not is_granted(Droit.ADMIN, session["access_level"]):
        return jsonify(ok=False, error="Seul un admin peut désactiver un compte admin"), 403
    value = data.get('access_status')
    value = True if value == 'true' else False
    if not login:
        return jsonify(ok=False, error="Login obligatoire"), 400
    db.execute("UPDATE users SET active = :a WHERE login = :l",
               a=value,
               l=login
               )
    return jsonify(ok=True, access=value)

@app.route('/api/delete_user', methods=['POST'])
def delete_user():
    if not (session.get("login") and is_granted(Droit.USERS_GESTION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    login = str(data.get("login", "")).strip()
    access_level = db.fetch_one("SELECT access_level FROM users WHERE login = :l", l=login)[0]
    if access_level & Droit.ADMIN and not is_granted(Droit.ADMIN, session["access_level"]):
        return jsonify(ok=False, error="Seul un admin peut supprimer un compte admin"), 403
    if session.get("login") == login:
        return jsonify(ok=False, error="Vous ne pouvez pas vous supprimer vous même"), 403
    if not login:
            return jsonify(ok=False, error="Login obligatoire"), 400
    db.execute("DELETE FROM login WHERE login = :l", l=login)
    db.execute("DELETE FROM users WHERE login = :l", l=login)
    return jsonify(ok=True)
    
# SUB/PATIENT MANAGEMENT
@app.route('/api/add_patient', methods=['POST'])
def add_patien():
    if not (session.get("login") and is_granted(Droit.PATIENT_EDITION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    lname = str(data.get("lastname", "")).strip()
    comm = str(data.get("comm", "")).strip()
    if db.fetch_one("SELECT id FROM patient WHERE name = :n AND lastname = :ln", n=name, ln=lname):
        return jsonify(ok=False, error="Patient déjà créé"), 409
    try :
        db.execute("INSERT INTO patient (name, lastname, comm) VALUES (:n, :ln, :comm)", n=name, ln=lname, comm=comm)
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=e), 500

@app.route('/api/get_patients', methods=['POST'])
def get_patient():
    if not (session.get("login") and is_granted(Droit.PATIENT_LECTURE, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    offset = (page -1) * 3
    rows = db.fetch_all("SELECT * FROM patient ORDER BY id LIMIT :l OFFSET :o", l=3, o=offset)
    users = [dict(r._mapping) for r in rows]
    return jsonify(ok=True, users=users)

@app.route('/api/get_prise_en_charge', methods=['POST'])
def get_prise_en_charge():
    if not (session.get("login") and is_granted(Droit.PATIENT_LECTURE, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    idp = str(data.get("id", "")).strip()
    page = int(data.get("page", 1))
    offset = (page -1) * 3
    if not idp:
        return jsonify(ok=False, error="ID patient obligatoire"), 400
    rows = db.fetch_all("SELECT * FROM prise_en_charge WHERE id_patient = :idp ORDER BY id LIMIT :l OFFSET :o", idp=int(idp), l=3, o=offset)
    pec = [dict(r._mapping) for r in rows]
    return jsonify(ok=True, pec=pec)

@app.route('/api/add_admition', methods=['POST'])
def add_admition():
    if not (session.get("login") and is_granted(Droit.PATIENT_EDITION, session["access_level"])):
        return redirect('/')
    data = request.get_json(silent=True) or {}
    idp = str(data.get("id", "")).strip()
    obj = str(data.get("objet", "")).strip()
    comm = str(data.get("comm", "")).strip()
    if db.fetch_one("SELECT id FROM patient WHERE id = :id", id=idp)[0]:
        db.execute("INSERT INTO prise_en_charge (id_patient, objet, comm) VALUES (:idp, :obj, :comm)", idp=int(idp), obj=obj, comm=comm)
        return jsonify(ok=True)
    return jsonify(ok=False, error="Patient inconnu"), 400

    

def api_template():
    if session.get('login'):
        print("do somthink")
    return redirect('/')

#
# Socetio event for log
#

if __name__ == '__main__':
    socketio.run(app, host=config.HOST, port=config.PORT, use_reloader=False)