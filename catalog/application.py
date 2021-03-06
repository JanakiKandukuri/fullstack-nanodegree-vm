#!/usr/bin/env python
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


# API END POINTS
@app.route('/JSON')
@app.route('/categories/JSON')
def catalogJSON():
    catalog = session.query(Catalog).all()
    all_cat = []
    for c in catalog:
        catalogItem = session.query(
                       CatalogItem).filter_by(catalog_id=c.id).all()
        all_cat.append({"id": c.id,
                        "name": c.name,
                        "submenu": [r.serialize for r in catalogItem]})
    return jsonify(all_cat)


# ROUTES TO RENDER HTML PAGES
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
        response = make_response(redirect(url_for('categories')))
        response.delete_cookie('login_session')
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
    catalog = {'userCatalog': user_catalog,
               'user_id': user_id, 'all': all_catalog}
    return render_template('user_login_catalog.html', catalog=catalog)


# Create new catalog or view catalog
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
                session.commit()
                message = {"name": request.form['sport_name'], "id": newCat.id}
                return render_template('new_catalog.html',
                                       message=message, user_id=user_id)
        else:
            return render_template('new_catalog.html', user_id=user_id)
    else:
        return redirect('/')


# edit catalog
@app.route('/categories/user/<int:user_id>/category/<int:catalog_id>',
           methods=['GET', 'POST'])
def editCatalog(user_id, catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalogItems = session.query(
                    CatalogItem).filter_by(
                        catalog_id=catalog_id,
                        user_id=user_id).all()
    edit = {'catalog': catalog, 'catalogItems': catalogItems,
            'user_id': user_id}
    if (request.method == 'GET'):
        return render_template('user_catalog_edit.html', catalog_edit=edit)
    elif(request.method == 'POST'):
        session.query(
                      CatalogItem).filter_by(
                        catalog_id=catalog_id,
                        user_id=user_id).delete(synchronize_session=False)
        session.commit()
        equipment_name = request.form.getlist('equipment_name')
        description = request.form.getlist('description')
        sport_name = request.form['sport_name']
        catalog.name = sport_name
        session.add(catalog)
        for index, name in enumerate(equipment_name):
            eq_name = name
            des_name = description[index] if description[index] else ""
            newCatItem = CatalogItem(name=eq_name, description=des_name,
                                     user_id=user_id, catalog_id=catalog_id)
            session.add(newCatItem)
            session.flush()
            session.commit()
        return redirect(url_for('userCatalog', user_id=user_id))


# delete catalog
@app.route('/categories/user/<int:user_id>/category/<int:catalog_id>/delete',
           methods=['POST'])
def deleteCatalog(user_id, catalog_id):
    deleteCat = session.query(Catalog).filter_by(id=catalog_id).one()
    if (request.method == 'POST'):
        session.delete(deleteCat)
        session.commit()
        return redirect(url_for('userCatalog', user_id=user_id))


# add new items to catalog
@app.route('/categories/user/<int:user_id>/category/<int:catalog_id>/items',
           methods=['POST'])
def newCatalogItems(user_id, catalog_id):
    if (request.method == 'POST'):
        data = json.loads(request.data)
        if(data):
            for d in list(data):
                newCatItem = CatalogItem(name=d['name'],
                                         description=d['description'],
                                         user_id=user_id,
                                         catalog_id=catalog_id)
                session.add(newCatItem)
                session.flush()
                session.commit()
                print("created")
            return '/categories/user/'+str(user_id)
        else:
            return render_template('/')


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
