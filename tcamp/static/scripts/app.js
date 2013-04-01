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
  });


})(this, jQuery);