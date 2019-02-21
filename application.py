import os

import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret"
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
	user = request.form.get('user')
	return render_template('channels.html', x=user)

@socketio.on('send_message')
def message(msg):
	mensagem = msg["mensagem"]
	emit('broadcast_message', {'mensagem' : mensagem}, broadcast=True)

if __name__ == "__main__":
	socketio.run(app, debug=True)
