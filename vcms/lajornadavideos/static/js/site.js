$(function() {
    /* inicializar búsqueda */

    // $('section.videos ol').each(function() {
    //     var lista = $(this);
    //     lista.imagesLoaded().always(function() {
    //         console.log(lista);
    //         lista.masonry({
    //             itemSelector: 'li',
    //             columnWidth: '.grid-sizer',
    //             percentPosition: true,
    //             transitionDuration: 0
    //         });
    //     });
    // });

    $.endlessPaginate({
        onCompleted: function(data) {
            console.log(data);
            var listas = $('section.videos.' + data.key + ' ol').masonry({
              itemSelector: 'li:not(.gid-sizer)',
              columnWidth: '.grid-sizer',
              percentPosition: true,
              transitionDuration: 0
          });

            listas.imagesLoaded().progress(function() {
              listas.masonry('layout');
            });
            listas.masonry('layout');

            bindsection();
        }
    });

    var listas = $('section.videos ol').masonry({
        itemSelector: 'li:not(.gid-sizer)',
        columnWidth: '.grid-sizer',
        percentPosition: true,
        transitionDuration: 0
    });

    listas.imagesLoaded().progress(function() {
      listas.masonry('layout');
    });

    function bindsection() {
        /* mouse over videos listas */
        var showDetails = function() {
            $(this).find('.detalle').slideDown('fast');
            return true;
        };
        var hideDetails = function() {
            $(this).find('.detalle').slideUp('slow');
            return true;
        };

        $('section figure').hover(showDetails, hideDetails).on('touchstart', function() {
            if ($(this).hasClass('hover')) {
                return true;
            } else {
                showDetails.call(this);
                $(this).addClass('hover');
                hideDetails.call($('section figure').not(this)
                                                    .removeClass('hover'));
                return true;
            }
        });
    }

    bindsection();
    

    new UISearch(document.getElementById('busqueda-form'));
});