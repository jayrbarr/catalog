#!/usr/bin/env python
#
# Catalog App

from flask import Flask, render_template, url_for, request, redirect
from flask import flash, session as login_session, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
import os

MAIN_DIRECTORY = os.path.dirname(__file__)
JSON_FILEPATH = os.path.join(MAIN_DIRECTORY, 'client_secrets.json')
CLIENT_ID = json.loads(open(
    JSON_FILEPATH,
    'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

app = Flask(__name__)

engine = create_engine('postgresql://catalog:catalog@127.0.0.1/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# load static global list of categories. Not editable in this version.
categories = session.query(Category).order_by(Category.name)

# Google sign-in Oauth2 success response - initialize login session
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application.json'
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/'
           'tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error'), 500))
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {
        'access_token': credentials.access_token,
        'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # create new user if user doesn't already exist
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = user_id

    output = "<p>You are now logged in as " + login_session['username']+"<p>"
    return output


# Logout - revoke current user token and reset login_session
@app.route('/logout/', methods=['POST'])
def logout():
    # only logout a user who has already logged in
    credentials = login_session.get('credentials')
    if credentials is None:
        return 'Current user is not logged in.'
    # revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # reset user session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        return 'Successfully logged out.'
    else:
        return 'Failed to revoke token for given user.'


# main catalog - latest 10 items in descending datetime order
@app.route('/')
@app.route('/catalog/')
def catalog():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    items = session.query(Item).order_by(Item.created.desc()).limit(10)
    if 'username' not in login_session:
        return render_template(
            'publiccatalog.html',
            categories=categories,
            items=items, STATE=state)
    return render_template(
        'catalog.html',
        categories=categories,
        items=items,
        STATE=state)

# Google verification
@app.route('/googled99ce8bde72b29d0.html')
def googleVerification():
	return render_template('googled99ce8bde72b29d0.html')

# single category listing - all items in category
@app.route('/catalog/<category>/')
def showCategory(category):
    cat = session.query(Category).filter_by(name=category).one_or_none()
    if cat is not None:
        catItems = session.query(Item).filter_by(
            category_id=cat.id).order_by(Item.name)
        if 'username' not in login_session:
            return render_template(
                'publiccategory.html',
                category=category,
                categories=categories,
                items=catItems)
        return render_template(
            'category.html',
            category=category,
            categories=categories,
            items=catItems)
    return redirect(url_for('catalog'))


# new item creation
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        flash('Not authorized to create new item.')
        return redirect('/catalog/')
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=int(request.form['category']),
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New item created!')
        return redirect(url_for('catalog'))
    else:
        return render_template('newItem.html', categories=categories)


# single item listing
@app.route('/catalog/<category>/<item>/')
def showItem(category, item):
    showItem = session.query(Item).filter_by(name=item).one_or_none()
    creator = getUserInfo(showItem.user_id)
    if showItem is not None:
        if 'username' in login_session:
            if creator.id == login_session['user_id']:
                return render_template('item.html', item=showItem)
        return render_template('publicitem.html', item=showItem)
    return redirect(url_for('catalog'))


# JSON API endpoint for single item name and description
@app.route('/catalog/<category>/<item>/api/')
def itemApi(category, item):
    apiItem = session.query(Item).filter_by(name=item).one_or_none()
    if apiItem is not None:
        return jsonify(item=apiItem.serialize)
    return redirect(url_for('catalog'))


# edit item
@app.route('/catalog/<item>/edit/', methods=['GET', 'POST'])
def editItem(item):
    editItem = session.query(Item).filter_by(name=item).one_or_none()
    if editItem is not None:
        creator = getUserInfo(editItem.user_id)
        if 'username' in login_session:
            if creator.id == login_session[user_id]:
                if request.method == 'POST':
                    editItem.name = request.form['name']
                    editItem.description = request.form['description']
                    editItem.category_id = request.form['category']
                    session.add(editItem)
                    session.commit()
                    flash('Item edited!')
                    return redirect(
                        url_for(
                            'showItem',
                            category=editItem.category.name,
                            item=editItem.name))
                else:
                    return render_template(
                        'editItem.html',
                        item=editItem,
                        categories=categories)
    flash('Not authorized to edit item.')
    return redirect(url_for('catalog'))


# delete item
@app.route('/catalog/<item>/delete/', methods=['GET', 'POST'])
def deleteItem(item):
    delItem = session.query(Item).filter_by(name=item).one_or_none()
    if delItem is not None:
        creator = getUserInfo(delItem.user_id)
        if 'username' in login_session:
            if creator.id == login_session[user_id]:
                if request.method == 'POST':
                    session.delete(delItem)
                    session.commit()
                    flash('Item deleted!')
                else:
                    return render_template('deleteItem.html', item=delItem)
    flash('Not authorized to edit item.')
    return redirect(url_for('catalog'))


# function to retrieve user ID from email address
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# function to retrieve User from user ID
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# create new User in database
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.debug = True
    app.run()
