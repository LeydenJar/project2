import os

import datetime
from time import strftime
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
users = []
#error_handle = ''


class newUser(object):

	def __init__(self, name, last_beat):
		self.name = name
		self.last_beat = last_beat
		print(rooms[0], file=sys.stderr)
		users.append(self)

	def __eq__(self, other):
		return self.name == other.name

	def logout(self):
		session["user"] = None
		for i in users:
			if  self.__eq__(i):
				users.remove(i)
		del self


def getlog():
	try:
		u = session["user"].name
	except:
		u = None
	return u

def check_avaliability(name):
	a = True
	for i in users:
		if i.name == name:
			a = False
	return a
			




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
			return render_template('channels.html', x=u)
		
	else:
		candidate_to_user = request.form.get('user')
		avaliability = check_avaliability(candidate_to_user)
		if avaliability == True:
			session["user"] = newUser(candidate_to_user, strftime("%H:%M"))
			return render_template('channels.html', x=session["user"].name)
		else:
			#error_handle = 'Username is in use'
			return redirect('/')
		

@app.route("/logout")
def logout():
	session['user'].logout()
	return redirect('/')

@socketio.on('ask_rooms')
def pass_rooms():
	r = rooms
	emit('passing_rooms', {'rooms':r})

@socketio.on('send_message')
def message(msg):
	mensagem = msg["mensagem"]
	user = msg["user"]
	room = msg["current_room"]
	time = strftime("%H:%M")
	emit('broadcast_message', {'mensagem' : mensagem, 'user' : user, "time" : time}, room=room)

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
	room = data['room']
	rooml = data['rooml']
	join_room(room)
	if rooml is not None:
		leave_room(rooml)


@socketio.on('button_ask')
def butt():
	emit('button_functionality')

@socketio.on('heartbeat')
def heart():
	session['user'].last_beat = strftime("%H:%M")
	print(session['user'].last_beat, file=sys.stderr)

if __name__ == "__main__":
	socketio.run(app, debug=True)
