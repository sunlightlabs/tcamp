(function(window, $, undefined){
  $('.overlay').click(function(e) {
    var outside_modal = !($(e.target).hasClass('inner') || $(e.target).parents('.inner').length > 0);
    var is_quit_button = $(e.target).hasClass('quit');
    var is_submit_button = $(e.target).attr('type') === 'submit';
    if (outside_modal || is_quit_button || is_submit_button) {
      removeModal();
    }
  });
  $(document).keyup(function(e) {
    if (e.keyCode == 27) {
      removeModal();
    }
  });
  var removeModal = function() {
    $('.overlay').remove();
  };
  var showModal = function() {
    $('.overlay').show();
  };
  if (document.cookie.indexOf('tcampmodal=true') === -1){
    //document.cookie='tcampmodal=true;path=/;'
    showModal();
  }
})(this, jQuery);
