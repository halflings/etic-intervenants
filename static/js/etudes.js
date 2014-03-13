$(document).ready(function() {

    $('.etude').click(function(e) {
        $('.etude').removeClass('active');

        $eDetails = $(this).find('.details');


        var visible = $eDetails.is(':visible');
        $('.details').hide(500);
        $eDetails.stop();
        if (visible) {
            $eDetails.hide(500);
        }
        else {
            $(this).addClass('active');
            $eDetails.show(500);
        }

    })

    $('.domains li').click(function(e) {
        var domain = $(this).data('domain');
        $('.etude').hide();
        $('.etude .domain:contains("' + domain + '")').closest('.etude').show();
    });
});
