$(function() {
	// Deck initialization
	$.deck('.slide');


});

function painter(event) {
	$('body').removeClass('dark');
	$('.instructions').removeClass('light');
<<<<<<< HEAD
	$('.instructions').html('Use <em>[&larr;]&nbsp;[&rarr;]</em> to navigate.');
=======
	$('.instructions').html('Use <em><a onclick="prevSlide();">[&larr;]</a>&nbsp;<a onclick="nextSlide();">[&rarr;]</a></em> to navigate.');
>>>>>>> master
	if(($.deck('getSlide').attr('id')=='heart')||($.deck('getSlide').attr('id')=='bye')){
		$('body').addClass('dark');
		$('.instructions').addClass('light');
		}
	if(($.deck('getSlide').attr('id')=='bye')){
		$('.instructions').html('<em>Hastalavista baby!</em>');
		}
		
}
<<<<<<< HEAD
=======

function nextSlide() {
$.deck('next');
painter();
}

function prevSlide() {
$.deck('prev');
painter();
}
>>>>>>> master
