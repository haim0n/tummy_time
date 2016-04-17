# -*- coding: utf-8 -*-
import os

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
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


def filter_rest_subject(subj):
    session = Session()
    return session.query(Restaurant).filter(
        Restaurant.subject.contains(subj)).all()


def list_all_subjects():
    pass