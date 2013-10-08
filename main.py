#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from user import User
from etude import Etude

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/<username>")
def userprofile(username):
    cur_user = User("ahmed.kachkach@gmail.com", "password")
    cur_user.name = username

    return render_template('index.html', user=cur_user)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)