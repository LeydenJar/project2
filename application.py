import os

import datetime
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_session import Session
import sys

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret"
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

now = datetime.datetime.now()
rooms = ['pixirica', 'arruai']


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
	print('I am starting the function', file=sys.stderr)
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

@socketio.on('ask_rooms')
def pass_rooms():
	print('**********I am starting the function ASKROOMS**************', file=sys.stderr)
	r = rooms
	emit('passing_rooms', {'rooms':r})

@socketio.on('send_message')
def message(msg):
	mensagem = msg["mensagem"]
	user = msg["user"]
	room = msg["current_room"]
	emit('broadcast_message', {'mensagem' : mensagem, 'user' : user}, room=room)

@socketio.on('create_room')
def create_room(data):
	room_name = str(data["room_name"])
	rooml = data['rooml']
	rooms.append(room_name)
	leave_room(rooml)
	join_room(room_name)
	emit('broadcast_new_room', {'room_name' : room_name}, broadcast=True)


@socketio.on('join_room')
def join(data):
	print('**********im starting the function join_room**************', file=sys.stderr)
	room = data['room']
	rooml = data['rooml']
	print(room,  file=sys.stderr)
	join_room(room)
	if rooml is not None:
		leave_room(rooml)


@socketio.on('button_ask')
def butt():
	emit('button_functionality')


if __name__ == "__main__":
	socketio.run(app, debug=True)
