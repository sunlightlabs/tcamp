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
              .timeline .stream { padding: 0 20px 0 10px; width: auto !important; }\
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
      var social = $('.share-buttons').filter(':visible'),
          opts = social.attr('data-options'),
          topts = social.attr('data-twitter-options'),
          fopts = social.attr('data-facebook-options'),
          width = $(window).width(),
          rexp = /\bshow-counts=(true|false)\b/;
      if(width < 1200){
        console.log('small');
        // too small, no counts
        if(topts.match(rexp)[1] == 'true'){
          social.attr('data-twitter-options', topts.replace(rexp, 'show-counts=false'));
          social.attr('data-facebook-options', fopts.replace(rexp, 'show-counts=false'));
          social.trigger('auto');
        }
      }else if(width >= 1200){
        console.log('big');
        if(topts.match(rexp)[1] == 'false'){
          social.attr('data-twitter-options', topts.replace(rexp, 'show-counts=true'));
          social.attr('data-facebook-options', fopts.replace(rexp, 'show-counts=true'));
          social.trigger('auto');
        }
      }
    }));

    // character counting on submit form
    $('.form-paper').find('input[type=text], textarea').keyup(function(e){
      var charlimit = parseInt($(this).attr('data-limit'), 10),
          value = $(this).val();
          if(! isNaN(charlimit)){
            if(value.length < charlimit) $(this).removeClass('full');
            else if(value.length == charlimit) $(this).addClass('full');
            else $(this).val(value.slice(0, charlimit)) && $(this).addClass('full');
          }
    });

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
