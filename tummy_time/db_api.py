# -*- coding: utf-8 -*-
import os

import sqlalchemy as sa
from sqlalchemy import asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker

_script_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

DB_FILE = os.path.join(_script_location, 'data.db')

_engine = sa.create_engine('sqlite:///{}'.format(DB_FILE))
Session = sessionmaker(bind=_engine)
_metadata = sa.schema.MetaData(_engine)

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = sa.Column(sa.String(128), primary_key=True)
    arrival_time = sa.Column(sa.DateTime, nullable=False)
    subject = sa.Column(sa.Unicode, nullable=False)


Base.metadata.create_all(_engine)


# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
def purge_db():
    _metadata.drop_all()


def update_food_arrivals_table(uid, date, data):
    return None


def filter_rest_subject(subject):
    session = Session()
    encoded_subjects = [unicode(s, 'utf8') for s in subject]
    conditions = [Restaurant.subject.contains(s) for s in encoded_subjects]

    return session.query(Restaurant).filter(or_(*conditions)).order_by(
        asc(Restaurant.arrival_time)).all()


def list_all_subjects():
    pass
