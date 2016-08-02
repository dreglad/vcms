$(function() {
    /* inicializar búsqueda */

    $("img.lazy").lazyload({
        threshold: 250
    });

    var listas = $('section.videos ol').masonry({
        itemSelector: 'li:not(.grid-sizer)',
        columnWidth: '.grid-sizer',
        percentPosition: true,
        // gutter: 3,
        transitionDuration: 0
    });

    listas.imagesLoaded().progress(function() {
      listas.masonry('layout');
    });

    // $('section.videos ol').each(function() {
    //     var lista = $(this);
    //     lista.imagesLoaded().progress(function() {
    //         lista.masonry('layout');
    //         // lista.masonry({
    //         //     //itemSelector: 'li',
    //         //     itemSelector: 'li:not(.grid-sizer)',
    //         //     columnWidth: '.grid-sizer', 
    //         //     percentPosition: true,
    //         //     // gutter: 3,
    //         //     transitionDuration: 0
    //         // });
    //     });
    // });

    $.endlessPaginate({
        onCLick: function(a) {
        },

        onCompleted: function(data) {
            var listas = $('section.videos.' + data.key + ' ol').masonry({
              itemSelector: 'li:not(.grid-sizer)',
              columnWidth: '.grid-sizer',
              percentPosition: true,
              // gutter: 3,
              transitionDuration: 0
            });

            listas.imagesLoaded().progress(function() {
              listas.masonry('layout');
            });

            // $('section.videos.' + data.key).each(function() {
            //     if ($(this).prev().hasClass('noinvertido')) {
            //         $(this).find('article').addClass('noinvertido');
            //     }
            //     if ($(this).prev().hasClass('invertido')) {
            //         $(this).find('article').addClass('invertido');
            //     }
            //     if ($(this).prev().hasClass('junto')) {
            //         $(this).find('article').addClass('junto');
            //     }
            // });

            // $('section.videos.' + data.key + ' img.lazy').lazyload({})
            bindsection();
        }
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

        $('section.noinvertido figure').hover(showDetails, hideDetails).on('touchstart', function() {
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

    if ($('nav').length > 0) {
        new UISearch(document.getElementById('busqueda-form'));
    }
});