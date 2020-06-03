# Many to one https://python-gino.readthedocs.io/en/v0.8.5/loaders.html#many-to-one-relationship
from db import gino_db


class Domain(gino_db.Model):
    __tablename__ = "domains"

    id = gino_db.Column(gino_db.Integer, primary_key=True)
    domain = gino_db.Column(gino_db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.domain


class Page(gino_db.Model):
    __tablename__ = "pages"

    id = gino_db.Column(gino_db.Integer, primary_key=True)
    page = gino_db.Column(gino_db.String, nullable=False)
    errors = gino_db.Column(gino_db.ARRAY(gino_db.String))
    likely_errors = gino_db.Column(gino_db.ARRAY(gino_db.String))
    page_response = gino_db.Column(gino_db.Integer)
    domain = gino_db.Column(gino_db.Integer, gino_db.ForeignKey('domains.id'))
