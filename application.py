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



class newUser(object):

	def __init__(self, name, last_beat):
		self.name = name
		self.last_beat = last_beat
		session["user"] = name
		users.append(self)

	def logout(self, name):
		users.remove(self)
		session["user"] = None
		del self


def getlog():
	try:
		u = session["user"]
	except:
		u = None
	return u

def adduser(user):
	if user not in users:
	#	user = newUser(user, strftime("%H:%M"))
		users.append(user)
		v=user
	else:
		session["user"] = None
		v=None
	for i in range(0, len(users)):
		print(users[i], file=sys.stderr)
	return v



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
			v = adduser(session['user'])
			if v == None:
				return redirect('/')
			else:
				return render_template('channels.html', x=v)
	else:
		session['user'] = request.form.get('user')
		v = adduser(session['user'])
		if v == None:
			return render_template('home.html', error="User already in use")
		else:
			return render_template('channels.html', x=v)
		

@app.route("/logout")
def logout():
	user = session['user']
	users.remove(user)
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
	#x = strftime()
	#print("Cheguei ate aqui", file=sys.stderr)
	time = strftime("%H:%M")
	#print(datetime.datetime.now.hour, file=sys.stderr)
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
	print('**********im starting the function join_room**************', file=sys.stderr)
	room = data['room']
	rooml = data['rooml']
	join_room(room)
	print("****************Runing Serverside*************", file=sys.stderr)
	if rooml is not None:
		leave_room(rooml)


@socketio.on('button_ask')
def butt():
	emit('button_functionality')

@socketio.on('heartbeat')
def heart():

	session['last_beat'] = strftime("%H:%M")
	print(session['last_beat'], file=sys.stderr)

if __name__ == "__main__":
	socketio.run(app, debug=True)
