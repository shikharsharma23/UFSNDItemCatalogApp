from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    jsonify
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User


# ouath specific
from flask import session as login_session  # login session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///catalogitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()  # database session

# auth specific client secret for the app to link it
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Methods to create and get new user info
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    # in this login session create a new user using info retrieved from
    # showLogin
    session.add(newUser)  # add the new user and commit
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):  # get user form user id
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get user from email (used at time of oauth login)


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# END


@app.route('/')
@app.route('/categories')
def showCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template(
            'categoriesWithLogin.html',
            categories=categories)
    return render_template('categories.html', categories=categories)


@app.route('/categories/<selected_category>')
def showItems(selected_category):
    selected_category = session.query(
        Category).filter_by(name=selected_category).one()
    items = session.query(Item).filter_by(
        category_id=selected_category.id).all()
    return render_template(
            'item.html',
            items=items,
            selected_category=selected_category)


@app.route('/categories/<selected_category>/<selected_item>')
def showDescription(selected_category, selected_item):
    items = session.query(Item).filter_by(name=selected_item).all()
    return render_template('itemDescription.html', items=items)


@app.route('/categories/<selected_category>/add', methods=['GET', 'POST'])
def addItem(selected_category):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=selected_category).one()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if(request.method == 'POST'):
        item = Item(
            user_id=user.id,
            name=request.form['name'],
            description=request.form['description'],
            category_id=category.id)
        session.add(item)
        session.commit()
        return redirect(url_for('showItems', selected_category=category.name))
    else:
        return render_template('newItem.html', selected_category=category.name)


@app.route(
    '/categories/<selected_category>/<selected_item>/edit',
    methods=[
        'GET',
        'POST'])
def editItem(selected_category, selected_item):
    if 'username' not in login_session:
        return redirect('/login')
    itemToEdit = session.query(Item).filter_by(name=selected_item).one()
    # if user access this link directly, say that you are not authorized
    if login_session['user_id'] != itemToEdit.user_id:
        return "<script>function myFunction() {alert('Please navigate back.\
        You are not authorized to edit this item . Please create your own \
        item in order to edit it.');}</script><body onload='myFunction()''>"

    if(request.method == 'POST'):
        itemToEdit.name = request.form['name']
        itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        return redirect(
            url_for(
                'showItems',
                selected_category=selected_category))
    else:
        return render_template(
            'editItem.html',
            item=itemToEdit,
            selected_category=selected_category)


@app.route(
    '/categories/<selected_category>/<selected_item>/delete',
    methods=[
        'GET',
        'POST'])
def deleteItem(selected_category, selected_item):
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(name=selected_category).one()
    item = session.query(Item).filter_by(name=selected_item).all()

    # multiple items fetched, delete first one
    if isinstance(item, (list,)):
        item = item[0]

    # if user access this link directly, say that you are not authorized
    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('Please navigate back\
        .You are not authorized to delete this item . Please create your\
        own item in order to\
        delete/manage it.');}</script><body onload='myFunction()''>"

    if(request.method == 'POST'):
        session.delete(item)
        session.commit()
        return redirect(
            url_for(
                'showItems',
                selected_category=selected_category))
    else:
        return render_template('deleteItem.html', item=item, category=category)


@app.route('/catalog.json')
def catalogJSON():
    # TODO : trying to do with join  and show as one massive json
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(
        Categories=[
            c.serialize for c in categories], Items=[
            i.serialize for i in items])


# Adding authentication stuff
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# This method is called with user details to verify
# nd result needs to be sent back after various checks
@app.route('/gconnect', methods=['POST'])  # oauth handling code
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Lets see if this user  exists else create a new user
    user_id = getUserID(login_session['email'])
    if not user_id:  # if this email was not seen before
        user_id = createUser(login_session)  # create this user
    # update the globaly shared login_session with the current user_id which
    # is logged in
    login_session['user_id'] = user_id

    # Output to be shown when logged in and redirecting to the desired homepage
    output = ''
    output += '<h1 style="margin:auto;'
    output += 'text-align:center;color:545e78;">Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: '
    output += '150px; margin-left:40%;margin-top:3%;"> '
    print("done!")
    return output


@app.route('/gdisconnect')  # to disconnect user
def gdisconnect():
    access_token = login_session.get('access_token')  # get access token
    if access_token is None:  # must be vaid
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    # make a call to revoke to google api
    url = 'https://accounts.google.com/o/'
    url += 'oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    # check results is ok or some error occured
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']  # delete all saved states
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps('Fail token revoke for user.'))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5003)
