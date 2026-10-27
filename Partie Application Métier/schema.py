from sqlalchemy import (MetaData, Table, Column, Integer, String, Text,
                        Numeric, DateTime, ForeignKey, Boolean, true, func)

metadata = MetaData()

# TABLE users
users = Table("users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("lastname", String(100), nullable=False),
    Column("login", String(50), nullable=False, unique=True),
    Column("access_level", Integer, nullable=False, default=0),
    Column("active", Boolean, nullable=False, default=true()),
)

# TABLE login
login = Table("login", metadata,
    Column("login", String(50), ForeignKey("users.login", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("psswd", String(64), nullable=False),
    Column("salt", String(32), nullable=False),
    Column("need_change", Boolean, nullable=False, default=true()),
)

#chambre = Table("chambre", metadata,
#    Column("n_chambre", Integer, primary_key=True, autoincrement=False),
#    Column("temperature", Numeric(4, 1)),
#    Column("qualite_air", Integer),
#)

patient = Table("patient", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("lastname", String(100), nullable=False),
    Column("comm", Text),
)

prise_en_charge = Table("prise_en_charge", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_patient", Integer, ForeignKey("patient.id"), nullable=False),
    Column("timestamp", DateTime, server_default=func.now()),
    Column("objet", Text),
    Column("comm", Text),
)
