import os

import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = 'False'
app.config["SESSION_TYPE"] = "filesystem"

now = datetime.datetime.now()


def getlog():
	try:
		u = session["user"]
	except:
		u = None
	return u


@app.route("/")
def index():
    return render_template("home.html")
@app.route("/channels", methods=['POST'])
def canais():
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}

	user = request.form.get('nome', headers=readers)
	return user