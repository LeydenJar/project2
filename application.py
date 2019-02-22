import os

import datetime
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret"
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

now = datetime.datetime.now()


def getlog():
	try:
		u = session["user"]
	except:
		u = None
	return u


@app.route("/")
def index():
	u = getlog()
	if u == None:
		return render_template('home.html')
	else:
		return redirect('/channels')



@app.route("/channels", methods=['POST', 'GET'])
def canais():

	if request.method=='GET':
		u = getlog()
		if u == None:
			return redirect('/')
		else:
			return render_template('channels.html', x=session['user'])
	else:
		session['user'] = request.form.get('user')
		return render_template('channels.html', x=session['user'])

@app.route("/logout")
def logout():
	session['user']=None
	return redirect('/')

@socketio.on('send_message')
def message(msg):
	mensagem = msg["mensagem"]
	user = msg["user"]
	emit('broadcast_message', {'mensagem' : mensagem, 'user' : user}, broadcast=True)

if __name__ == "__main__":
	socketio.run(app, debug=True)
