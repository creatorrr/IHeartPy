$(function() {
	// Deck initialization
	$.deck('.slide');


});

function painter(event) {
	$('body').removeClass('dark');
	$('.instructions').removeClass('light');
	$('.instructions').html('Use <em><a onclick="prevSlide();">[&larr;]</a>&nbsp;<a onclick="nextSlide();">[&rarr;]</a></em> to navigate.');
	if(($.deck('getSlide').attr('id')=='heart')||($.deck('getSlide').attr('id')=='bye')){
		$('body').addClass('dark');
		$('.instructions').addClass('light');
		}
	if(($.deck('getSlide').attr('id')=='bye')){
		$('.instructions').html('<em>Hastalavista baby!</em>');
		}
		
}

function nextSlide() {
$.deck('next');
painter();
}

function prevSlide() {
$.deck('prev');
painter();
}
