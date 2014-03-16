#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

import mongoengine
from flask import Flask, render_template, redirect, request, session, g, jsonify

from user import User, DEPARTMENTS
from etude import Etude
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.context_processor
def inject_user():
    """ Injects a 'user' variable in templates' context when a user is logged-in """
    if session.get('logged_in', None):
        return dict(user=User.objects(email=session['logged_in']).first())
    else:
        return dict(user=None)

@app.before_request
def load_user():
    """ Injects the current logged-in user (if any) to the request context """
    g.user = User.objects(email=session.get('logged_in')).first()


def requires_login(f):
    """  Decorator for views that requires the user to be logged-in """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in', None):
            return redirect('/login')
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    etudes = Etude.objects()
    return render_template('index.html', etudes=etudes)

@app.route("/etudes")
@requires_login
def etudes():
    etudes = Etude.objects()
    domains = set(etude.domain for etude in etudes)
    return render_template('etudes.html', etudes=etudes, domains=domains)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/signup')
def signup():
    return render_template('signup.html', departments=DEPARTMENTS)

@app.route('/signup', methods=['POST'])
def process_signup():
    email, password, name, department = [request.form[attr] for attr in ['email', 'password', 'name', 'department']]
    email = email.lower()
    user = User.new_user(email, password, name, department)
    try:
        user.save()
    except mongoengine.ValidationError as e:
        failed_data = dict(email=email, name=name, department=department)
        return render_template('signup.html', departments=DEPARTMENTS, error=e.message, **failed_data)

    session['logged_in'] = user.email
    return redirect('/')

@app.route('/login', methods=['POST'])
def process_login():
    email, password = request.form['email'].lower(), request.form['password']
    user = User.objects(email=email).first()
    if user is None or not user.valid_password(password):
        return render_template('login.html', error="Wrong password or username.", email=email)
    else:
        session['logged_in'] = user.email
        inject_user()
        load_user()
        return redirect('/')

@app.route('/api/etude/<etude_id>/notify', methods=['POST'])
def notify_etude(etude_id):
    # TODO : implement this
    etude = Etude.objects.get(number=etude_id)
    app.logger.info('Received notification by user "{}" for etude: \n{}'.format(g.user.name, etude))
    return jsonify(ok=True)


if __name__ == "__main__":
    # Creating dummy user
    User.drop_collection()
    dummy_user = User.new_user(email='dummy@insa-lyon.fr', password='123456', name='John McDummy', department='IF')
    dummy_user.save()

    app.run(host='0.0.0.0', debug=True)
