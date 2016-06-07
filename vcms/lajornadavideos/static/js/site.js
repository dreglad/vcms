$(function() {
    /* inicializar búsqueda */
    new UISearch(document.getElementById('busqueda-form'));

    /* mouse over videos listas */
    var showDetails = function() {
        $(this).find('.detalle').slideDown('fast');
        return true;
    }, hideDetails = function() {
        $(this).find('.detalle').slideUp('slow');
        return true;
    };

    $('section figure').hover(showDetails, hideDetails)
    .on('touchstart', function() {
        if ($(this).hasClass('hover')) {
            return true;
        } else {
            showDetails.call(this);
            $(this).addClass('hover');
            hideDetails.call(
                $('section figure').not(this).removeClass('hover')
            );
            return true;
        }
    });
});