(function($){
    /**
    * jQuery.deparam
    * reverses jQuery's param() method, converting a querystring back to an object
    */
    $.deparam = function(qs) {
        var params, pieces;
        params = {};
        if (!qs) {
            return params;
        }
        pieces = qs.split(/[&=]/);
        $.each(pieces, function(idx, val) {
            if (idx % 2) {
                params[pieces[idx - 1]] = val;
            }
        });
        return params;
    };
    // Ajax table loader
    var refreshInterval = $.deparam(location.search).refresh || 300000; // default to 5 minutes
    function ajaxRefresh(interval){
        setTimeout(function(){
            $('#table_wrap').load(location.href + ' #table_display', function(text, status, xhr){
                if(status == 'success' || status == 'notmodified'){
                    $('body').removeClass('reconnecting');
                }else{
                    $('body').addClass('reconnecting');
                }
                ajaxRefresh(interval);
            });
        }, interval);
    }
    // Domready bootstrap
    $(function(){
        ajaxRefresh(refreshInterval);
    });
})(jQuery);