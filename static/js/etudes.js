// Overloading jQuery's "contains" selector to be case insensitive
jQuery.expr[':'].contains = function(a, i, m) {
  return jQuery(a).text().toUpperCase()
      .indexOf(m[3].toUpperCase()) >= 0;
};

function filterEtudes() {
    var activeDomains = $('.domain.active');
    var searchTerm = $('#recherche-etude').val();

    $('.etude').hide();

    // If all domains are unactive, we show all Etudes that match the current search term
    if (activeDomains.length == 0) {
        $('.etude:contains("' + searchTerm + '")').show();
        return;
    }

    // Otherwise we only show Etudes of the selected domains that match the current search term
    $('.etude').hide();
    $.each(activeDomains, function(i, d) {
        var domain = $(d).data('domain');
        $('.etude:contains("' + searchTerm + '") .domain:contains("' + domain + '")').closest('.etude').show();
    })
}

$(document).ready(function() {
    $('.etude').click(function(e) {
        $('.etude').removeClass('active');
        $etudeDetails = $(this).find('.details');

        var visible = $etudeDetails.is(':visible');
        $('.details').hide(500);
        $etudeDetails.stop();
        if (visible) {
            $etudeDetails.hide(500);
        }
        else {
            $(this).addClass('active');
            $etudeDetails.show(500);
        }

    })

    $('.domain').click(function(e) {
        // We toggle the state of the selected domain as active
        $(this).toggleClass('active');
        // We deselect any selected etude
        $('.etude').removeClass('active');
        $('.etude .details').hide(500);
        // We filter out shown etudes
        filterEtudes();
    });

    // Search input
    $('#recherche-etude').keyup(function() {
        filterEtudes();
    })
});
