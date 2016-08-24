$(document).ready(function() {
	$('#nav').affix({
      offset: {
        top: $('header').height() - $('header div.fixed').height()
      }
	});
	$('#subnav').affix({
      offset: {
        top: $('header').height() - $('header div.fixed').height()
      }
	});
  $('header div.fixed').affix({
      offset: {
        top: 0
      }
  });
});

// function to set the height on fly
 function autoHeight() {
   $('#content').css('min-height', 0);
   $('#content').css('min-height', (
     $(document).height() 
     - $('header').height() 
     - $('nav').height()
     - $('footer').height()
   ));
 }

 // onDocumentReady function bind
 $(document).ready(function() {
   autoHeight();
 });

 // onResize bind of the function
 $(window).resize(function() {
   autoHeight();
 });