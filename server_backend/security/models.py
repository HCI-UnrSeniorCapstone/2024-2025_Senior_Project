from flask_sqlalchemy import SQLAlchemy

from flask_security import hash_password
from sqlalchemy import String, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from app import db

# db = SQLAlchemy()
from flask_security.models import fsqla_v3 as fsqla

fsqla.FsModels.set_db_info(db)

# Association table for user roles
roles_users = db.Table(
    "users_roles",  # Match the table name in DB
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id")),
    db.Column("role_type_id", db.Integer, db.ForeignKey("role_type.id")),
)


class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = "role_type"  # Match the table name in DB

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "user"

    user_id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = db.Column(db.String(255))
    last_name: Mapped[str] = db.Column(db.String(255))
    email: Mapped[str] = db.Column(db.String(255))
    user_password: Mapped[Optional[str]] = db.Column(db.String(255), nullable=True)
    created_at: Mapped[TIMESTAMP] = db.Column(
        db.TIMESTAMP, default=func.current_timestamp()
    )
    active: Mapped[bool] = db.Column(db.Boolean, default=True)
    fs_uniquifier: Mapped[str] = db.Column(db.String(255), unique=True, nullable=False)
    fs_webauthn_user_handle: Mapped[Optional[str]] = db.Column(
        db.String(255), unique=True, nullable=True
    )
    mf_recovery_codes: Mapped[Optional[str]] = db.Column(db.Text)
    us_phone_number: Mapped[Optional[str]] = db.Column(db.String(20))
    username: Mapped[Optional[str]] = db.Column(db.String(255))
    us_totp_secrets: Mapped[Optional[str]] = db.Column(db.Text)
    confirmed_at: Mapped[Optional[TIMESTAMP]] = db.Column(db.TIMESTAMP)
    last_login_at: Mapped[Optional[TIMESTAMP]] = db.Column(db.TIMESTAMP)
    current_login_at: Mapped[Optional[TIMESTAMP]] = db.Column(db.TIMESTAMP)
    last_login_ip: Mapped[Optional[str]] = db.Column(db.String(45))
    current_login_ip: Mapped[Optional[str]] = db.Column(db.String(45))
    login_count: Mapped[int] = db.Column(db.Integer, default=0)
    tf_primary_method: Mapped[Optional[str]] = db.Column(db.String(50))
    tf_totp_secret: Mapped[Optional[str]] = db.Column(db.Text)
    tf_phone_number: Mapped[Optional[str]] = db.Column(db.String(20))
    create_datetime: Mapped[TIMESTAMP] = db.Column(
        db.TIMESTAMP, default=func.current_timestamp()
    )
    update_datetime: Mapped[TIMESTAMP] = db.Column(
        db.TIMESTAMP,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    roles: Mapped[List[Role]] = db.relationship(
        "Role",
        secondary=roles_users,  # Association table
        backref=db.backref("users", lazy="dynamic"),
    )

    # Used to make the naming match the expected naming in Flask-Security
    @property
    def id(self):
        return self.user_id

    @property
    def password(self):
        return self.user_password

    @password.setter
    def password(self, value):
        # Let Flask-Security handle salting and hashing
        self.user_password = hash_password(value)
