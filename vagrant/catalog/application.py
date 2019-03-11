from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import UserInfo, Catalog, CatalogItem
from database_setup import Base

from sqlalchemy import *

# imports for 3rd party auth
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "sports-inventory"

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
metadata = MetaData()
session.commit()

# google sign in route
@app.route('/gconnect', methods=['POST'])
def gconnect():
    with open('client_secrets.json', 'r') as file:
        CLIENT_ID = json.load(file)['web']['client_id']
    # Verify Anti Forgery State Token received from client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store authorization code received from client
    code = request.data
    # Exchange authorization code with Google for a credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange authorization code for a credentials token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade\
                                 the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is valid/working
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Handle error if access token is not valid
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID\
                                 doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right application
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client\
                                 ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user\
                                 is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user details (name and email) from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    user_info = getUserInfo(user_id)
    return jsonify(UserInfo=[i.serialize for i in user_info])


# google logout route
@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    access_token = login_session.get('access_token')
    if (access_token is None):
        response = make_response(
                    json.dumps('Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = (h.request(url, 'GET')[0])
    print(result)
    if (result['status'] == '200'):
        del login_session['username']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Sucessfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# ****** DIFFERENT ROUTES FOR USER NAVIGATION **********
# Initial Route / Categories
@app.route('/')
@app.route('/categories')
def categories():
    users = session.query(UserInfo).all()
    for u in users:
        print(u.id)
    if('username' in login_session):
        user_id = getUserID(login_session['email'])
        return redirect(url_for('userCatalog', user_id=user_id))
    else:
        catalog = session.query(Catalog).all()
        items = session.query(CatalogItem).all()
        for c in catalog:
            print(c.name)
            print(c.user_id)
        state = ''.join(
                    random.choice(string.ascii_uppercase +
                                  string.digits)for x in range(32))
        login_session['state'] = state
        return render_template('categories.html', catalog=catalog, STATE=state)


# METHOD: GET
# Router for category Items
@app.route('/categories/<int:category_id>')
def categoryItem(category_id):
    if(category_id):
        catalog_items = session.query(
                    CatalogItem).filter_by(
                        catalog_id=category_id).all()
        catalog = session.query(Catalog).all()
        return jsonify(CatalogItem=[i.serialize for i in catalog_items])


# METHOD: GET
# Router for user login
@app.route('/categories/user/<int:user_id>')
def userCatalog(user_id):
    user_catalog = session.query(Catalog).filter_by(user_id=user_id).all()
    all_catalog = session.query(Catalog).all()
    catalog = {'userCatalog': user_catalog, 'user_id': user_id, 'all': all_catalog}
    return render_template('user_login_catalog.html', catalog=catalog)


@app.route('/categories/user/<int:user_id>/create', methods=['GET', 'POST'])
def createCatalog(user_id):
    if(user_id):
        if (request.method == 'POST'):
            if (request.form['sport_name'] != ''):
                user_id = getUserID(login_session['email'])
                newCat = Catalog(name=request.form['sport_name'],
                                 user_id=user_id)
                session.add(newCat)
                session.flush()
                session.refresh(newCat)
                flash('New Sport added to Catalog')
                message = {"name": request.form['sport_name'], "id": newCat.id}
                return render_template('new_catalog.html', message=message)
        else:
            create = {'user_id': user_id}
            return render_template('new_catalog.html', catalog_new=create)
    else:
        return redirect('/')


@app.route('/categories/user/<int:user_id>/category/<int:catalog_id>',
           methods=['GET', 'POST'])
def editCatalog(user_id, catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalogItems = session.query(
                    CatalogItem).filter_by(
                        catalog_id=catalog_id).all()
    edit = {'catalog': catalog, 'catalogItems': catalogItems,
            'user_id': user_id}
    if (request.method == 'GET'):
        return render_template('user_catalog_edit.html', catalog_edit=edit)


# helper functions for users
def createUser(login_session):
    newUser = UserInfo(name=login_session['username'],
                       email=login_session['email'],
                       picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(
            UserInfo).filter_by(
                email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(UserInfo).filter_by(id=user_id).all()
    return user


def getUserID(email):
    try:
        user = session.query(UserInfo).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
