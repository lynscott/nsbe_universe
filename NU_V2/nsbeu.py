import os
import sys
from flask import (Flask, render_template, request, redirect,
                    url_for, jsonify, flash, send_from_directory)
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
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'media/eventPics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def addUserPoints(user_id,event):
    user = session.query(User).filter_by(id=user_id).first()
    points =  session.query(Event).filter_by(Event.id).points
    new_points = user.points + points
    session.add(new_points)
    session.commit
    return new_points


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
    current_user = getUserInfo(User.id)
    # return "This page will show all my catalogs of various sauces"
    return render_template('eventList.html', events=events, current_user=current_user, creator=creator)


@app.route('/login/')
def userLogin():
    current_user = getUserInfo(User.id)
    return render_template('login.html', current_user=current_user)


@app.route('/about/')
def About():
    return render_template('about.html')


@app.route('/event/new', methods=['GET', 'POST'])
def createEvent():
    if request.method == 'POST':
        newEvent = Event(name=request.form['name'], points= request.form['points'], address=request.form[
                           'address'], date=request.form['date'], details=request.form['details'],
                         url=request.form['url'])
        if request.files['picture']:
            picture = request.files['picture']
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            newEvent.picture=filename
        session.add(newEvent)
        session.commit()
        flash("New Event Created!")
        return redirect(url_for('showEvents'))
    else:
        return render_template('eventForm.html')


@app.route('/picture/<filename>')
def uploaded_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/event/<int:event_id>/details')
def eventDetail(event_id):
    event = session.query(Event).filter_by(id=event_id).one()
    creator = getUserInfo(Event.user_id)
    return render_template('eventDetail.html', id=event_id, event=event,
                            creator=creator)




if __name__ == '__main__':
    app.secret_key = 'nsbe_u_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
