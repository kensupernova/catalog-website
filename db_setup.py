#coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
import os

import datetime

from multiprocessing.util import register_after_fork

from secret import postgresql_conn_aws, local_psql, local_psql_2, local_sqlite

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)

    created = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    created = Column(DateTime, default=datetime.datetime.utcnow)

    
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,    
            'description': self.description
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    created = Column(DateTime, default=datetime.datetime.utcnow)
   

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category,  backref=backref("items", cascade="all, delete-orphan"))
    
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {  
            'id': self.id,
            'name': self.name,
            'category': self.category.name,
            'description': self.description
        }

def get_engine():
    ## method 1: local postsql database
    # engine = create_engine(URL(**LOCAL_PSQL_DATABASE))

    ## method 1.1: local postsql
    #engine = create_engine(local_psql_db_2)

    ## method 2: local sqlite database
    
    engine = create_engine(local_sqlite)

    
    ## method 3: database on AWS Server
    # engine = create_engine(postgresql_conn_aws)

    # 注册数据引擎
    register_after_fork(engine, engine.dispose)
    
    Base.metadata.create_all(engine)

    return engine

def get_DBSession():
    engine = get_engine()

    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    ## connect to db

    DBSession = sessionmaker(bind=engine)
    # If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()

    return session
