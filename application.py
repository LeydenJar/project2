import os

import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
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
	user = request.form.get('nome')
	return render_template('channels.html', x=user)
