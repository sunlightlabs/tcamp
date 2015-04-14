(function(window, $, undefined){
  // various ways to minimize modal
  $('.overlay .quit').click(function() {
    removeModal();
  })
  $('.overlay').click(function(e) {
    if (!$(e.target).hasClass('inner')) {
      removeModal()
    }
  })
  $(document).keyup(function(e) {
    if (e.keyCode == 27) {
      removeModal();
    }
  });
  
  var removeModal = function() {
    $('.overlay').remove()
  }
})(this, jQuery);
