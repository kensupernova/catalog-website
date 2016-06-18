from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime

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
    category = relationship(Category)
    
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


engine = create_engine('sqlite:///catalogwebsite.db')


Base.metadata.create_all(engine)
