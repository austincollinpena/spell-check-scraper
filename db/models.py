# Many to one https://python-gino.readthedocs.io/en/v0.8.5/loaders.html#many-to-one-relationship
from db import db


class Domain(db.Model):
    __tablename__ = "domains"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.domain


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String, nullable=False)
    errors = db.Column(db.ARRAY(db.String))
    likely_errors = db.Column(db.ARRAY(db.String))
    page_response = db.Column(db.Integer)
    domain = db.Column(db.Integer, db.ForeignKey('domains.id'))
