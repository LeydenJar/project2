import os

import datetime
import time, threading
from time import strftime, strptime
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


rooms = []
users = []

class new_Message(object):
	def __init__(self, user, content, timestamp, channel):
		if channel == None:
			return false
		self.user = user
		self.content = content
		self.timestamp = timestamp
		self.channel = channel
		if len(channel.messages) == 100 or len(channel.messages) > 100:
			del channel.messages[0]
		channel.messages.append(self)


class newRoom(object):
	def __init__(self, name, prev_Room, user1):
		self.name = name
		self.messages = []
		self.users = [user1]
		self.member_count = 1
		leave_room(prev_Room)
		if session["user"].current_room is not None:
			session["user"].current_room.users.remove(session["user"].name)
			session["user"].current_room.member_count -= 1
		join_room(name)
		session["user"].current_room = self
		rooms.append(self)

	def change(self, new_room, old_room):
		if old_room is not None:
			leave_room(old_room)
		self.users.remove(session["user"].name)
		self.member_cont -=1
		join_room(new_room)
		for i in rooms:
			if i.name == new_room:
				session["user"].current_room = i
		session["user"].current_room.users.append(session["user"].name)
		session["user"].current_room.member_count += 1


class newUser(object):
	def __init__(self, name, last_beat):
		self.name = name
		self.last_beat = last_beat
		self.current_room = None
		users.append(self)

	def __eq__(self, other):
		return self.name == other.name

	def logout(self):
		session["user"] = None
		for i in users:
			if  self.__eq__(i):
				users.remove(i)
		del self


def clean_users():
	print("starting the function clean_users")
	now = time.time()
	for i in users:
		if now - i.last_beat > 60:
			print("removed " + i.name, file=sys.stderr)
			users.remove(i)
	threading.Timer(60, clean_users).start()
	print("Ending the function Clean_Users", file=sys.stderr)

def getlog():
	try:
		u=None
		for i in users:
			if session["user"].__eq__(i):
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
			



#********************************.Routes and socket comunications.**************************************

@app.route("/")
def index():
	u = getlog()
	if u == None:
		return render_template('home.html')
	else:
		return redirect('/channels')



clean_users()

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
			session["user"] = newUser(candidate_to_user, time.time())
			return render_template('channels.html', x=session["user"].name)
		else:
			return redirect('/')
		

@app.route("/logout")
def logout():
	session['user'].logout()
	return redirect('/')

@socketio.on('ask_rooms')
def pass_rooms():
	r = []
	for i in rooms:
		r.append(i.name)
	emit('passing_rooms', {'rooms':r})

@socketio.on('send_message')
def message(msg):
	print("Hey, i am trying to send that message you sent!", file=sys.stderr)
	mensagem = msg["mensagem"]
	user = msg["user"]
	room = session["user"].current_room
	#room=msg["current_room"]
	time = strftime("%H:%M")
	if room == None:
		print("I dont find the room", file=sys.stderr)
	m = new_Message(user, mensagem, time, room)
	print("i am about to emit a message to" + m.channel.name, file=sys.stderr)
	emit('broadcast_message', {'mensagem' : m.content, 'user' : m.user, "time" : m.timestamp}, room=m.channel.name)

@socketio.on('create_room')
def create_room(data):
	print("******************Just Got Here", file=sys.stderr)
	room_name = str(data["room_name"])
	rooml = data['rooml']
	print(room_name + "   " + rooml ,file=sys.stderr)
	n = newRoom(room_name, rooml, session["user"].name)
	#rooms.append(room_name)
	#leave_room(rooml)
	#join_room(room_name)
	emit('broadcast_new_room', {'room_name' : room_name}, broadcast=True)


@socketio.on('join_room')
def join(data):
	new_room = data['room']
	try:
		old_room = session["user"].current_room
	except:
		old_room = None
	print("i am trying to put you in the room", file=sys.stderr)
	#session["user"].current_room.change(new_room, old_room)
	if old_room is not None:
		leave_room(old_room)
		old_room.users.remove(session["user"].name)
		old_room.member_count -=1
	
	i = None
	for i in rooms:
		print("testing the room" + i.name, file=sys.stderr)
		if i.name == new_room:
			print("found your room", file = sys.stderr)
			session["user"].current_room = i
			break
	session["user"].current_room = i
	join_room(new_room)
	session["user"].current_room.users.append(session["user"].name)
	session["user"].current_room.member_count += 1

	for i in session["user"].current_room.messages:
		emit('broadcast_message', {'mensagem' : i.content, 'user' : i.user, "time" : i.timestamp})
	#old_room = data['rooml']

	#join_room(room)
	#if rooml is not None:
	#	leave_room(rooml)


@socketio.on('button_ask')
def butt():
	emit('button_functionality')

@socketio.on('heartbeat')
def heart():
	session['user'].last_beat = time.time()
	print(session["user"].name + " --  HeartBeat --" + str(session['user'].last_beat), file=sys.stderr)


@socketio.on("askRoomUsers")
def askRoomUsers(data):
	print("I am getting here", file=sys.stderr)
	room = data["room"]
	roomUsers = []
	for i in rooms:
		if i.name == room:
			roomUsers = i.users
			emit('roomUsers', {"roomUsers" : roomUsers})
			for s in roomUsers:
				print(s, file=sys.stderr)


if __name__ == "__main__":
	socketio.run(app, debug=True)
