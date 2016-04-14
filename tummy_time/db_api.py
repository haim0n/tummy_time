import os

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

_script_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

DB_FILE = os.path.join(_script_location, 'data.db')

Base = declarative_base()
_session = None


# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
class RestaurantData(Base):
    __tablename__ = 'restaurant'
    id = sa.Column(sa.String, primary_key=True)
    arrival_time = sa.Column(sa.DateTime, nullable=False)
    subject = sa.Column(sa.Unicode, nullable=False)


archive_states = {'fetched': 0, 'parsed': 1}


class ArchivedData(Base):
    __tablename__ = 'archived_data'
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False)
    state = sa.Column(sa.Integer, nullable=False)


# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
def _get_db_engine():
    return sa.create_engine('sqlite:///{}'.format(DB_FILE))


def get_db_session():
    if not _session:
        global _session
        db_session = sa.orm.sessionmaker(bind=_get_db_engine())
        _session = db_session()

    return _session


def purge_db():
    Base.metadata.create_all(_get_db_engine())


def update_food_arrivals_table(uid, date, data):
    return None
