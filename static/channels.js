/*
Those are utility variables.
tema is portuguese for theme. I used it because I had used theme already.
Espero que estejam gostando dos comentários
(I hope you are enjoying the comments)
*/

var room_list = [];
var current_room = localStorage.getItem("current_room");
var tema = "light";

	
	

	document.addEventListener('DOMContentLoaded', ()=>{
		//setting everything up.. more utility variables
		var chatBox = document.querySelector('#ChatBox');
		var roomselect = document.querySelector('#room_selection');
		var socket=io.connect(location.protocol + '//' + document.domain + ':' + location.port);
		var message_counter = 0; //this one is to erease the messages when needed, without having to comunicate with the server.



		socket.on('connect', ()=>{

			//Here we just ask the rooms...
			socket.emit('ask_rooms');

			/*And we try to join our previous room.
				It will not happen if you've clicked the logoff button the last time you visited the site, in this case current_room will be null
				But it will work if you just closed your browser. In this case, you have to logon again.
				You can choose a new name, or the same if it's still avaliable, but the room will be remembered anyway.
				I think it is better this way, because it makes the names avaliable when someone leaves without forgetting the room that the person was.
				(2 users cant have the same name in this project)
			*/
			if (current_room != null){
				socket.emit('join_room', {"room" : current_room});
			}


			//this part introduces the enter functionality, if you press enter, the message will be sent. 
			document.querySelector("#input").onkeypress = (e) =>{
			 if (e.keyCode !== 13) {
      		  document.querySelector("#input").value += (e.key);
 			   }
 			 else{
 			 	msg = document.querySelector('#input').value;
				x2 = nome_user;
				socket.emit('send_message', {'mensagem' : msg, 'user' : x2, 'current_room' : localStorage.getItem("current_room")});
				document.querySelector('#input').value = '';
 			 }
				return false;
			};
			//Of course, you can always send the message via the 'Enviar' button(witch means send in portuguese, I will just let it this way)
			document.querySelector('#button').onclick = () =>{
				msg = document.querySelector('#input').value;
				x2 = nome_user;
				socket.emit('send_message', {'mensagem' : msg, 'user' : x2, 'current_room' :  localStorage.getItem("current_room")});
				document.querySelector('#input').value = '';
				return false;
			};

			/*
			This part handles a bit of the room creation.
			To make things easyer, you cant create a room with more that 15 characters.
			You can't have 2 rooms with the same name also...
			If is everything ok, the javascript shold delete the messages of your current room and procede with the creation of the new one

			*/

			document.querySelector('#create_room form #create_room_button').onclick = () =>{
				room_name = document.querySelector('#create_room form #create_room_name').value;
				if (room_name.length > 15){
					alert("room names must have 15 or less chars");
					return false

				}
				if (room_list.includes(room_name)){
					alert('error: Room already exists');
					return false;
				}
				else{
					rooml = localStorage.getItem("current_room");
					var node = document.querySelector("#ChatBox");
						while(node.firstChild){
							node.removeChild(node.firstChild);
							if (message_counter !== 0){
								message_counter --;
								}
							}


					socket.emit('create_room', {'room_name' : room_name, 'rooml' : rooml});
					msg = "Genesis of the room " + room_name;
					user = "system";
					socket.emit('send_message', {"mensagem" : msg, "user" : user, "current_room" : room_name});
					localStorage.setItem("current_room", room_name);
					document.querySelector('#create_room form #create_room_name').value = '';
					return false;
				}
			};
		});

	

			//Here is the heart
			setInterval(function(){
			socket.emit("heartbeat")
		},10000);


			//Here we ask for the rooms that currently exist
			//Then we create the buttons for every room
			//In the end we ask the server to emit the button_functionality signal that is below.
		socket.on('passing_rooms', data=>{
			var i;
			for (i=0; i<data.rooms.length; i++){
				room_name = data.rooms[i];
				room_list.push(room_name);
				const button = document.createElement('button');
				button.innerHTML = data.rooms[i];
				button.setAttribute("class", "room_button btn btn-light");
				button.setAttribute("type", "submit");
				document.querySelector('#room_selection').appendChild(button);
			}
			socket.emit('button_ask')

		});


		/*
		This one makes the buttons clickable.
		It also makes a list of the users in certain room appear in the bottom right of the screen when you hover the mouse over its button
		*/
		socket.on('button_functionality', ()=>{
			if (document.querySelectorAll('.room_button').length > 0){
						document.querySelectorAll('.room_button').forEach(function(button){
								button.onclick = ()=>{
									room = button.innerHTML;
									rooml = localStorage.getItem("current_room");

										//Here we remove the messages in the current/old room
										var node = document.querySelector("#ChatBox");
										while(node.firstChild){
											node.removeChild(node.firstChild);
											if (message_counter !== 0){
												message_counter --;
											}
										}

										//Here we actually ask the server to put us in the new room
										socket.emit('join_room', {'room' : room, 'rooml' : rooml});
										localStorage.setItem("current_room", room);

										//Here we send a message to the new room, it's a cute little message
										msg = "Batman has joined the room!";
										user = "system";
										socket.emit('send_message', {"mensagem" : msg, "user" : user, "current_room" : room});
										return false;
					}


								button.onmouseenter = ()=>{
									//Here we make that list appear
									room = button.innerHTML;
									const userlistContainer = document.createElement("div");
									userlistContainer.setAttribute("class", "userlistContainer");
									var usernames = document.createElement("p");
									socket.emit('askRoomUsers', {"room" : room});
									socket.on('roomUsers', data=>{
										var i = 0;
										while (data.roomUsers[i]){
											usernames.innerHTML +=  data.roomUsers[i] + "<br>";
											i++;
										}
									});


									userlistContainer.appendChild(usernames);
									document.querySelector('body').appendChild(userlistContainer);
									return false;
								}

								button.onmouseleave = () =>{
									//And here we make it disappear
									var list = document.querySelector(".userlistContainer");
									while(list.firstChild){
										list.removeChild(list.firstChild);
									}
									list.parentNode.removeChild(list);
									return false;
								}
				});
			}});


//In this one, we make a new room button(this happensa when a room is created)
		socket.on('broadcast_new_room', data => {
			room_name = data.room_name;
			room_list.push(room_name);
			const button = document.createElement('button');
			button.innerHTML = data.room_name;
			classe = "room_button btn btn-" + tema;
			button.setAttribute("class", classe);
			document.querySelector('#room_selection').appendChild(button);
			roomselect.scrollTop = roomselect.scrollHeight;
			socket.emit('button_ask'); //And we ask for the functionality again
		});


//Here we make a new message appear, if we have a lot of messages, we are going to delete the oldest ones
		socket.on('broadcast_message', data =>{
			if(message_counter == 100){
				var element = document.querySelector(".msg_div");
				element.parentNode.removeChild(element);
				message_counter --;
			}
			const div = document.createElement('div');
			const h = document.createElement('h4');
			const line = document.createElement('br');
			const msg = document.createElement("p");
			const timediv = document.createElement("div");
			const time = document.createElement("p");
			h.innerHTML = data.user;
			msg.innerHTML = data.mensagem;
			time.innerHTML = data.time;
			timediv.setAttribute("class", "timestamp");
			timediv.appendChild(time);
			div.appendChild(h);
			div.appendChild(msg);
			div.appendChild(timediv);
			div.setAttribute("class", "msg_div");
			document.querySelector('#ChatBox').appendChild(div);
			message_counter ++;
			chatBox.scrollTop = chatBox.scrollHeight;
		});


//This one makes sure that the user will make logout even if he doesn't click the logout button.
//This way the username become avaliable to other people to use
//It does not interfere with the ability of the system to remember the room that the user was.
		document.querySelector("body").onbeforeunload = function (){
			current_room = localStorage.getItem("current_room");
			socket.emit("logoff", {"current_room" : current_room});
			return false;
		}

//If you press the button, the current_room item in the localStorage will be set to null, so the system won't remember your last room.
		document.querySelector("#logout").onclick = function(){
			current_room = localStorage.getItem("current_room");
			socket.emit("logoff", {"current_room" : current_room});
			window.location.href = 'http://127.0.0.1:5000/';
			localStorage.setItem("current_room", null);
			return false;
		}
		

//This one handles room deletion, it finds the right room and removes it
		socket.on("del_room", data=>{
			var rtd = data.room;
			var buttons = document.getElementsByClassName("room_button");
			var n = buttons.length
			for (var i=0; i < n; i++){
				if (buttons[i].innerHTML == rtd){
					buttons[i].parentNode.removeChild(buttons[i]);
					break;
				}
			}
			index = room_list.indexOf(rtd);
			room_list.splice(index);
		});


//And here we handle the theme selection stuff. In my oppinion, the dark theme is awesome. 

		document.querySelectorAll(".theme").forEach(function(button){
			button.onclick = ()=>{
				var theme = button.innerHTML;
				var body = document.querySelector("body");
				var chat = document.querySelector("#ChatBox");
				var room_select = document.querySelector("#room_selection");
				var theme_div = document.querySelector("#theme_selection");
				var room_buttons = document.querySelectorAll(".room_button");



				if (theme == "Dark"){
					tema = "dark";
					body.style.backgroundColor = "Black";
					chat.style.backgroundColor = "#660066";
					room_select.style.backgroundColor = "#660066";
					theme_div.style.backgroundColor = "#660066";
					room_buttons.forEach(function(botao){
						botao.setAttribute("class", "room_button btn btn-dark");

					});
				}
				
					
				else if( theme == "Light"){
					tema = "light";
					body.style.backgroundColor = "#8080ff";
					chat.style.backgroundColor = "#ccccff";
					room_select.style.backgroundColor = "#ccccff";
					theme_div.style.backgroundColor = "#ccccff";
					room_buttons.forEach(function(botao){
						botao.setAttribute("class", "room_button btn btn-light");

					});
				}
				else if (theme == "Summer"){
					tema = "warning";
					body.style.backgroundColor = "#fc7136";
					chat.style.backgroundColor = "#fda781";
					room_select.style.backgroundColor = "#fda781";
					theme_div.style.backgroundColor = "#fda781";
					room_buttons.forEach(function(botao){
						botao.setAttribute("class", "room_button btn btn-warning");

					});
				}}});
	});
