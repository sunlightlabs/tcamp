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
      $(window).resize();
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

    // responsivize videos
    $('#content').fitVids();

    // hack twitter widgets with some custom css when the twttr global
    // becomes available
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

    // redraw social buttons bigger when window is resized
    // also, enable/disable panel menu
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
      if(width < 768){
        if(size == '16'){
          social.attr('data-options', opts.replace(rexp, 'size=24'));
          social.trigger('auto');
        }
      }else if(width >= 768){
        if(size == '24'){
          social.attr('data-options', opts.replace(rexp, 'size=16'));
          social.trigger('auto');
        }
      }
    }));

    // hack hack hack
    $(window).resize();
    setTimeout(function(){ $(window).resize(); }, 250);
    // keep links clicked in web-app mode on the same page,
    if(window.navigator.standalone){
      $('body').on('click', 'a', function(e){
        var el = $(e.target);
        if(el.attr('href') && !el.attr('href').match(/^http/)){
          e.preventDefault();
          location.href = el.attr('href');
        }
      });
    }
  });
})(this, jQuery);
