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
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    year = Column(String(50), nullable=False)
    major = Column(String(50), nullable=False)
    password = Column(String(250))
    picture = Column(String(250))
    points = Column(Integer)
    alias = Column(String(50), nullable=False)
    alias_bio = Column(String(250), nullable=False)
    alias_pic = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'year': self.year,
            'major': self.major,
            'alias': self.alias,
            'points': self.points,
                }

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    points = Column(Integer, nullable=False)
    address = Column(String(250), nullable=False)
    details = Column(String(250), nullable=False)
    picture = Column(String(250))
    date = Column(String(50), nullable=False)
    url = Column(Text)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'points': self.points,
        }


engine = create_engine('sqlite:///nsbeuniv_users.db')


Base.metadata.create_all(engine)
