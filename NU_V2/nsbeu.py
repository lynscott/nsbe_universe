import os
import sys
from flask import (Flask, render_template, request, redirect, url_for,
                                jsonify, flash, send_from_directory)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Event, User
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import bleach
from flask import make_response
import requests
from functools import wraps
from werkzeug.utils import secure_filename
from passlib.hash import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, EqualTo
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import helpers as admin_helpers
from flask_mail import Mail




UPLOAD_FOLDER = 'media/eventPics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


APPLICATION_NAME = "nsbe universe"


engine = create_engine('postgresql://nsbeu@localhost:5432/nsbeu')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if  login_session['is_admin']!=True:
            return redirect(url_for('userLogin'))
        return super(MyHomeView, self).index()


class MyAdmin(FileAdmin):
    allowed_extensions = ('swf', 'jpg', 'gif', 'png')

    def is_accessible(self):
        return login_session['is_admin']==True

    def inaccessible_callback(self, name, **kwargs):
    # redirect to login page if user doesn't have access
        return redirect(url_for('goHome', next=request.url))


class UserView(ModelView):
    form_base_class = SecureForm
    column_exclude_list = ['password', 'alias_bio']
    column_searchable_list = ['name', 'email']
    form_excluded_columns = ['password', 'attended']
    can_create = False
    can_export = True

    def is_accessible(self):
        return login_session['is_admin']==True

    def inaccessible_callback(self, name, **kwargs):
    # redirect to login page if user doesn't have access
        return redirect(url_for('goHome', next=request.url))

class EventView(ModelView):
    form_base_class = SecureForm
    page_size = 50
    can_export = True

    def is_accessible(self):
        return login_session['is_admin']==True


    def inaccessible_callback(self, name, **kwargs):
    # redirect to login page if user doesn't have access

        return redirect(url_for('goHome', next=request.url))

admin = Admin(app, index_view=MyHomeView(), name='NSBE U', template_mode='bootstrap3')
admin.add_view(UserView(User, session))
admin.add_view(EventView(Event, session))
path = os.path.join(os.path.dirname(__file__), 'media/eventPics/')
admin.add_view(MyAdmin(path, name='Event Files'))


# Create login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

#Admin decorator
def admin_required(f):
    @wraps(f)
    def admin_function(*args, **kwargs):
        if login_session['is_admin'] is False:
            flash("You are not authorized for that page!", "deny")
            return redirect('/login')
        return f(*args, **kwargs)
    return admin_function


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

#create Forbidden content Error page
@app.errorhandler(KeyError)
def special_exception_handler(error):
    return render_template('500.html'), 500


@app.route('/api/check_in/', methods=['POST'])
@login_required
def userCheckIn():
    points = int(request.form['data[points]'])
    event_id = int(request.form['data[event_id]'])
    flash("Check-in successful!")
    current_user = session.query(User).filter_by(id=login_session['user_id']).first()
    current_user.points = current_user.points + points
    current_user.attended = current_user.attended + [event_id]
    print(current_user.attended )
    session.add(current_user)
    session.commit()
    return redirect(url_for('showEvents'))


@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    events = session.query(Event).all()
    return jsonify(users=[r.serialize for r in users], events=[r.serialize for r in events])



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



@app.route('/events/')
@login_required
def showEvents():
    events = session.query(Event).all()
    creator = getUserInfo(Event.user_id)
    current_user = session.query(User).filter_by(id=login_session['user_id']).first()
    return render_template('eventList.html', events=events, current_user=current_user, creator=creator)


@app.route('/login/', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        user = session.query(User).filter_by(email=request.form['email']).first()
        if user is not None and bcrypt.verify(request.form['password'], user.password) is True:
            login_session['provider'] = 'manual'
            login_session['username'] = user.name
            login_session['user_id'] = user.id
            login_session['points'] = user.points
            login_session['alias'] = user.alias
            login_session['pic'] = user.alias_pic
            login_session['is_admin'] =user.is_admin
            flash('Now logged in as %s' % login_session['username'], "success")
            return redirect(url_for('goHome'))
        elif user is None:
            flash("You dont have an account with that email address!", "deny")
        elif user is not None and bcrypt.verify(request.form['password'], user.password) is False:
            flash("Password Incorrect!", "deny")
    return render_template('login.html')


@app.route('/about/')
def About():
    return render_template('about.html')


@app.route('/leaderboard')
def leaderBoard():
    users = session.query(User).all()
    order = sorted(users, key=lambda user: user.points, reverse=True)
    return render_template('leaderboard.html', users=order)


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
@admin_required
def createEvent():
    if request.method == 'POST':
        newEvent = Event(name=request.form['name'], points= request.form['points'], address=request.form[
                           'address'], date=request.form['date'], start=request.form['start'],
                           end=request.form['end'], details=request.form['details'],
                         url=request.form['url'])
        if request.files['picture']:
            picture = request.files['picture']
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            newEvent.picture=filename
        session.add(newEvent)
        session.commit()
        flash("New Event Created!", "success")
        return redirect(url_for('showEvents'))
    else:
        return render_template('eventForm.html')


@app.route('/picture/<filename>')
def uploaded_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/event/<int:event_id>/details')
@login_required
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
    del login_session['is_admin']
    flash('You are now logged out!', "success")
    return redirect(url_for('goHome'))





if __name__ == '__main__':
    app.secret_key = 'nsbe_u_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
