from flask import Flask, render_template, request, url_for, redirect, flash, jsonify # for flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item,User

app = Flask(__name__)

engine = create_engine('sqlite:///catalogitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession() # database session


@app.route('/')
@app.route('/categories')
def showCategories():
	categories = session.query(Restaurant).all() 
	return render_template('categories.html', categories=categories)


@app.route('/categories/<selected_category>')
def showItems(selected_category):
	return selected_category

@app.route('/categories/<selected_category>/<selected_item>')
def showDescription(selected_category,selected_item):
	return selected_item


@app.route('/categories/<selected_category>/add')
def addItem(selected_category,selected_item):
	return 'Page to Add Item'


@app.route('/categories/<selected_category>/<selected_item>/edit')
def editItem(selected_category,selected_item):
	return 'Page to Edit Item'


@app.route('/categories/<selected_category>/<selected_item>/delete')
def deleteItem(selected_category,selected_item):
	return 'Page to Delete Item'

@app.route('/catalog.json'):
def returnJson():
	return 'returns Json'

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5003)





