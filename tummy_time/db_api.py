import os

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

_script_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

DB_FILE = os.path.join(_script_location, 'data.db')



Base = declarative_base()


class RestaurantData(Base):
    __tablename__ = 'restaurant'
    id = sa.Column(sa.String, primary_key=True)
    arrival_time = sa.Column(sa.DateTime, nullable=False)
    subject = sa.Column(sa.Unicode, nullable=False)


def create_db_session(engine):
    engine = sa.create_engine('sqlite:///{}'.format(DB_FILE))
    db_session = sa.orm.sessionmaker(bind=engine)

    return db_session()


def purge_db():
    engine = sa.create_engine('sqlite:///{}'.format(DB_FILE))
    Base.metadata.create_all(engine)
