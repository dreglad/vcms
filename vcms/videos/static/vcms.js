(function($) {
    $(function() {
        function qs(key) {
            key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
            var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
            return match && decodeURIComponent(match[1].replace(/\+/g, " "));
        }
    //     $('.info-descripcion .info-value').ellipsis({
    //       lines: '1',
    //       ellipClass: 'ellip',
    //       responsive: true
        // });

        // ..

        $('th.field-padded_pk a').on('click', function(ev) {
            if (qs('_popup').indexOf('http://') === 0) {
                ev.preventDefault();
                var id = parseInt($(this).parents('tr').attr('data-video')),
                    url = qs('_popup');
                $.ajax({
                    url: url,
                    data: { 'video_id': id }
                })
                window.close();
            }
        });

        $('span.help-inline:contains("Mantenga presionado")').hide();


        $('.field-plataformas select').attr(
            'data-placeholder', 'Disponible en todas las plataformas');
        $('.field-categoria select').attr(
            'data-placeholder', 'Sin categoría');
        $('#destacado_form .field-categoria select').attr(
            'data-placeholder', 'Página principal');

        $('.related-widget-wrapper-link.add-related').hide();
        $('.related-widget-wrapper-link.delete-related').hide();

        $('#Video_links-group .add-related').show();
        $('#Video_links-group .delete-related').show();


        $('#left-nav>ul>li:not(:first-child)').addClass('active');

        $('.breadcrumb li:contains("Gestor de video")').remove()

        if ($('#fieldset-video').is(':visible'))  {

            var playerInstance = jwplayer();
             playerInstance.on('ready',function() {
                    if (jwplayer().getRenderingMode() == "html5"){
                        videoTag = document.querySelector('video');
                         if(videoTag.playbackRate) {
                            playerInstance.addButton(
                                "icon_dir.png",
                                "0.25x",
                                function() {
                                  changeSpeed(0.25);
                                },
                                "0p25xslow"
                            );

                            playerInstance.addButton(
                                "icon_dir.png",
                                "0.5x",
                                function() {
                                  changeSpeed(0.5);
                                },
                                "0p5slow"
                            );

                            playerInstance.addButton(
                                "icon_dir.png",
                                "1x",
                                function() {
                                  changeSpeed(1);
                                },
                                "1xnormal"
                            );

                            playerInstance.addButton(
                                "icon_dir.png",
                                "1.5x",
                                function() {
                                  changeSpeed(1.5);
                                },
                                "1p5xforward"
                            );

                            playerInstance.addButton(
                                "icon_dir.png",
                                "2x",
                                function() {
                                  changeSpeed(2);
                                },
                                "2xforward"
                            );
                        }
                    }
                    else{
                        alert("your browser doesn't support HTML5，cant't change speed.");
                    }
                    console.log("state is :"+playerInstance.getState());
                });

             old_height = null;

             function pipOn() {
                var player_elem = $('.jwplayer');

                player_elem.css('opacity', 0).addClass('pip-on');
                jwplayer().setControls(false);
                player_elem.fadeTo(800, 1);
             }

             function pipOff() {
                var player_elem = $('.jwplayer');

                player_elem.css('opacity', 0).removeClass('pip-on');
                jwplayer().resize().setControls(true);
                player_elem.fadeTo(400, 1);
                // if (old_height) {
                //     player_elem.parent().css('height', old_height);
                //     old_height = 0;
                // }
             }

             $('#suit_form_tabs a').on('click', function() {
                // console.log('clicked');
                // pipOn();
                // var player_elem = $('.jwplayer');
                // if (!old_height) {
                //     old_height = player_elem.css('height')
                //     player_elem.parent().css('height', 0);
                // }
             })

            $(document).scroll(function() {
                 var current_scroll = $(document).scrollTop(),
                    breakpoint = $('#videobottom').offset().top,
                    player_elem = $('.jwplayer'),
                    is_piped = player_elem.hasClass('pip-on');

                if (!is_piped && current_scroll > breakpoint+30) {
                    pipOn();

                } else if (is_piped && current_scroll < breakpoint) {
                    pipOff();
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
                row.find('.bar').css('width', status['progress'] + '%');
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
