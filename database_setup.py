#!/usr/bin/python3

''' Setup database via SQLAlchemy ORM '''

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


## user table to allow specific users to modify restaurant and menu 
## we add user_id as foreig n key to other tables
class Category(Base): # define the category table
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id
       }
   
class User(Base): # define the user table
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Item(Base): # define the Item table
    __tablename__ = 'item'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description  = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id =  Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'description'  : self.description,
           'categoryID'   : self.category_id,
           'userID'       : self.user_id
       }
 

engine = create_engine('sqlite:///catalogitems.db') # link to engine
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base.metadata.create_all(engine)  # create db