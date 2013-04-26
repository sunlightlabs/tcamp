/**
 * Drawer menu js
 * draggable panel for mobile that reveals a menu underneath
 */

// define some utility functions to prevent click bleed-through on the menu trigger
(function($){
  function freezeLinks(el){
    $(el).find('a').bind('click.freezelinks', function(e){
      e.preventDefault();
      e.stopPropagation();
    });
  }
  function unfreezeLinks(el){
    setTimeout(function(){
      $(el).find('a').unbind('click.freezelinks');
    }, 10);
  }
  // init menu on domready
  $(function(){
    (function(opts){
      // silly hamburger menu!
      // first, create a couple of containers for the content panel and drawer
      var menuPanel = $('<div class="' + opts.panel.replace('.', '') + '"></div>'),
          menuDrawer = $('<div class="' + opts.drawer.replace('.', '') + '"></div>'),
          // define an event handler to make sure we can't scroll sideways
          verticalScrollOnly = function(e){
            if($(window).width() > opts.phoneWidth ||
            (e.distX > e.distY && e.distX < -e.distY) ||
            (e.distX < e.distY && e.distX > -e.distY)) {
              e.preventDefault();
            }
          };
      // fill the drawer with the normal nav
      menuDrawer.append($(opts.sourceMenu).clone());
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
      $(opts.drawer + ' a.dropdown-toggle').click(function(){
        window.location.href = $(this).attr('href');
      });
      // enforce scrolling to vertical-only
      $(opts.drawer + ', ' + opts.panel).on('movestart', verticalScrollOnly);
      // now bind some swipe handlers
      $(opts.panel)
      // as we swipe, calculate the position and distance and move
      // the panel to the corresponding left coordinate on the screen
      .on('move', function(e){
        e.stopPropagation();
        var el = $(opts.panel),
            menu = $(opts.drawer),
            width = $(window).width();
        if(e.distX < 0){ // swipe left
          left = 50 * (e.pageX + e.distX) / width;
          el.css('left', Math.max(left, 0) + '%');
        }
        if(e.distX > 0){ // swipe right
          left = 100 * (e.distX) / width;
          el.css('left', Math.min(left, opts.bound) + '%');
        }
      })
      // at the end of the swipe, check to see if we've moved far enough to snap open.
      // if not snap closed.
      .on('moveend', function(e){
        e.preventDefault();
        e.stopPropagation();
        var el = $(opts.panel),
            menu = $(opts.drawer),
            width = $(window).width();
        if(el.offset().left + e.distX > width / 2){
          el.css('left', opts.bound + '%');
          menu.css('z-index', 1);
          unfreezeLinks(opts.drawer);
        }else{
          el.css('left', '0');
          menu.css('z-index', 0);
          freezeLinks(opts.drawer);
        }
      });
      // toggle on clicks of the menu-trigger
      $(opts.trigger)
      .click(function(e){
        e.preventDefault();
        e.stopPropagation();
        $(opts.panel).css('left',
          $(opts.panel).offset().left === 0 ? '80%' : '0');
      });
    })({
      phoneWidth: 768,
      bound: 80, // as a percent
      trigger: '.menu-trigger',
      panel: '.menu-panel',
      drawer: '.menu-drawer',
      sourceMenu: '#menu'
    });

    // default state is for links in drawer menu to be noops
    freezeLinks('.menu-drawer');
  });
})(jQuery);
