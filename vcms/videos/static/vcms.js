(function($) {
    $(function() {
    //     $('.info-descripcion .info-value').ellipsis({
    //       lines: '1',
    //       ellipClass: 'ellip',
    //       responsive: true
        // });
        $('#left-nav>ul>li:not(:first-child)').addClass('active');

        $('.breadcrumb li:contains("Gestor de video")').remove()


        if ($('#fieldset-video').is(':visible'))  {

            $(document).scroll(function() {
                 var current_scroll = $(document).scrollTop(),
                    breakpoint = $('#videobottom').offset().top,
                    player_elem = $('.jwplayer'),
                    is_piped = player_elem.hasClass('pip-on');

                if (!is_piped && current_scroll > breakpoint+30) {
                    player_elem.css('opacity', 0).addClass('pip-on');
                    jwplayer().setControls(false);
                    player_elem.fadeTo(800, 1);

                } else if (is_piped && current_scroll < breakpoint) {
                    player_elem.css('opacity', 0).removeClass('pip-on');
                    jwplayer().resize().setControls(true);
                    player_elem.fadeTo(400, 1);
                }
            });
        }
    });
})(jQuery)

function update_status(id, url) {
    $.getJSON(url, function(status) {
        console.log('a');
        if (status) {
            var row = $('tr[data-video=' + id + ']');

            row.find('.progress').removeClass('progress-success');
            row.find('.msg').addClass('hide').empty();
            //row.find('.field-video img').remove();

            if (status.progress) {
                row.find('.bar').css('width', (status['progress'] - 20) + '%');
                row.find('.progress').removeClass('hide');
            } else {
                row.find('.msg').removeClass('hide');
            }


            if (status.status == 'download') {
                row.find('.bar').html('Descargando video...');
                //row.find('.field-video').append('<img width="360" height="240" src="/static/vcms/img/generic-video.png">')
            } else if (status.status == 'valid') {
                row.find('.bar').html('Procesando video...');
                row.find('.progress').addClass('progress-success');
            } else if (status.status == 'queue') {
                row.find('.msg').html('<div class="alert alert-warn">El video está en cola para ser procesado.</div>');    
            } else if (status.status == 'error') {
                row.find('.msg').html('<div class="alert alert-error">Error. '+ status.msg +'</div>');
            } else if (status.status == 'done') {
                row.find('.msg').append('<div class="alert alert-success">El video se procesó correctamente.</div>');
                row.find('.progress').remove();
                location.reload();
            }
        }
    });
}
