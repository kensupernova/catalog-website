from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
import os

import datetime

from multiprocessing.util import register_after_fork

from secret import postgresql_conn

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
    DATABASE = {
        'drivername': 'postgresql',
        'host': 'localhost',
        'port': '5432',
        'username': 'catalog',
        'password': 'catalog',
        'database': 'catalogdb'
    }

    #engine = create_engine(URL(**DATABASE))

    #db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'catalogwebsite.db')
    #engine = create_engine('sqlite:///%s' % db_file)

    #engine = create_engine('postgresql://catalog:catalog@localhost:5432/catalogdb')
    engine = create_engine(postgresql_conn)

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
