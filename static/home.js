document.addEventListener('DOMContentLoaded', ()=>{
	user = localStorage.getItem("user");
	if (user != "null" ){
		var form = document.querySelector("form");
		var input = document.querySelector("input");
		input.value = user;
		form.submit();

	}
});