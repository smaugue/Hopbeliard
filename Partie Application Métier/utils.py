from db_manager import Database
from config import Config
from db_manager import Database
from datetime import datetime
from enum import IntFlag
import inspect
import hashlib, hmac, secrets
import string

from schema import metadata

def init(config: Config, args) -> Database:
    db = Database(config.DB_FORMAT, config.DB_HOST, config.DB_PORT, config.DB_USER, config.DB_PASSWORD, config.DB_NAME)
    if args.reset_db:
        metadata.drop_all(db.engine)
        #for tn in metadata.tables :
        #   db.execute(f"DROP TABLE {tn}") #+ " ".join(f" {tn}," for tn in metadata.tables).removesuffix(','))
        metadata.create_all(db.engine)
        db.execute("INSERT INTO users (name, lastname, login, access_level, active) VALUES (:name, :lastname, :login, :access_level, :active)", name="admin", lastname="admin", login="admin", access_level=256, active=True)
        #print(db.fetch_one("SELECT * FROM users WHERE login = :login", login='admin'))
        sel = secrets.token_hex(16)
        #rdmpsswd = ''.join(choices(string.ascii_uppercase + string.digits + string.ascii_lowercase + string.punctuation, k=26))
        psswd = hashlib.sha256((''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(26)) + sel).encode()).hexdigest()
        db.execute("INSERT INTO login (login, psswd, salt, need_change) VALUES (:user, :passwd, :salt, :need_change)", user="admin", passwd=psswd, salt=sel, need_change=True)
        konsol("INFO", "Database initialized")
    else:
        metadata.create_all(db.engine)
        db.execute("INSERT OR IGNORE INTO users (name, lastname, login, access_level) VALUES (:name, :lastname, :login, :access_level)", name="admin", lastname="admin", login="admin", access_level=256)
    if args.disabeled_admin:
        konsol('INFO', "Admin user disabled")
        db.execute("UPDATE users SET active = :s WHERE login = :l", s=False, l="admin")
    if args.reset_admin:
        konsol('INFO', "Admin user reset")
        db.execute('DELETE FROM login WHERE login = :l', l='admin')
        db.execute("DELETE FROM users WHERE login = :l", l='admin')
        db.execute("INSERT INTO users (name, lastname, login, access_level, active) VALUES (:name, :lastname, :login, :access_level, :active)", name="admin", lastname="admin", login="admin", access_level=256, active=True)
    if args.reset_admin_password:
        konsol("INFO", 'Admin password reset')
        db.execute("DELETE FROM login WHERE login = :l ", l='admin')
        db.execute("INSERT OR IGNORE INTO users (name, lastname, login, access_level) VALUES (:name, :lastname, :login, :access_level)", name="admin", lastname="admin", login="admin", access_level=256)
        sel = secrets.token_hex(16)
        psswd = hashlib.sha256((args.reset_admin_password+ sel).encode()).hexdigest()
        db.execute("INSERT INTO login (login, psswd, salt, need_change) VALUES (:l, :p, :s, :nc)", l="admin", p=psswd, s=sel, nc=False)
    return db


class Droit(IntFlag):
    PATIENT_LECTURE   = 1
    PATIENT_EDITION   = 2
    VEHICULE_RESA     = 4
    VEHICULE_GESTION  = 8
    VIDEO             = 16
    USERS_GESTION     = 32
    RESERVED_1        = 64
    RESERVED_2        = 128
    ADMIN             = 256


def is_granted(droit_voulu: int, droit_user: int = 0) -> bool:
    if droit_user & Droit.ADMIN: # xxxxxxxx? =?= 000000001 => T/F
        return True
    return (droit_user & droit_voulu) == droit_voulu

def logs(data):
        try:
            now = datetime.now()
            startDate = now.strftime('%Y-%m-%d')
            with open(f"logs/{startDate}.log", "a+", encoding="utf-8") as logs_file:
                logs_file.write(data + "\n")
        except Exception as e:
            konsol("ERROR", f"Log impossible: {e}", False)

def konsol(type, arg, log: bool = True):
    """
    Utilisation:
    ------------
    `type`: type de log (info, warn, error, debug)
    `arg`: se qui doit être print

    Exemple:
    --------
    >>> console("INFO", "Bot loggin")
    """
    colors = {
        "INFO": "\033[94m",    # Blue
        "WARN": "\033[93m",    # Yellow
        "ERROR": "\033[91m",   # Red
        "DEBUG": "\033[92m",   # Green
        "FUNCTION": "\033[35m",# Violet
        "GRAY": "\033[90m",    # Gray
        "ENDC": "\033[0m"      # Reset color
    }
    now = datetime.now()
    startDate = now.strftime('%Y-%m-%d')
    startTime = now.strftime('%H:%M:%S')
    color = colors.get(type.upper(), colors["ENDC"])
    if log:
        data = f"{startDate} {startTime} {type}\t{inspect.stack()[1].function}: {arg}"
        logs(data)
    print(f"{colors['GRAY']}{startDate} {startTime} {color}{type}{colors['ENDC']}\t{colors['FUNCTION']}{inspect.stack()[1].function}{colors['ENDC']}: {arg}")

Render = {
    'DEFAULT' : '<button id="logoutButton">Logout</button><a href="/account">Paramètre du compte</a>',
    'PATIENT_LECTURE' : '<a href="/patients">Patients Pannel</a>',
    'PATIENT_EDITION' : "",
    'VEHICULE_RESA' : "",
    'VEHICULE_GESTION' : "",
    'VIDEO' : "",
    'USERS_GESTION' : '<a href="/users_administration">Administration Utilisateurs</a>',
    'RESERVED_1' : "",
    'RESERVED_2' : "",
    'ADMIN' : "",
}

def navbar_generator(access: int):
    nb = Render['DEFAULT']
    for d in Droit:
        if is_granted(d.value, access):
            nb += Render[d.name].strip()
    return nb
