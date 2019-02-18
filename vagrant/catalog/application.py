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
APPLICATION_NAME = "Inventory Client"

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
metadata = MetaData()
session.commit()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if(request.args.get('state') != login_session['state']):
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        print(code)
        credentials = oauth_flow.step2_exchange(code)
        print(credentials.access_token)
    except FlowExchangeError:
        response = make_response(
                    json.dumps('Failed upgrading authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token  # noqa
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if error in retriving token abort and return error
    if (result.get('error') is not None):
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # verify if we have right access token
    gplus_id = credentials.id_token['sub']
    if (result['user_id'] != gplus_id):
        response = make_response(
                    json.dumps('Token user_id doesnt match given user'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check to see if users already logged in into system
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None and gplus_id == stored_gplus_id):
        response = make_response(
                    json.dumps(' current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
    # valid access token in session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # user info
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


@app.route('/')
@app.route('/catagories/')
def catalogMenu():
    if('username' in login_session):
        user_id = getUserID(login_session['email'])
        catalog = session.query(Catalog).filter_by(user_id=user_id).all()
        return render_template('main.html', catalog=catalog)
    else:
        catalog = session.query(Catalog).all()
        return render_template('main.html', catalog=catalog)


@app.route('/header')
@app.route('/catagories/header')
def header():
    if('username' in login_session):
        user_id = getUserID(login_session['email'])
        catalog = session.query(Catalog).filter_by(user_id=user_id).all()
        state = login_session['state']
        return render_template('header.html', STATE=state)
    else:
        catalog = session.query(Catalog).all()
        state = ''.join(
                    random.choice(string.ascii_uppercase +
                                  string.digits)for x in range(32))
        login_session['state'] = state
        return render_template('header.html', STATE=state)


@app.route('/user_catalog')
def userCatalog():
    if('username' in login_session):
        user_id = getUserID(login_session['email'])
        user_catalog = session.query(Catalog).filter_by(user_id=user_id).all()
        all_catalog = session.query(Catalog).all()
        catalog = {'userCatalog': user_catalog, 'all': all_catalog}
        return render_template('user_login_catalog.html', catalog=catalog)  
    else:
        catalog = session.query(Catalog).all()
        return render_template('main.html', catalog=catalog)


@app.route('/catagories/new', methods=['GET', 'POST'])
def newCatalogMenu():
    if('username' not in login_session):
        return redirect('/')
    else:
        if (request.method == 'POST'):
            if (request.form['sport_name'] != ''):
                user_id = getUserID(login_session['email'])
                newCat = Catalog(name=request.form['sport_name'], user_id=user_id)
                session.add(newCat)
                session.commit()
                # catalogAdded = session.query(
                #                 Catalog).filter_by(
                #                     name=request.data).all()
                flash('New Sport added to Catalog')
                message = request.form['sport_name']
                return render_template('new_catalog.html', message=message)
        else:
            catalog = session.query(Catalog).all()
            return render_template('new_catalog.html', catalog=catalog)


@app.route('/categories/<int:category_id>/newItem', methods=['GET', 'POST'])
def catalogMenuItem(category_id):
    catalogItems = session.query(
                    CatalogItem).filter_by(
                        catalog_id=category_id).all()
    # catalog = session.query(Catalog).all()
    if (request.method == 'POST'):
        if (request.form['name'] != ''):
            # editRes.name = request.form['name']
            # session.add(editRes)
            session.commit()
            flash('res edited')
        return redirect(url_for('showRestaurants'))
    else:
        return jsonify(CatalogItem=[i.serialize for i in catalogItems])


@app.route('/user_catalog/<int:catalog_id>/delete', methods=['POST'])
def deleteCatalog(catalog_id):
    deleteCat = session.query(Catalog).filter_by(id=catalog_id).one()
    if (request.method == 'POST'):
        session.delete(deleteCat)
        session.commit()
        flash('Item deleted')
        return 'success'


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
