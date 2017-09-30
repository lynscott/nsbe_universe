import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    points = Column(Integer)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    points = Column(Integer)
    address = Column(String(250), nullable=False)
    details = Column(String(250), nullable=False)
    picture = Column(String(250))
    date = Column(Date, nullable=False)
    url = Column(Text)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'points': self.points,
        }


engine = create_engine('sqlite:///nsbeuniv.db')


Base.metadata.create_all(engine)
