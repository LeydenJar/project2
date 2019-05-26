

#####Setting everything up, nothing special.

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

#This arrays are going to store the rooms and users, they are objects defined down here vvvv
rooms = []
users = []


"""
messages will be stored in the 'newRoom' type objects.
When they are spawned they do a check to see if the channel is storing more that 100 messages.
In this case, the oldest message is deleted.
"""
class new_Message(object):
	def __init__(self, user, content, timestamp, channel):
		self.user = user  
		self.content = content
		self.timestamp = timestamp
		self.channel = channel
		if len(channel.messages) == 100 or len(channel.messages) > 100:
			del channel.messages[0]
		channel.messages.append(self)


"""
The newRoom type objects are the Rooms of the chat.
This member_count property is going to be useful to delete rooms that are not being used.
When a user creates a room, he is taken off his previous room(If there is one).

The checkfordel function is going to be casted several times in the project.
It serves the purpose of checking if a room has users and delete it in the case it doesn't have any.
For the sake of simplicity, it also handles some of the processes of leaving a room, since it is aways casted in this ocasions anyway.
"""
class newRoom(object):
	def __init__(self, name, prev_Room, user1):
		self.name = name
		self.messages = []
		self.users = [user1]
		self.member_count = 1
		leave_room(prev_Room)
		if session['user'].current_room is not None:
			for i in rooms:
				if i.name == session["user"].current_room:
					i.users.remove(session["user"].name)
					i.member_count -= 1
					break
		join_room(name)
		session['user'].current_room = self
		rooms.append(self)

	def check_for_del(self):
		self.users.remove(session['user'].name)
		self.member_count -=1
		if self.member_count == 0:
			rooms.remove(self)
			emit("del_room", {"room" : self.name}, broadcast = True)
			del self


"""
The user is also quite simple.
This __eq__ function serves to compare 2 users and see if they are the same. It is a utility function.
"""
class new_User(object):
	def __init__(self, name, last_beat):
		self.name = name
		self.last_beat = last_beat
		self.current_room = None
		users.append(self)

	def __eq__(self, other):
		return self.name == other.name

	def logoutU(self):
		for i in users:
			if  self.__eq__(i):
				users.remove(i)
		session["user"] = None
		del self



"""
This one is interesthing.
In the current state, the system shold remove any user that leave the site, even if he dont click the logout button.
But anyhow, this function will clean any inactive users periodically.
Each ten minutes, users that are more than 10 minutes inactive will be removed.
I shold probably take this off... It is not necessary and cold potentially cause problems if the user change the javascript on his side.
I will let you have some fun with it. 
"""
def clean_users():
	print("starting the function clean_users", file=sys.stderr)
	now = time.time()
	for i in users:
		if now - i.last_beat > 600:
			print("removed " + i.name, file=sys.stderr)
			for n in rooms:
				if i.current_room.name == n.name:
					n.users.remove(i.name)
					n.member_count -=1
			session["user"] = None
			users.remove(i)
	threading.Timer(600, clean_users).start()
	print("Ending the function Clean_Users", file=sys.stderr)




def getlog(): #check if the user is logged in(possibly unnecessary in the current state of the system)
	try:
		u=None
		for i in users:
			if session["user"].__eq__(i):
				u = session["user"].name
	except:
		u = None
	return u

def check_avaliability(name): #This one checks the avaliability of an username
	a = True
	for i in users:
		if i.name == name:
			a = False
	return a
			



###############################################################Routes#########################################################################


"""The index will just redirect anyone who's already logged in to the channels page
As i sayd, this shold not happen since the user will be logged out once he leaves the page
Hey, it shold be useful if the user opens a new tab and try to log into the site...
Sooo, maybe the function getlog is not so obsolete hmff"""
@app.route("/")
def index():
	u = getlog()
	if u == None:
		return render_template('home.html')
	else:
		return redirect('/channels')



clean_users()#starting my possibly obsolete, possibly buggy function...


