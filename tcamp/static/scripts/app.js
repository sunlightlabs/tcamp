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

    // silly hamburger menu!
    // first, create a couple of containers for the content panel and drawer
    var menuPanel = $('<div class="menu-panel"></div>'),
        menuDrawer = $('<div class="menu-drawer"></div>'),
        // define an event handler to make sure we can't scroll sideways
        verticalScrollOnly = function(e){
          if($(window).width() > 768 ||
          (e.distX > e.distY && e.distX < -e.distY) ||
          (e.distX < e.distY && e.distX > -e.distY)) {
            e.preventDefault();
          }
        };
    // fill the drawer with the normal nav
    menuDrawer.append($('#menu').clone());
    // class the body to show the panel
    $('html').addClass('with-drawer-menu');
    // wrap the page with the panel
    $('body').children().wrapAll(menuPanel);
    // hide the drawer so it doesn't show while the page is continuing to load
    // show it a hacky 500 msecs later.
    menuDrawer.css('height', 0);
    setTimeout(function(){ menuDrawer.css('height', '100%'); }, 500);
    // add the drawer to the body
    $('body').append(menuDrawer);
    // override the bootstrap click behavior for parent nav items
    $('.menu-drawer a.dropdown-toggle').click(function(){
      window.location.href = $(this).attr('href');
    });
    // enforce scrolling to vertical-only
    $('.menu-drawer, .menu-panel').on('movestart', verticalScrollOnly);
    // bind some swipe handlers
    $('.menu-panel')
    // as we swipe, calculate the position and distance and move
    // the panel to the corresponding left coordinate on the screen
    .on('move', function(e){
      var el = $('.menu-panel'),
          menu = $('.menu-drawer'),
          bound = 80, // as a percent
          width = $(window).width();
      if(e.distX < 0){ // swipe left
        left = 50 * (e.pageX + e.distX) / width;
        el.css('left', Math.max(left, 0) + '%');
      }
      if(e.distX > 0){ // swipe right
        left = 100 * (e.distX) / width;
        el.css('left', Math.min(left, bound) + '%');
      }
    })
    // at the end of the swipe, check to see if we've moved far enough to snap open.
    // if not snap closed.
    .on('moveend', function(e){
      var el = $('.menu-panel'),
          menu = $('.menu-drawer'),
          width = $(window).width();
      if(el.offset().left + e.distX > width / 2){
        el.css('left', '80%');
        menu.css('z-index', 1);
      }else{
        el.css('left', '0');
        menu.css('z-index', 0);
      }
    });

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
    $(window).resize();
    // hack hack hack
    setTimeout(function(){ $(window).resize(); }, 250);
    // keep links clicked in web-app mode on the same page,
    // and write location to localstorage on background for persistence when reopening
    if(window.navigator.standalone){
      $('body').on('click', 'a', function(e){
        var el = $(e.target);
        if(el.attr('href') && !el.attr('href').match(/^http/)){
          e.preventDefault();
          // localStorage.setItem('webloc', el.attr('href'));
          location.href = el.attr('href');
        }
      });
    }
  });
})(this, jQuery);
