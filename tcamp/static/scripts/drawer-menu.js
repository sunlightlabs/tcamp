/**
 * Drawer menu js
 * draggable panel for mobile that reveals a menu underneath
 */

(function($){
  // define some utility functions to prevent click bleed-through on the menu trigger
  function freezeLinks(el){
    $(el).find('a').bind('click.drawer-menu', function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
    });
  }
  function unfreezeLinks(el){
    setTimeout(function(){
      $(el).find('a').unbind('click.drawer-menu');
    }, 10);
  }

  // init menu on domready
  $(function(){
    (function(opts){
      // first, create a couple of containers for the content panel and drawer
      var menuPanel = $('<div class="' + opts.panel.replace('.', '') + '"></div>'),
          menuDrawer = $('<div class="' + opts.drawer.replace('.', '') + '"></div>'),
          // define an event handler to make sure we can't scroll sideways
          verticalScrollOnly = function(e){
            if($(window).width() > opts.phoneWidth ||
                (e.distX > e.distY && e.distX < -e.distY) ||
                (e.distX < e.distY && e.distX > -e.distY)) {
              // allows scroll to happen
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
      // and then show it a hacky 500 msecs later.
      menuDrawer.css('height', 0);
      setTimeout(function(){ menuDrawer.css('height', '100%'); }, 500);
      // add the drawer to the body
      $('body').append(menuDrawer);
      // override the bootstrap default click behavior for parent nav items
      $(opts.drawer + ' a.dropdown-toggle').click(function(){
        window.location.href = $(this).attr('href');
      });

      // capturing the move event prevents scrolling on touch devices.
      // whenever we dip below the threshold dimensions, bind our movestart to
      // skip the move event bindings entirely if we're scrolling more vertically
      // than horizontally.
      // resize() is triggered on domready in app.js, so there's no need to do it here.
      $(window).resize($.throttle(150, function(){
        if($(window).width() < opts.phoneWidth && (! $('body').attr('data-swipe-menu-enabled'))){
          $(opts.drawer + ', ' + opts.panel).on('movestart.drawer-menu', verticalScrollOnly);
          bindSwipeHandlers();
        }else if($(window).width() >= opts.phoneWidth && $('body').attr('data-swipe-menu-enabled')){
          $(opts.drawer + ', ' + opts.panel).off('movestart.drawer-menu');
          unbindSwipeHandlers();
        }
      }));

      function bindSwipeHandlers(){
        $('body').attr('data-swipe-menu-enabled', true);
        $(opts.panel)
        // as we swipe, calculate the position and distance and move
        // the panel to the corresponding left coordinate on the screen
        .on('move.drawer-menu', function(e){
          e.preventDefault();
          if($(window).width() < opts.phoneWidth){
            e.stopPropagation();
            var el = $(opts.panel),
                menu = $(opts.drawer),
                width = $(window).width();
            el.addClass('moving');
            if(e.distX < 0){ // swiping left
              left = 50 * (e.pageX + e.distX) / width;
              el.css('left', Math.max(left, 0) + '%');
            }
            if(e.distX > 0){ // swiping right
              left = 100 * (e.distX) / width;
              el.css('left', Math.min(left, opts.bound) + '%');
            }
          }
        })
        // at the end of the swipe, check to see if we've moved far enough
        // to snap open. if not, snap closed.
        .on('moveend.drawer-menu', function(e){
          e.preventDefault();
          if($(window).width() < opts.phoneWidth){
            e.stopPropagation();
            var el = $(opts.panel),
                menu = $(opts.drawer),
                width = $(window).width();
            el.removeClass('moving');
            if(el.offset().left + e.distX > width / 2){
              el.css('left', opts.bound + '%');
              menu.css('z-index', 1);
              unfreezeLinks(opts.drawer);
            }else{
              el.css('left', '0');
              menu.css('z-index', 0);
              freezeLinks(opts.drawer);
            }
          }
        });
        // also, toggle the menu on clicks of the menu-trigger element.
        $(opts.trigger).on('click.drawer-menu', function(e){
          e.preventDefault();
          e.stopPropagation();
          $(opts.panel).css('left',
            $(opts.panel).offset().left === 0 ? opts.bound + '%' : '0');
        });
      }
      function unbindSwipeHandlers(){
        $('body').attr('data-swipe-menu-enabled', false);
        $(opts.panel)
        .off('move.drawermenu')
        .off('moveend.drawer-menu')
        .off('click.drawermenu');
      }

    })({  // immediately execute this closure, and pass in some options:
      phoneWidth: 768,
      bound: 80, // as a percent
      trigger: '.menu-trigger',
      panel: '.menu-panel',
      drawer: '.menu-drawer',
      sourceMenu: '#menu'
    });

    // default state is for links in drawer menu to be no-ops
    freezeLinks('.menu-drawer');
  });
})(jQuery);
