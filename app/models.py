import getpass
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy, event

db = SQLAlchemy()


class AuditColumns:
    """Mapeamento padrão sobre a informação de criação e atualização do objeto"""

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow(), nullable=False)
    created_by = db.Column(db.String(64), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
        nullable=False,
        onupdate=datetime.utcnow(),
    )
    updated_by = db.Column(db.String(64), nullable=False)

    @event.listens_for(db.mapper, "before_insert")
    @staticmethod
    def before_insert(mapper, connection, target):
        username = getpass.getuser()
        target.created_at = datetime.utcnow()
        target.created_by = username

        target.updated_at = datetime.utcnow()
        target.updated_by = username

    @event.listens_for(db.mapper, "before_update")
    @staticmethod
    def before_update(mapper, connection, target):
        username = getpass.getuser()
        target.updated_at = datetime.utcnow()
        target.updated_by = username
