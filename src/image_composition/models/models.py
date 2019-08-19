from datetime import datetime
from ..database import db


class Alphabet(db.Model):
    """
    アルファベット画像用テーブル
    """

    __tablename__ = "alphabets"

    id = db.Column(db.Integer, primary_key=True)
    uppercase_letter = db.Column(db.String(255), nullable=False)
    lowercase_letter = db.Column(db.String(255), nullable=False)
    uppercase_image = db.Column(db.String(255), nullable=False)
    lowercase_image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )


class Scene(db.Model):
    """
    シーン画像用テーブル
    """

    __tablename__ = "scenes"

    id = db.Column(db.Integer, primary_key=True)
    scene = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
