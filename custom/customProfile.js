$(document).ready(function(){
	var message = {'success': null};
	$("button#submitusername").on("click", function() {
		var bla = $('#username').val();
		$.post("/profile/update", JSON.stringify({'username': bla}), function(returnedData) {
			$('#flash').append(flashMessage(JSON.parse(returnedData)));
		});
	});
});
