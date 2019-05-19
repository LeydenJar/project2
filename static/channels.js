var room_list = ['cracatua'];
var current_room = localStorage.getItem("current_room");


	
	

	document.addEventListener('DOMContentLoaded', ()=>{
		var chatBox = document.querySelector('#ChatBox');
		var roomselect = document.querySelector('#room_selection');
		var socket=io.connect(location.protocol + '//' + document.domain + ':' + location.port);
		socket.on('connect', ()=>{


		
			socket.emit('ask_rooms');


			console.log(localStorage.getItem("current_room"));
/*			if(localStorage.getItem("current_room") !== null){
				console.log("running this");
				var abcde = "qualquer coisa";
				var abcd = localStorage.getItem("current_room");
				socket.emit("join_room", {"room" : abcd, "rooml" : abcde});

			}
*/

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
				if (room_list.includes(room_name)){
					alert('error: Room already exists');
					return false;
				}
				else{
					rooml = localStorage.getItem("current_room");
					//localStorage.setItem() = room_name;
					socket.emit('create_room', {'room_name' : room_name, 'rooml' : rooml});
					msg = "You've created the room " + room_name;
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
			console.log('running0');
			if (document.querySelectorAll('.room_button').length > 0){
						console.log('running');
						document.querySelectorAll('.room_button').forEach(function(button){
							console.log('running2');
								button.onclick = ()=>{
									room = button.innerHTML;
									rooml = localStorage.getItem("current_room");
									console.log('running3');
										socket.emit('join_room', {'room' : room, 'rooml' : rooml});
										localStorage.setItem("current_room", room);
										msg = "Welcome to the room " + room;
										user = "system";
										socket.emit('send_message', {"mensagem" : msg, "user" : user, "current_room" : room});
										//current_room = room;
										return false;
					}
				})
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
			chatBox.scrollTop = chatBox.scrollHeight;
		});

	
		/*document.querySelector('#ChatBox').onbeforeunload = função(){
				alert("works");
			};*/
	});
