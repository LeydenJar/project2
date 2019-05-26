# Flack

This is a simple 2 pages site.
It is a chat application.

the more interesting stuff is on the channels.js and the application.py files, they are both nicely commented.

The application.py handles all back-end processes.
The channels.js takes care of the fron-end.

The system relies on information that is mantained serverside, the python file keeps the rooms and users stored in arrays and use them when needed.
The messages are keeped in arrays inside of the room objects.

The js will frequently request information from the server to make its activities.

###################################################################################################################################################

The users can send messages either clicking the Enviar button or pressing enter. The message will be sended to the server, stored and broadcasted.
In this process the server will also check if the channel that the message was sent do does not have more that 100 messages. If it has the oldest one will be deleted so it is not passed when the next user enters the room.
The JS also has a message counter that keeps ereasing old messages when you have 100 or more in your chat box.

Everyone can create a join rooms freely. It's quite intuitive.




The localStorage is used to remember rooms and names, it works like this:

If you make logout by clicking the logout button, the site wont remember neyther your name or your room.

If you just close the browser, both will be remembered.
	The name will be avaliable for others to pick when you leave. When you come back, if no one has taken it, you will be automatically logged in.
	The room is remembered regardeless of the name. If your previous room still exists when you come back, you are going to be connected.
		rooms are automatically deleted if there is no members connected.



######################### As a personal touch, I've workeded in the front end. ####################### 

The channels page now has 3 different themes, they make the site more aesthetically pleasing.

I also added the ability for the user to see who is in a certain room, by hovering the mouse on to the room button, it will spawn a div in the right botton of the screen.