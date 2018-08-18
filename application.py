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
	categories = session.query(Category).all() 
	return render_template('categories.html', categories=categories)


@app.route('/categories/<selected_category>')
def showItems(selected_category):
	selected_category = session.query(Category).filter_by(name=selected_category).one() 
	items = session.query(Item).filter_by(category_id=selected_category.id).all()
	return render_template('item.html', items=items,selected_category = selected_category)


@app.route('/categories/<selected_category>/<selected_item>')
def showDescription(selected_category,selected_item):
	items = session.query(Item).filter_by(name=selected_item).all() 
	return render_template('itemDescription.html', items=items)


@app.route('/categories/<selected_category>/add',methods=['GET', 'POST'])
def addItem(selected_category):
    category = session.query(Category).filter_by(name=selected_category).one() 
    if(request.method=='POST'):
        item=Item(name=request.form['name'],description=request.form['description'],category_id=category.id) 
        session.add(item)
        session.commit()
        return redirect(url_for('showItems',selected_category=category.name))
    else:
        return render_template('newItem.html',selected_category=category.name)


@app.route('/categories/<selected_category>/<selected_item>/edit',methods=['GET', 'POST'])
def editItem(selected_category,selected_item):
    itemToEdit = session.query(Item).filter_by(name=selected_item).one()
    if(request.method=='POST'):
        itemToEdit.name=request.form['name']
        itemToEdit.description=request.form['description']
        session.add(itemToEdit)
        session.commit()
        return redirect(url_for('showItems',selected_category=selected_category))
    else:
        return render_template('editItem.html',item=itemToEdit,selected_category=selected_category)


@app.route('/categories/<selected_category>/<selected_item>/delete', methods=['GET', 'POST'])
def deleteItem(selected_category,selected_item):
    category=session.query(Category).filter_by(name=selected_category).one()
    item = session.query(Item).filter_by(name=selected_item).all()
    if isinstance(item, (list,)): # multiple items fetched, delete first one
    	item=item[0]
    if(request.method=='POST'):
        session.delete(item)
        session.commit()
        return redirect(url_for('showItems',selected_category=selected_category))
    else:
        return render_template('deleteItem.html',item=item,category=category)

@app.route('/catalog.json')
def catalogJSON():
    #result = session.query(Item,Category).filter(Item.category_id == Category.id).all() # trying to do with join . TodO : serialze and return joined resut
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(Categories = [c.serialize for c in categories], Items = [i.serialize for i in items])

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5003)



