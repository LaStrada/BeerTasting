$('#star input:radio').addClass('input_hidden');
$('#star span').click(function(){
	$('#star span').removeClass('glyphicon-star');
	$('#star span').addClass('glyphicon-star-empty');
	
	$(this).removeClass('glyphicon-star-empty');
	$(this).addClass('glyphicon-star');
	
});