"""And here is our star!!
And the getlog function is beyng awesome again!"""
@app.route("/channels", methods=['POST', 'GET'])
def canais():
	if request.method=='GET': 
		u = getlog()
		if u == None:
			return redirect('/')           #you will not get here without making login
		else:
			return render_template('channels.html', x=u)
		
	else:
		candidate_to_user = request.form.get('user')
		avaliability = check_avaliability(candidate_to_user)    #and here it is....
		if avaliability == True:
			session['user'] = new_User(candidate_to_user, time.time())
			return render_template('channels.html', x=session['user'].name)
		else:
			return redirect('/')                              #if the user is already taken...
		



#######################################################Socket comunications############################################################



	
@socketio.on('ask_rooms')						 #this one is called when the user enters the channels page
def pass_rooms():
	r = []
	for i in rooms:
		r.append(i.name)
	emit('passing_rooms', {'rooms':r}) 			 #and here we return with a list of rooms that exist in the moment

@socketio.on('send_message')   					  #Well, I think you can guess this one...
def message(msg):
	mensagem = msg["mensagem"]
	user = msg["user"]
	room = session["user"].current_room
	time = strftime("%H:%M")
	m = new_Message(user, mensagem, time, room)  #creating the object, it will automatically append itself to the room messages list
	emit('broadcast_message', {'mensagem' : m.content, 'user' : m.user, "time" : m.timestamp}, room=m.channel.name)

@socketio.on('create_room')  					  #Quite descriptive
def create_room(data):
	room_name = str(data["room_name"])
	rooml = data['rooml']
	for i in rooms:
		if i.name == rooml:							#rooml means room to leave, it is the room that the user was before creating the room
			i.check_for_del()						#here is that function you've seen before, as you can see it helps a lot...
			break
	n = newRoom(room_name, rooml, session["user"].name)
	emit('broadcast_new_room', {'room_name' : room_name}, broadcast=True)



"""Allright, this one is probably the more complex one.
"""
@socketio.on('join_room')
def join(data):
	new_room = data['room']


	########here we check if the user has a room already and is trying to change the room.######
	########Then we store this information in this boolean called notnone.
	try:
		old_room = session["user"].current_room
	except:
		old_room = None
	notnone=old_room != None



	########If the user had a room before, we check to see if he is not trying to join the same room again
	########if he doesn't had a room, then he obviously is not....
	if notnone:
		notequal = old_room.name != new_room
	else:
		notequal = True


	#####in the case the room is the same, there is not reason to leave and join it again, so nothing happens
	#####if the user doesn't had a room before, there is no reason to leave the previous room(since it doesn't exist)
	if notequal and notnone:
		leave_room(old_room)
		for i in rooms:
			if i.name == session["user"].current_room.name:
				i.check_for_del()
				break

	if notequal:	
		for i in rooms:
			if i.name == new_room:
				if session["user"].name not in i.users:
					i.users.append(session["user"].name)
					i.member_count +=1
				session['user'].current_room = i
				join_room(new_room)
				break
		for i in session["user"].current_room.messages:
			emit('broadcast_message', {'mensagem' : i.content, 'user' : i.user, "time" : i.timestamp}) #after joining the room, we get the messages...





@socketio.on('button_ask') #this is called after the room buttons are created
def butt():
	emit('button_functionality') #this one activates the functionality of the buttons, so people can click it(or hover it)



@socketio.on('heartbeat') #this keeps the heart beats up-to-date, it helps the cleanUsers function, we've seen it on the beginning.
def heart():
	session['user'].last_beat = time.time()
	print(session["user"].name + " --  HeartBeat --" + str(session['user'].last_beat), file=sys.stderr)


@socketio.on("askRoomUsers") #this one sends the users in a specific room when someone hovers the mouse over its button
def askRoomUsers(data):
	room = data["room"]
	roomUsers = []
	for i in rooms:
		if i.name == room:
			roomUsers = i.users
			emit('roomUsers', {"roomUsers" : roomUsers})
			break


@socketio.on("logoff") #just a normal logoff...
def logoff(data):
	for i in rooms:
			if data["current_room"] == i.name:
				i.check_for_del()
	session['user'].logoutU()
	return redirect("/")



if __name__ == "__main__":
	socketio.run(app)
