(function(window, $, undefined){

  // == BRAINSTORM APP ==
  var drawVoteChart = function(el){
    el = $(el);
    var upvoteEl = el.find('.upvotes'),
        downvoteEl = el.find('.downvotes'),
        max = Math.max(window.maxVote, 20);
    upvoteEl.width((parseInt(upvoteEl.text(), 10) / max) * 100 + '%');
    downvoteEl.width((parseInt(downvoteEl.text(), 10) / max) * 100 + '%');
  };

  $(function(){
    // bind voting events
    $(window).bind('repaint.brainstorm', function(e, opts){
      drawVoteChart($(opts.elem));
    });
    $('.brainstorm-vote').each(function(){
      drawVoteChart(this);
    });

    // bind submit form toggle
    $('form.brainstorm legend').css({
      cursor: 'pointer'
    }).click(function(){
      var form = $(this).parents('form');
      form.toggleClass('open')
        .scrollTop(0);
      if(form.hasClass('open')){
        form.find('input#title').focus();
      }
    });
    // responsivize vidsnsuch
    $('#content').fitVids();

    // hack twitter widgets
    function checktwttr(){
      if(window.twttr){
        twttr.ready(function(T){
          $('iframe.twitter-timeline').each(function(){
            $(this.contentDocument.head).append('<style>\
              .timeline .stream { padding: 0 20px 0 10px; width: auto; }\
              .stream p.e-entry-title, .stream .profile, .var-chromeless .stream button.load-more { font-family: georgia, serif; font-weight: 300; }\
              .var-chromeless .stream button.load-more { font-size: 14px; }\
              .stream p.e-entry-title { color: #574227; }\
              .profile .p-name { color: #574227; }\
              .profile span.p-nickname { color: #736a5e; }\
              </style>');
          });
        });
      }else{
        setTimeout(checktwttr, 200);
      }
    }
    checktwttr();
    // silly hamburger menu
    jPM = $.jPanelMenu({
      duration: 50,
      closeOnContentClick: false
    });
    jPM.on();
    $('#jPanelMenu-menu a.dropdown-toggle').click(function(){
      window.location.href = $(this).attr('href');
    });
    $('.jPanelMenu-panel')
    .on('swiperight', function(e){
      if($(window).width() < 768){
        jPM.open();
      }
    })
    .on('swipeleft', function(e){
      if($(window).width() < 768){
        jPM.close();
      }
    })
    .on('movestart', function(e){
      if ((e.distX > e.distY && e.distX < -e.distY) ||
          (e.distX < e.distY && e.distX > -e.distY)) {
        e.preventDefault();
      }
    });
    // redraw social buttons bigger when window is resized
    $(window).resize($.throttle(150, function(){
      var social = $('.share-buttons'),
          opts = social.attr('data-options'),
          width = $(window).width(),
          rexp = /\bsize=([\d]+)\b/,
          size;
      try{
        size = social.attr('data-options').match(rexp)[1] || '16';
      }catch(e){
        size = '16';
      }
      if(width < 768 && size == '16'){
        social.attr('data-options', opts.replace(rexp, 'size=24'));
        social.trigger('auto');
      }else if(width >= 768 && size == '24'){
        social.attr('data-options', opts.replace(rexp, 'size=16'));
        social.trigger('auto');
      }
    }));
    $(window).resize();
    // hack hack hack
    setTimeout(function(){$(window).resize()}, 250);
  });


})(this, jQuery);
