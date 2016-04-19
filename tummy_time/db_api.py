# -*- coding: utf-8 -*-
import os

import sqlalchemy as sa
from sqlalchemy import asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker

import constants

DB_FILE = os.path.join(constants.DATA_DIR, 'data.db')
if not os.path.exists(constants.DATA_DIR):
    os.makedirs(constants.DATA_DIR)

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


class Alias(Base):
    __tablename__ = 'aliases'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode, nullable=False)
    query_keywords = sa.Column(sa.Unicode, nullable=False)


Base.metadata.create_all(_engine)


# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
def purge_db():
    _metadata.drop_all()


def _str_list_to_unicode(lst):
    # type: (lst) -> list
    return map(lambda x: x if isinstance(x, unicode) else unicode(x, 'utf8'),
               lst)


def filter_restaurant_subject(subject):
    # type: (subject) -> list
    session = Session()
    encoded_subjects = _str_list_to_unicode(subject)
    conditions = [Restaurant.subject.contains(s) for s in encoded_subjects]

    return session.query(Restaurant).filter(or_(*conditions)).order_by(
        asc(Restaurant.arrival_time)).all()


# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
def _alias_list(alias_name, session):
    return session.query(Alias).filter(Alias.name == alias_name).first()


def alias_create(alias_name, query):
    session = Session()
    alias_name = unicode(alias_name, 'utf8')
    if _alias_list(alias_name, session):
        raise LookupError('duplicate alias creation')
    encoded_query = u' '.join([unicode(q, 'utf8') for q in query])
    new_alias = Alias(name=alias_name, query_keywords=encoded_query)
    session.add(new_alias)
    session.commit()


def alias_list_all():
    return Session().query(Alias).all()


def alias_query_get(alias_name):
    alias_name = unicode(alias_name, 'utf8')

    return _alias_list(alias_name, Session())


def alias_delete(alias_name):
    session = Session()
    alias_name = unicode(alias_name, 'utf8')
    a = _alias_list(alias_name, session)
    session.delete(a)
    session.commit()
