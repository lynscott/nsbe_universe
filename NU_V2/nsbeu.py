from flask import (Flask, render_template, request, redirect,
                    url_for, jsonify, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Event, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)


APPLICATION_NAME = "nsbe universe"


engine = create_engine('sqlite:///nsbeuniv.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


#Helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/home/')
def goHome():
    current_user = getUserInfo(User.id)
    return render_template('index.html', current_user=current_user)

# Show all sauce catalogs
@app.route('/events/')
def showEvents():
    events = session.query(Event).all()
    creator = getUserInfo(Event.user_id)
    # return "This page will show all my catalogs of various sauces"
    return render_template('eventList.html', events=events, creator=creator)


if __name__ == '__main__':
    app.secret_key = 'nsbe_u_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
