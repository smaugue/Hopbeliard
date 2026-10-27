from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pymysql

DRIVERS = {
    "sqlite":     "sqlite",
    "mysql":      "mysql+pymysql",
    "mariadb":    "mariadb+pymysql",
    "postgresql": "postgresql+psycopg",
}

class Database:
    def __init__(self,
                 type="sqlite",
                 host="localhost",
                 port=None,
                 user=None,
                 password=None,
                 database="local_db"
                ):
        if type not in DRIVERS:
            raise ValueError(f"Type de base non supporté : {type}")

        if type == "sqlite":
            url = URL.create("sqlite", database=database)
        else:
            url = URL.create(DRIVERS[type], username=user, password=password,
                             host=host, port=port, database=database)
        self.engine = create_engine(url, pool_pre_ping=True)

    def fetch_one(self, sql, **params):
        with self.engine.connect() as conn:
            return conn.execute(text(sql), params).fetchone()

    def fetch_all(self, sql, **params):
        with self.engine.connect() as conn:
            return conn.execute(text(sql), params).fetchall()

    def execute(self, sql, **params):
        with self.engine.begin() as conn:
            return conn.execute(text(sql), params).rowcount
