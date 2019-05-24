var room_list = ['cracatua'];
var current_room = localStorage.getItem("current_room");


	
	

	document.addEventListener('DOMContentLoaded', ()=>{
		var chatBox = document.querySelector('#ChatBox');
		var roomselect = document.querySelector('#room_selection');
		var socket=io.connect(location.protocol + '//' + document.domain + ':' + location.port);
		var message_counter = 0;
		socket.on('connect', ()=>{


		
			socket.emit('ask_rooms');


			console.log(localStorage.getItem("current_room"));


			document.querySelector("#input").onkeypress = (e) =>{
			 if (e.keyCode !== 13) {
      		  document.querySelector("#input").value += (e.key);
 			   }
 			 else{
 			 	msg = document.querySelector('#input').value;
				x2 = nome_user;
				//time = now.getHours() +":"+ now.getMinutes()
				socket.emit('send_message', {'mensagem' : msg, 'user' : x2, 'current_room' : localStorage.getItem("current_room")});
				document.querySelector('#input').value = '';
 			 }
				return false;
			};

			document.querySelector('#button').onclick = () =>{
				msg = document.querySelector('#input').value;
				x2 = nome_user;
				//time = now.getHours() +":"+ now.getMinutes()
				socket.emit('send_message', {'mensagem' : msg, 'user' : x2, 'current_room' :  localStorage.getItem("current_room")});
				document.querySelector('#input').value = '';
				return false;
			};

			//**************************************************************************************//

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
					//localStorage.setItem() = room_name;

					var node = document.querySelector("#ChatBox");
						while(node.firstChild){
							node.removeChild(node.firstChild);
							if (message_counter !== 0){
								message_counter --;
								}
							console.log(message_counter);
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

			
			setInterval(function(){
			socket.emit("heartbeat")
		},10000);

		socket.on('passing_rooms', data=>{
			var i;
			for (i=0; i<data.rooms.length; i++){
				room_name = data.rooms[i];
				room_list.push(room_name);
				const button = document.createElement('button');
				button.innerHTML = data.rooms[i];
				button.setAttribute("class", "room_button");
				button.setAttribute("type", "submit");
				document.querySelector('#room_selection').appendChild(button);
				socket.emit('button_ask')
			}

		});

		socket.on('button_functionality', ()=>{
			if (document.querySelectorAll('.room_button').length > 0){
						document.querySelectorAll('.room_button').forEach(function(button){
								button.onclick = ()=>{
									room = button.innerHTML;
									rooml = localStorage.getItem("current_room");
										var node = document.querySelector("#ChatBox");
										while(node.firstChild){
											node.removeChild(node.firstChild);
											if (message_counter !== 0){
												message_counter --;
											}
											console.log(message_counter);
										}
										socket.emit('join_room', {'room' : room, 'rooml' : rooml});
										localStorage.setItem("current_room", room);
										msg = "Batman has joined the room!";
										user = "system";
										socket.emit('send_message', {"mensagem" : msg, "user" : user, "current_room" : room});
										//current_room = room;
										return false;
					}
								button.onmouseenter = ()=>{
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
									var list = document.querySelector(".userlistContainer");
									while(list.firstChild){
										list.removeChild(list.firstChild);
									}
									list.parentNode.removeChild(list);
									return false;


								}
				});
			}});

		socket.on('broadcast_new_room', data => {
			room_name = data.room_name;
			room_list.push(room_name);
			const button = document.createElement('button');
			button.innerHTML = data.room_name;
			button.setAttribute("class", "room_button")
			document.querySelector('#room_selection').appendChild(button);
			roomselect.scrollTop = roomselect.scrollHeight;
			socket.emit('button_ask');
		});

		socket.on('broadcast_message', data =>{
			if(message_counter == 100){
				console.log("running inside");
				var element = document.querySelector(".msg_div");
				element.parentNode.removeChild(element);
				message_counter --;
			}
			console.log("running outside");
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


		document.querySelector("body").onbeforeunload = function (){
			current_room = localStorage.getItem("current_room");
			socket.emit("logoff", {"current_room" : current_room});
			window.location.href = 'http://127.0.0.1:5000/';
			return false;
		}
		document.querySelector("#logout").onclick = function(){
			current_room = localStorage.getItem("current_room");
			socket.emit("logoff", {"current_room" : current_room});
			window.location.href = 'http://127.0.0.1:5000/';
			return false;
		}
		
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
			
	});
