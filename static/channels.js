var room_list = ['cracatua'];
var current_room = 'default';


	document.addEventListener('DOMContentLoaded', ()=>{
		var chatBox = document.querySelector('#ChatBox');
		var roomselect = document.querySelector('#room_selection');
		var socket=io.connect(location.protocol + '//' + document.domain + ':' + location.port);
		socket.on('connect', ()=>{

			socket.emit('ask_rooms');


			document.querySelector('#button').onclick = () =>{
				msg = document.querySelector('#input').value;
				x2 = nome_user;
				socket.emit('send_message', {'mensagem' : msg, 'user' : x2, 'current_room' : current_room});
				document.querySelector('#input').value = '';
				return false;
			};

			document.querySelector('#create_room form #create_room_button').onclick = () =>{
				room_name = document.querySelector('#create_room form #create_room_name').value;
				if (room_list.includes(room_name)){
					alert('error: Room already exists');
					return false;
				}
				else{
					rooml = current_room;
					current_room = room_name;
					socket.emit('create_room', {'room_name' : room_name, 'rooml' : rooml});
					document.querySelector('#create_room form #create_room_name').value = '';
					return false;
				}
			};
		});

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
									rooml = current_room;
									console.log('running3');
										socket.emit('join_room', {'room' : room, 'rooml' : rooml});
										current_room = room;
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
			h.innerHTML = data.user;
			msg.innerHTML = data.mensagem;
			div.appendChild(h);
			div.appendChild(msg);
			div.setAttribute("class", "msg_div");
			document.querySelector('#ChatBox').appendChild(div);
			chatBox.scrollTop = chatBox.scrollHeight;
		});
	});
