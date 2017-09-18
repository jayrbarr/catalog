#!/usr/bin/env python2
#
# Database setup for catalog app
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False, unique=True)
	
class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	email = Column(String(50), nullable=False)
	
class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	description = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	created = Column(DateTime(timezone=True), server_default=func.now())
	
	@property
	def serialize(self):
		return {
		   'name': self.name,
		   'description': self.description
		}
	
engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.create_all(engine)