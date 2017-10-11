import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    year = Column(String(50), nullable=False)
    major = Column(String(50), nullable=False)
    password = Column(String(500))
    picture = Column(String(500))
    points = Column(Integer, default=0)
    alias = Column(String(50), nullable=False)
    alias_bio = Column(String(500), nullable=False)
    alias_pic = Column(String(500), nullable=False)
    attended = Column(ARRAY(Integer), default=0)

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
            'attended': self.attended,
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


engine = create_engine('postgresql://nsbeu@localhost:5432/nsbeu')


Base.metadata.create_all(engine)
