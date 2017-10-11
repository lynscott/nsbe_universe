import os
import sys
from flask import (Flask, render_template, request, redirect, url_for,
                                jsonify, flash, send_from_directory)
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
from passlib.hash import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, EqualTo

UPLOAD_FOLDER = 'media/eventPics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


APPLICATION_NAME = "nsbe universe"


engine = create_engine('postgresql://nsbeu@localhost:5432/nsbeu')
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


@app.route('/api/check_in/', methods=['POST'])
def userCheckIn():
    points = int(request.form['data[points]'])
    print(points)
    event_id = int(request.form['data[event_id]'])
    print(event_id)
    flash("Check-in successful!")
    current_user = session.query(User).filter_by(id=login_session['user_id']).first()
    current_user.points = current_user.points + points
    current_user.attended = current_user.attended + [event_id]
    print(current_user.attended )
    session.add(current_user)
    session.commit()
    return redirect(url_for('eventList'))

@app.route('/users/JSON')
def JSON():
    users = session.query(User).all()
    return jsonify(users=[r.serialize for r in users])


@app.route('/signup/', methods=['GET', 'POST'])
def signUp():
    users = session.query(User).all()
    if request.method == 'POST':
        newUser = User(name=request.form['name'], email=request.form[
                       'email'], year=request.form['year'], major=request.form['major'],
                       password=bcrypt.hash(request.form['password']), alias=request.form['character'],
                       alias_pic=request.form['pic'], alias_bio=request.form['bio'] )
        session.add(newUser)
        session.commit()
        user = session.query(User).filter_by(email=request.form['email']).first()
        return redirect(url_for('userLogin'))
    else:
        return render_template('signUp.html', users=users)


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
    current_user = session.query(User).filter_by(id=login_session['user_id']).first()
    # return "This page will show all my catalogs of various sauces"
    return render_template('eventList.html', events=events, current_user=current_user, creator=creator)


@app.route('/login/', methods=['GET', 'POST'])
def userLogin():
    current_user = getUserInfo(User.id)
    if request.method == 'POST':
        user = session.query(User).filter_by(email=request.form['email']).first()
        if user is not None and bcrypt.verify(request.form['password'], user.password) is True:
            login_session['provider'] = 'manual'
            login_session['username'] = user.name
            login_session['user_id'] = user.id
            login_session['points'] = user.points
            login_session['alias'] = user.alias
            login_session['pic'] = user.alias_pic
            flash('Now logged in as %s' % login_session['username'])
            return redirect(url_for('goHome'))
        elif user is None:
            flash("You dont have an account with that email address!")
        elif user is not None and bcrypt.verify(request.form['password'], user.password) is False:
            flash("Password Incorrect!")
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


@app.route('/event/<int:event_id>/delete/', methods=['GET', 'POST'])

def deleteEvent(event_id):
    eventToDelete = session.query(Event).filter_by(id=event_id).one()
    # if catalogToDelete.user_id != login_session['user_id']:
    #     return '''<script>function authFunction() {alert('You are not authorized
    #      to delete this catalog.');}</script><body onload='authFunction()''>'''
    if request.method == 'POST':
        session.delete(eventToDelete)
        session.commit()
        return redirect(url_for('showEvents', event_id=event_id))
    else:
        return render_template('deleteEvent.html', event=eventToDelete)


@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])

def editEvent(event_id):
    editedEvent = session.query(Event).filter_by(id=event_id).one()
    # if login_session['user_id'] != catalog.user_id:
    #     return '''<script>function authFunction() {alert('You are not authorized
    #      to edit this item.');}</script><body onload='authFunction()''>'''
    if request.method == 'POST':
        if request.form['name']:
            editedEvent.name = request.form['name']
        if request.form['points']:
            editedEvent.points = request.form['points']
        if request.form['date']:
            editedEvent.date = request.form['date']
        if request.form['address']:
            editedEvent.address = request.form['address']
        if request.form['details']:
            editedEvent.details = request.form['details']
        if request.form['url']:
            editedEvent.url = request.form['url']
        if request.files['picture']:
            picture = request.files['picture']
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            editedEvent.picture = filename
        session.add(editedEvent)
        session.commit()
        flash("Event Updated!")
        return redirect(url_for('showEvents', event_id=event_id))
    else:
        return render_template('editEvent.html', event_id=event_id, event=editedEvent)



@app.route('/picture/<filename>')
def uploaded_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/event/<int:event_id>/details')
def eventDetail(event_id):
    event = session.query(Event).filter_by(id=event_id).one()
    current_user = session.query(User).filter_by(id=login_session['user_id']).first()
    return render_template('eventDetail.html', id=event_id, event=event,
                            current_user=current_user)

@app.route('/logout/')
def manualLogOut():
    del login_session['provider']
    del login_session['username']
    del login_session['user_id']
    del login_session['points']
    del login_session['alias']
    del login_session['pic']
    flash('You are now logged out!')
    return redirect(url_for('goHome'))





if __name__ == '__main__':
    app.secret_key = 'nsbe_u_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
