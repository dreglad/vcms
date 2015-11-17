(function() {

    idioma = 'es';

    var SERVER_URL = '/';
    var CAPTURA_API = SERVER_URL + 'ops/',
        MULTIMEDIA_API = SERVER_URL + 'api/v1/',
        USER_INFO_URL = SERVER_URL + 'admin/user_info',
        SITE_NAME = 'Globovisión',
        LOGIN_URL = '/admin/login/?next=' + top.window.location.href + top.window.location.hash;

    /* * * * * *  VARIABLES  * * * * */
    var api_url = MULTIMEDIA_API,
        page_size = 10,
        templates = ['./templates/menuItem.html', './templates/editForm.html',
                     './templates/programaRow.html', './templates/mediaRow.html',
                     './templates/modals.html', './templates/clipStatus.html',
                     './templates/homeRow.html'],
        // initial state
        tipo_slug = '', tipo_nombre_plural = 'Todos los videos',
        // required API resources
        resources = ['tipo_clip', 'categoria', 'pais', 'corresponsal', 'programa', 'tema'],
        // custom resources
        custom_resources = {},
        // custom_resources = {
        //     tipo_clip: {
        //         es: [
        //             { slug: 'videolibro', nombre_plural: "Videolibros", nombre: "Videolibro" },
        //             { slug: 'independiente', nombre_plural: "Independientes", nombre: "Independiente" }
        //         ]
        //     }
        // },
        icons = {
            noticia: 'notebook', entrevista: 'users', programa: 'layers',
            reportaje: 'chemistry', documental: 'folder', 'especial-web': 'globe'
        },
        // internal state
        current_params = {}, current_offset = 0,
        resources_data = {}, current_label = '', global_random=null,
        user = null;

    /* * * * * *  LIST EVENT HANDLERS  * * * * */

    // navegación principal (tipos)
    $('#menu_tipos').on('click', 'a', function(ev) {
        ev.preventDefault();
        go('list-view');

        // update state
        tipo_slug = $(this).attr('data-tipo');
        tipo_nombre_plural = $(this).attr('title');
        current_label = '';
        current_offset = 0;

        // select first menu item
        $('div.modos a:first').trigger('click');
    });

    $('.nav').on('click', 'a', function(ev) {
        $('.nav li').removeClass("active");
        $(this).parents('li').addClass("active");
    });


    // mostrar más
    $('button[data-action=mostrar-mas]').click(function(ev) {
        // update UI
        $('#cargando').show();
        $(this).css({opacity: '0.3'});

        // update state
        current_offset += page_size;

        // load content
        populateMediaList({params: current_params});
    });


    // navegación secundaria (modos)
    $('div.modos').on('click', 'a', function(ev) {
        ev.preventDefault();

        var el = $(this), params = {}, label = "";
        current_offset = 0;

        if (el.attr('data-modo') == 'dropdown')
            return;

        // ajustar estado de menú modos
        $(".modos a.selected").removeClass('selected');
        $(".modos button.selected").removeClass('selected');
        // para poner el estado activo cuando es submenú en caso de BOTONES
        var padreul = el.parents("ul[class='dropdown-menu']");
        if (padreul.prev("button").length > 0) {
            padreul.prev("button").addClass('selected');
        }
        el.addClass('selected').siblings().removeClass('selected');

        // Elegir parámetro adecuados
        switch (el.attr('data-modo')) {
            case "publicados":
               params = {publicado: true};
               label = __("Publicados");
                break;
            case "despublicados":
                params = {publicado: false};
                label = __("Despublicados");
                break;
            case "seleccion":
                params = {seleccionado: true};
                label = __("Selección del Editor");
                break;
            case "secciones":
                params = {categoria: el.attr('data-valor')};
                label = el.html();
                break;
            case "programas":
                params = {programa: el.attr('data-valor')};
                label = el.html();
                break;
            case "corresponsales":
                params = {corresponsal: el.attr('data-valor')};
                label = __("Corresponsales");
                break;
            case "temas":
                params = {tema: el.attr('data-valor')};
                label = __("Temas");
                break;
            case "cronologia":
                params = {tiempo: el.attr('data-valor')};
                label = el.html();
                break;
            case "populares":
                params = {orden: "popularidad"};
                label = __("Populares")
                break;
        }

        // update UI
        $('ul.media-list').empty();
        $('[data-action=mostrar-mas]').css({opacity: 0});
        current_label = " &raquo; " + label;

        // load content
        populateMediaList({params: params});
    });

    // modal linkembed
    $('#modallinkembed').on('show.bs.modal', function(ev) {
        var clip = $(ev.relatedTarget).parents('.media-row').data('clip');
        $(this).find('.modal-body').empty().mustache('modal-linksembed', { clip: clip });
        $('input.linksembed, textarea.linksembed').focus(function() {
            var $this = $(this);
            $this.select();
            // Work around Chrome's little problem
            $this.mouseup(function() {
                $this.unbind("mouseup");
                return false;
            });
        }).first().focus();
    })


    // auto-thumbnail clip
    $(document).on('click', '.boton-acciones a.autothumbnail', function(ev) {
        ev.preventDefault();
        var row = $(this).parents('.media-row');
        var clip = row.data('clip');

        row.css('opacity', 0.5);

        $.ajax({
            url: CAPTURA_API + 'cambiar_thumbnail/',
            dataType: 'json',
            type: 'POST',
            data: {
                usuario_remoto: user.email,
                key: user.password,
                slug: clip.slug,
                id: clip.id
            }
        }).retry({times:3}).done(function(data) {
            $.ajax({
                url: api_url + 'clip/'+ clip.id +'/?nc=' + Math.random(),
                cache: false,
                data: { detalle: 'completo', autenticado: true },
                dataType: 'json'
            }).done(function(data) {
                updateMediaRow(data);
                row.css('opacity', 1);
            });
        }).fail(function() {
            row.css('opacity', 1);
            bootbox.alert(__("Error cambiando thumbnail de clip, verifique que aún tiene conexión a Internet e intente de nuevo."));
        });
    });


    // eliminar clip
    $(document).on('click', '.boton-acciones a.eliminar', function(ev) {
        ev.preventDefault();
        var row = $(this).parents('.media-row');
        var clip = row.data('clip');

        row.css('background', '#e3e3e3');

        bootbox.confirm(__('Confirme que desea eliminar este clip'), function(result) {
            if (result) {
                $.ajax({
                    url: CAPTURA_API + 'eliminar/',
                    dataType: 'json',
                    type: 'POST',
                    data: {
                        usuario_remoto: user.email,
                        key: user.password,
                        slug: clip.slug,
                        id: clip.id
                    }
                }).retry({times:3}).done(function(data) {
                    row.slideUp();
                }).fail(function() {
                    bootbox.alert(__("Error eliminando clip, verifique que aún tiene conexión a Internet e intente de nuevo."))
                });
            }
            row.css('background', '');
        });
    });


    // despublicar clip
    $(document).on('click', '.boton-acciones a.despublicar', function(ev) {
        ev.preventDefault();
        var row = $(this).parents('.media-row');
        var clip = row.data('clip');

        row.css('background', '#e3e3e3');

        bootbox.confirm(__('Confirme que desea despublicar este clip'), function(result) {
            if (result) {
                $.ajax({
                    url: CAPTURA_API + 'despublicar/',
                    dataType: 'json',
                    type: 'POST',
                    data: {
                        usuario_remoto: user.email,
                        key: user.password,
                        slug: clip.slug,
                        id: clip.id
                    }
                }).retry({times:3}).done(function(data) {
                    row.slideUp();
                }).fail(function() {
                    bootbox.alert(__("Error despublicando clip, verifique que aún tiene conexión a Internet e intente de nuevo."));
                });
            }
            row.css('background', '');
        });
    });

    // publicar clip
    $(document).on('click', '.boton-acciones a.publicar', function(ev) {
        ev.preventDefault();
        var row = $(this).parents('.media-row');
        var clip = row.data('clip');

        row.css('background', '#e3e3e3');

        bootbox.confirm(__('Confirme que desea publicar este clip'), function(result) {
            if (result) {
                $.ajax({
                    url: CAPTURA_API + 'publicar/',
                    dataType: 'json',
                    type: 'POST',
                    data: {
                        usuario_remoto: user.email,
                        key: user.password,
                        slug: clip.slug,
                        id: clip.id
                    }
                }).done(function(data) {
                    row.slideUp();
                }).fail(function() {
                    bootbox.alert(__("Error publicando clip, verifique que aún tiene conexión a Internet e intente de nuevo."));
                });
            }
            row.css('background', '');
        });
    });


    // edit clip
    $('#list-view, #edit-view').on('click', 'a.edit', function(ev) {
        ev.preventDefault();
        var clip = $(this).parents('.media-row').data('clip');

        go('edit-view', {clip: clip});
    });


    // edit programa
    $('#programas-view').on('click', '[data-action=programa-edit]', function(ev) {
        ev.preventDefault();
        var programa = $(this).parents('li').data('programa');

        go('programa-edit-view', {programa: programa});
    });


    // add new clip
    $('#menu_nuevo').on('click', 'a.clip', function(ev) {
        ev.preventDefault();

        go('edit-view', {clip: null });
    });


    //Buscar
    $('#form-search').on('submit', function(e) {
        e.preventDefault();

        var q = $('#input-search').val();
        $('ul.media-list').empty();
        $('div.content-heading h2').html(__('Búsqueda') + ': ' + q);
        $('#input-search').val('');

        // load content
        populateMediaList({ params: { texto: q } });
    });


    // Programas
    $('#menu_settings').on('click', 'a.programas', function(ev) {
        var programa_list = $('ul.programa-list').empty();

        $.each(resources_data.programa, function(i, programa) {
            $('<li class="programa-row">').mustache('programa-row', {programa: programa})
            .appendTo(programa_list).data('programa', programa);
        });

        go('programas-view');
        $('div.content-heading h2').html(__('Programas'));
    });


    var initHomeRow = function(homeRow) {
        var setting = homeRow.data('setting');

        // seleccionar filtros
        _.each(setting.filters, function(value, key) {
            homeRow.find('div.filterSelect select[name='+key+']').val(value);
        });

        // chosen
        homeRow.find('.chosen-select').chosen({no_results_text: "No hay resultados!"});

        // crear campos para IDs y llenarlos
        if (homeRow.hasClass('primary')) var num = 2;
        else if (homeRow.hasClass('secondary')) var num = 4;
        else var num = 3;

        homeRow.find('div.ids input').remove();
        for (var i=0; i<num; i++) {
            var val = setting.ids[i] || "";
            $('<input type="text" class="form-control small" />').val(val).appendTo(homeRow.find('div.ids'));
        }

        // seleccionar modo
        homeRow.find('select.mode option[value="'+setting.mode+'"]').attr('selected', true)
        .trigger('change');
    };

    var doSortable = function() {
        $('.sortable').sortable({
            forcePlaceholderSize: true,
            placeholder: '<div class="box-placeholder p0 m0"><div></div></div>',
            items: "li.top"
        });
    };

    // Contenido de home
    $('#menu_settings').on('click', 'a.home', function(ev) {
        var home_list = $('ul.home-list').empty();

        var settings = _.object(_.map(resources_data.setting, function(setting) {
            return [ setting.key, JSON.parse(setting.value) ];
        }))['videosite_'+idioma];

        if (!settings) { // No settings
            settings = { primary_clips: {}, secondary_clips: {}, tops: []}
        }

        // headers (primary/secondary)
        $('<li class="home-row primary">').mustache('home-row', {setting: settings.primary_clips, isTop: false, top: 'primary', resources_data: resources_data})
            .appendTo(home_list).data('setting', settings.primary_clips);

        $('<li class="home-row secondary">').mustache('home-row', {setting: settings.secondary_clips, isTop: false, top: 'secondary', resources_data: resources_data})
            .appendTo(home_list).data('setting', settings.secondary_clips);

        // tops
        $.each(settings.tops, function(i, setting) {
            $('<li class="home-row top">')
            .mustache('home-row', {setting: setting, isTop: true, top: i, resources_data: resources_data})
            .data('setting', setting)
            .appendTo(home_list);
        });

        // inicializar
        $('li.home-row').each(function() {
            initHomeRow($(this));
        })

        // sortable
        doSortable();

        go('home-view');
        $('div.content-heading h2').html(__('Home de Sitio de Videos'));
    });

    /* * * * * *  HOME EVENT HANDLERS  * * * * */  
    $('#home-view').on('change', 'select.mode',  function(ev) {
        var homeRow = $(ev.target).parents('.home-row'),
            helpText = homeRow.find('.helpText');

        switch ($(ev.target).val()) {
            case 'ids':
                helpText.text(__('Especifique los IDs de los videos que desea mostrar'));
                homeRow.find('div.filterSelect').hide();
                homeRow.find('div.filterText').hide();
                homeRow.find('div.ids').show();
                homeRow.find('div.filterSearch').hide();
                homeRow.find('div.filterId').hide();
                break;
            case 'filter':
                helpText.text(__('Especifique los criterios de filtrado que desea aplicar'));
                homeRow.find('div.filterSelect').show();
                //homeRow.find('div.filterText').show();
                homeRow.find('div.filterText').hide(); // Hide filterText
                homeRow.find('div.ids').hide();
                homeRow.find('div.filterSearch').hide();
                homeRow.find('div.filterId').hide();
                break;
            case 'busqueda':
                helpText.text(__('Se mostrarán los resultados de la última búsqueda que realizó el usuario'));
                homeRow.find('div.filterSelect').hide();
                homeRow.find('div.filterText').hide();
                homeRow.find('div.ids').hide();
                homeRow.find('div.filterSearch').hide();
                homeRow.find('div.filterId').hide();
                break;
            case 'history':
                helpText.text(__('Se mostrarán los últimos videos vistos por el usuario'));
                homeRow.find('div.filterSelect').hide();
                homeRow.find('div.filterText').hide();
                homeRow.find('div.ids').hide();
                homeRow.find('div.filterSearch').hide();
                homeRow.find('div.filterId').hide();
                break;
            case 'customSearch':
                helpText.text(__('Especifique una búsqueda de texto. Adicionalmente puede filtrar el resultado'));
                homeRow.find('div.filterSelect').show();
                homeRow.find('div.filterText').hide();
                homeRow.find('div.ids').hide();
                homeRow.find('div.filterSearch').show();
                homeRow.find('div.filterId').hide();
                break;
            case 'related':
                helpText.text(__('Especifique un clip para mostrar sus videos relacionados.'));
                homeRow.find('div.filterSelect').hide();
                homeRow.find('div.filterText').hide();
                homeRow.find('div.ids').hide();
                homeRow.find('div.filterSearch').hide();
                break;
        }
    });

    $('#home-view').on('click', 'button.add',  function(ev) {
        var setting = {
            mode: 'ids',
            ids: [],
            filters: []
        }, 
        homeRow = $('<li class="home-row top">')
            .mustache('home-row', {setting: setting, isTop: true, resources_data: resources_data})
            .data('setting', setting)
            .appendTo($('.home-list'));

        initHomeRow(homeRow);
        doSortable();
    });

    $('#home-view').on('click', 'a.delete',  function(ev) {
        ev.preventDefault();
        var home_li = $(this).parents("li.home-row");
        bootbox.confirm(__('Confirme que desea borrar esta fila'), function(result) {
            if (result) {
                home_li.fadeOut();
                home_li.remove();
            }
        });
    });
    $('#home-view')
        .on('mouseenter', 'a.delete',  function() {
        var home_li = $(this).parents("li.home-row");
        home_li.css({'background-color':'#f5f5f5','border':'2px dashed #bcbdbf'});
        })
        .on('mouseleave', 'a.delete',  function() {
        var home_li = $(this).parents("li.home-row");
            home_li.css({'background-color':'#fff','border':'none','border-bottom':'1px solid #e1e1e8'});
    });

    $('#home-view').on('click', 'button.cancel',  function(ev) {
        $('#menu_settings a.home').click().trigger('click');
    });

    var getSettingJson = function(elem) {
        var json = {
            mode: elem.find('select.mode').val(), 
            filters: {},
            ids: []
        };
        if (elem.find('input.title').length) {
            json.title = elem.find('input.title').val().trim();
        }
        elem.find('.filterSelect select,.filterText input').each(function() {
            if ($(this).val()) {
                json.filters[$(this).attr('name')] = $(this).val();
            }
        });

        // IDs
        elem.find('.ids input').each(function() {
            if ($(this).val()) {
                json.ids.push($(this).val().trim());
            }
        });

        console.log(json);

        return json;
    };
    $('#home-view').on('click', 'button.save',  function(ev) {
        // fabricar estructura
        var prim = getSettingJson($('#home-view li.home-row.primary'));
        var sec = getSettingJson($('#home-view li.home-row.secondary'));
        var tops = []
        $('#home-view li.home-row.top').each(function() {
            tops.push(getSettingJson($(this)));
        })
        
        var json = {
            primary_clips: prim,
            secondary_clips: sec,
            tops: tops
        }

        $.ajax({
            url: CAPTURA_API + 'editar_settings/',
            dataType: 'json',
            type: 'POST',
            data: {
                usuario_remoto: user.email,
                key: user.password,
                idioma: idioma,
                settings: JSON.stringify(json)
            }
        }).retry({times:3}).done(function(data) {
            loadResources(function() {
                bootbox.alert(__('Configuración de Home actualiada'));
                $('#menu_settings a.home').trigger('click');
            }, ['setting']);
        }).fail(function() {
            bootbox.alert(__('Error al guardar datos en el servidor'))
        });
        console.log(json);
    });


    /* * * * * *  EDIT EVENT HANDLERS  * * * * */

    $('#edit-view').on('click', 'a.sel_veneuela', function(ev) {
        ev.preventDefault();
        $('#pais').val('VE');
    });


    // CANCEL clip edit
    $('#edit-view').on('click', 'button.cancel', function(ev) {
        go('list-view');
    });


    // CANCEL programa edit
    $('#programa-edit-view').on('click', 'button.cancel', function(ev) {
        go('programas-view');
    });


    // SAVE EDIT clip
    $('#edit-view').on('click', 'button.save', function(ev) {
        // Validate Form
        if (!$('#titulo').val().trim()) {
            bootbox.alert(__('Por favor introduzca un título'));
            $('#titulo').focus();
            return;
        } else if ($('#titulo').val().trim().length < 4) {
            bootbox.alert(__('Por favor introduzca un título más largo'));
            $('#titulo').focus();
            return;
        } else if (!$('#tipo').val()) {
            bootbox.alert(__('Por favor especifique el tipo de clip'));
            $('#tipo').focus();
            return;
        } else if ($('#tipo').val() == 'programa' && !$('#programa').val()) {
            bootbox.alert(__('Un clip de tipo programa debe especificar el programa de origen'));
            $('#programa').focus();
            return;
        }

        // disable button
        var el = $(this), section_params = el.parents('section').data('params');
        el.attr('disabled', 'disabled');

        var clip = section_params.clip;
        if (clip) {
            // EXISTING clip, editing..
            $.ajax({
                url: CAPTURA_API + 'editar/',
                dataType: 'json',
                type: 'POST',
                data: {
                    usuario_remoto: user.email,
                    key: user.password,
                    slug: clip.slug,
                    id: clip.id,
                    archivo_img_id: $('#upload_img_id').val(),
                    titulo: $('#titulo').val().trim(),
                    programa: $('#programa').val(),
                    categoria: $('#categoria').val(),
                    tipo: $('#tipo').val(),
                    descripcion: $('#descripcion').val().trim(),
                    hashtags: $('#hashtags').val().trim(),
                    corresponsal: $('#corresponsal').val(),
                    tema: $('#tema').val(),
                    // ciudad: $('#ciudad').val(),
                    pais: $('#pais').val(),
                    // idioma: idioma,
                    seleccionado: $('#seleccionado').is(':checked') ? $('#seleccionado').val() : '',
                    publicado: $('#publicado').is(':checked') ? $('#publicado').val() : ''
                }
            }).retry({times:3}).done(function(data) {
                // Succesfully edited clip, now update Media List
                var li = $('ul.media-list li.clip-' + clip.id);
                li.css('opacity', 0.5);
                $.ajax({
                    url: api_url + 'clip/' + clip.id + '/?nc=' + Math.random(),
                    cache: false,
                    data: { detalle: 'completo', autenticado: true },
                    dataType: 'json'
                }).done(function(data) {
                    if (clip.tipo.slug == data.tipo.slug &&
                        (clip.publicado == data.publicado || !('publicado' in current_params))) {
                        // clip still belongs to media list, just update
                        updateMediaRow(data);
                    } else {
                        // This clip no longer belongs to media list, remove
                        var li = $('ul.media-list li.clip-' + clip.id);
                        li.slideUp();
                    }
                });
                go('list-view');
            }).fail(function() {
                bootbox.alert(__("Error guardando la información. Verifique que aún tenga conexión a Internet e intente de nuevo"));
                el.removeAttr('disabled');
            });
        } else {
            // NEW CLIP, creating...
            var origen = $('#origen').val(), origen_url;
            if (origen == 'upload') {
                origen_url = $('#upload_clip_id').val();
            } else if (origen == 'url') {
                origen_url = $('#origen_url').val();
            }
            $.ajax({
                url: CAPTURA_API + 'crear/',
                dataType: 'json',
                type: 'POST',
                data: {
                    usuario_remoto: user.email,
                    key: user.password,
                    origen: origen,
                    url: origen_url,
                    titulo: $('#titulo').val().trim(),
                    programa: $('#programa').val(),
                    categoria: $('#categoria').val(),
                    tipo: $('#tipo').val(),
                    descripcion: $('#descripcion').val().trim(),
                    hashtags: $('#hashtags').val().trim(),
                    corresponsal: $('#corresponsal').val(),
                    tema: $('#tema').val(),
                    seleccionado: $('#seleccionado').is(':checked') ? $('#seleccionado').val() : '',
                    pais: $('#pais').val(),
                    publicado: $('#publicado').attr('checked') ? 1 : 0
                }
            }).done(function(data) {
                bootbox.alert('<p style="min-height: 100px;" id="status_label"></p>');
                $('#status_label').empty().mustache('status-progress', { progress: 0, status: __("Iniciando...")});

                go('list-view');

                var check_status = function() {
                    if ($("#status_label").length == 0) return; // modal still opened?
                    $.ajax({
                        url: CAPTURA_API + 'query_nuevo/',
                        data: { uid: data.uid },
                        dataType: 'json'
                    }).done(function(result) {
                        switch (result.status) {
                            case 'queue':
                                $('#status_label').empty().mustache('status-progress', { progress: 0, status: __("En cola...")});
                                break;
                            case 'download':
                                // downloading file
                                $('#status_label').empty().mustache('status-progress', {
                                    progress: Math.round(Math.min(99, Math.max(1, result.progress))/5),
                                    status: __("Obteniendo video...")
                                });
                                break;
                            case 'valid':
                                // download done, compressing
                                var status = result.progress < 98 ? __('Procesando video...') : __("Finalizando...");
                                $('#status_label').empty().mustache('status-progress', {
                                    progress: 20 + Math.round((Math.min(99, Math.max(1, result.progress))/2)),
                                    status: status
                                });
                                break;
                            case 'invalid':
                                // download done but invalid video file
                                $('#status_label').empty().mustache('status-progress', { status: __("Archivo de video inválido.")});
                                return;
                            case 'done':
                                // done
                                $('#status_label').empty().mustache('status-progress', { progress: 100, status: __("Verificando...")});
                                var wait_for_clip = function() {
                                    if ($("#status_label").length == 0) return; // modal still opened?
                                    $.ajax({
                                        url: api_url + 'clip/' + result.id + '/?nc=' + Math.random(),
                                        data: { detalle: 'completo', autenticado: 'admin20' },
                                        dataType: 'json'
                                    }).done(function(clip) {
                                        // clip ready
                                        $('#status_label').empty().mustache('status-progress', { progress: 100, status: __("Completado")});
                                        go('edit-view', {clip: clip});
                                        bootbox.hideAll();
                                    }).fail(function() {
                                        // clip not ready
                                        setTimeout(wait_for_clip, 300);
                                    });
                                }
                                wait_for_clip();
                                return;
                        }
                        setTimeout(check_status, 300);
                    }).fail(function() {
                        setTimeout(check_status, 300);
                    });
                }
                check_status();
            }).fail(function() {
               bootbox.alert(__("Error guardando la información. Verifique que aún tenga conexión a Internet e intente de nuevo"));
                el.removeAttr('disabled');
            });
        }
    });


    // SAVE EDIT programa
    $('#programa-edit-view').on('click', 'button.save', function(ev) {
        // disable button
        var el = $(this);
        el.attr('disabled', 'disabled');
        var programa = el.parents('section').data('params').programa;

        var params = {};
        if (programa.mismo_idioma) {
            // MISMO IDIOMA
            params = {
                usuario_remoto: user.email,
                key: user.password,
                id: programa.id,
                upload_banner_id: $('#upload_banner_id').val(),
                horario: $('#horario').val().trim(),
                twitter: $('#twitter').val().trim(),
                twitter_widget: $('#twitter_widget').val().trim(),
                descripcion: $('#descripcion').val().trim(),
                idioma: idioma,
                conductor1: $('#conductor1').val().trim(),
                conductor1_twitter: $('#conductor1_twitter').val().trim(),
                conductor1_twitter_widget: $('#conductor1_twitter_widget').val().trim(),
                conductor2: $('#conductor2').val().trim(),
                conductor2_twitter: $('#conductor2_twitter').val().trim(),
                conductor2_twitter_widget: $('#conductor2_twitter_widget').val().trim(),
                conductor3: $('#conductor3').val().trim(),
                conductor3_twitter: $('#conductor3_twitter').val().trim(),
                conductor3_twitter_widget: $('#conductor3_twitter_widget').val().trim()
            }
        } else {
            // IDIOMA DIFERENTE
            params = {
                usuario_remoto: user.email,
                key: user.password,
                id: programa.id,
                idioma: idioma,
                descripcion: $('#descripcion').val().trim(),
                horario: $('#horario').val().trim(),
            }
        }

        $.ajax({
            url: CAPTURA_API + 'editar_programa/',
            dataType: 'json',
            type: 'POST',
            data: params
        }).retry({times:3}).done(function(data) {
            loadResources(function() {
                $('#menu_settings a.programas').trigger('click');
            }, ['programa']);
        }).fail(function() {
            bootbox.alert(__("Error guardando la información. Verifique que aún tenga conexión a Internet e intente de nuevo"));
            el.removeAttr('disabled');
        });
    });



    /* * * * * *  FUNCTIONS  * * * * */

    var go = function(view, params) {
        if (top.window.location.hash) {
            top.window.location.hash = '';
        }
        $('section.view').hide();
        $('section#'+view).data('params', params).show();
        window.scrollTo(0, 0);

        if (params) {
            switch (view) {
                case 'programa-edit-view':
                    $('#programa-form').empty().mustache('programa-edit-form', {
                        programa: params.programa,
                        resources_data: resources_data
                    });
                    var uploader = OMUpload.setup({
                        element: document.getElementById('uploader_banner'),
                        autoUpload: true,
                        multiple: false,
                        text: { uploadButton: __('Elegir archivo...') },
                        callbacks: {
                            onUpload: function() {
                                $('#programa-form button.save').attr('disabled', 'disabled');
                                $('.qq-upload-button').empty();
                                //$('.editar_form .archivo_status').empty().removeClass('success').removeClass('error');
                            },

                            onCancel: function() {
                                $('#programa-form button.save').removeAttr('disabled');
                            },

                            onComplete: function(id, fileName, responseJSON){
                                $('#programa-form button.save').removeAttr('disabled');

                                if (responseJSON.error) {
                                    //$('.qq-upload-button').show();
                                    //alert(responseJSON.error);
                                    //$('.nuevo_form .archivo_status').html("<h5>ERROR: "+responseJSON.error).addClass('error').removeClass('success');
                                    bootbox.alert(__("Error al subir archivo, por favor intente de nuevo"));
                                    $('.qq-upload-fail').empty();
                                }
                                if (responseJSON.id) {
                                    $('#upload_banner_id').val(responseJSON.id);
                                    $('#upload_banner_status').html('<h4><em class="icon-check"></em> ' + __('Archivo subido correctamente.') +'</h4>').addClass('success').removeClass('error');
                                    $('#uploader_banner').hide();
                                }
                            }
                        }
                    });
                    break;

                case 'edit-view':
                    $('#edit-form').empty().mustache('clip-edit-form', {
                        clip: params.clip,
                        resources_data: resources_data
                    })

                    if (params.clip) {
                        top.window.location.hash = params.clip.id;
                        $('.editar-label').html(params.clip.titulo + ' <em><small>(video ID: ' + params.clip.id + ')</small></em>')
                    } else {
                        top.window.location.hash = 'nuevo';
                        $('.editar-label').html(__('Cargar nuevo video'));
                    }

                    // boton acciones en edit-form
                    //.data('clip', params.clip).find('.boton-acciones').empty()
                    //.mustache('boton-acciones', { clip: params.clip });

                    if (params.clip) {
                        // editing existing clip, select current dropdowns
                        if (params.clip.tipo) $('#tipo').val(params.clip.tipo.slug);
                        if (params.clip.categoria) $('#categoria').val(params.clip.categoria.slug);
                        if (params.clip.programa) $('#programa').val(params.clip.programa.slug);
                        if (params.clip.corresponsal) $('#corresponsal').val(params.clip.corresponsal.slug);
                        if (params.clip.tema) $('#tema').val(params.clip.tema.slug);
                        if (params.clip.pais) $('#pais').val(params.clip.pais.id);

                        var options = {
                            width: "100%",
                            aspectratio: params.clip.aspect || "4:3",
                            title: params.clip.titulo,
                            description: params.clip.descripcion,
                            image: params.clip.thumbnail_grande,
                            tracks: [],
                            sources: []
                        };

                        if (params.clip.hls_url)
                            options.sources.push({file: params.clip.hls_url});
                        options.sources.push({file: params.clip.archivo_url});

                        if (params.clip.sprites_url) {
                            options.tracks.push({
                                file: params.clip.sprites_url,
                                kind: "thumbnails"
                            })
                        }
                        jwplayer("video-player").setup(options);

                        var img_uploader = OMUpload.setup({
                            element: document.getElementById('uploader_img'),
                            autoUpload: true,
                            multiple: false,
                            text: { uploadButton: __('Elegir archivo...') },
                            callbacks: {
                                onUpload: function() {
                                    //$('#edit-form button.save').attr('disabled', 'disabled');
                                    $('.qq-upload-button').empty();
                                    $('#edit-form button.save').attr('disabled', 'disabled');
                                    //$('.editar_form .archivo_status').empty().removeClass('success').removeClass('error');
                                },
                                onCancel: function() {},
                                onComplete: function(id, fileName, responseJSON){
                                    if (responseJSON.error) {
                                        bootbox.alert(__("Error al subir archivo, por favor intente de nuevo"));
                                        $('.qq-upload-fail').empty();
                                    }
                                    if (responseJSON.id) {
                                        $('#upload_img_id').val(responseJSON.id);
                                        $('#upload_img_status').html('<h4><em class="icon-check"></em> ' + __('Archivo subido correctamente.') + '</h4>').addClass('success').removeClass('error');
                                        $('#uploader_img').hide();
                                        $('#edit-form button.save').removeAttr('disabled');
                                    }
                                }
                            }
                        });
                    } else {
                        // creating new clip
                        $('select#origen').on('change', function() {
                            switch ($(this).val()) {
                                case 'url':
                                    $('#url_wrapper').show();
                                    $('#upload_wrapper').hide();
                                    $('#edit-form button.save').removeAttr('disabled');
                                    break;
                                case 'upload':
                                    $('#url_wrapper').hide();
                                    $('#upload_wrapper').show();
                                    if (!$('#upload_clip_id').val()) {
                                        $('#edit-form button.save').attr('disabled', 'disabled');
                                    }
                            }
                        }).trigger('change');
                        var uploader = OMUpload.setup({
                            element: document.getElementById('uploader_clip'),
                            autoUpload: true,
                            multiple: false,
                            text: { uploadButton: __('Elegir archivo...') },
                            callbacks: {
                                onUpload: function() {
                                    $('.qq-upload-button').empty();
                                },
                                onCancel: function() {},
                                onComplete: function(id, fileName, responseJSON){
                                    if (responseJSON.error) {
                                        bootbox.alert(__("Error al subir archivo, por favor intente de nuevo"));
                                        $('.qq-upload-fail').empty();
                                    }
                                    if (responseJSON.id) {
                                        $('#upload_clip_id').val(responseJSON.id);
                                        $('#upload_clip_status').html('<h4><em class="icon-check"></em> ' + __('Archivo subido correctamente.') + '</h4>').addClass('success').removeClass('error');
                                        $('#uploader_clip').hide();
                                        $('#edit-form button.save').removeAttr('disabled');
                                    }
                                }
                            }
                        });
                    }
                    break;
            }
        }
    }


    var populateMediaList = function(opts) {
        $('#cargando').show();
        $('div.content-heading h2').html('<span style="top:25px;left:20px;" class="whirl line"></span>');
        $('ul.media-list').css('min-height','0px');
        current_params = $.extend(opts.params, {tipo: tipo_slug, primero: current_offset+1, ultimo: current_offset+page_size, detalle: 'completo', autenticado: 'admin20' });

        var random = Math.random();
        global_random = random;

        $.ajax({
            //url: api_url + 'clip/?callback=?',
            url: api_url + 'clip/',
            cache: false,
            data: current_params,
            dataType: 'json'
        }).retry({times:3}).done(function(data) {
            if (global_random != random) { console.log('late response...'); return; }
            if (typeof data == 'undefined') { console.log('Bad repsonse'); populateMediaList(opts); return; }
            $('#cargando').hide();
            if (data.length > 0) {
                $('div.content-heading h2').html(tipo_nombre_plural + current_label);
                if (data.length == page_size) {
                    $('[data-action=mostrar-mas]').css({opacity: 1});
                }
                $.each(data, function(i, clip) {
                    appendMediaRow(clip);
                });
            } else {
                $('ul.media-list').css('min-height','300px');
                $('div.content-heading h2').html(tipo_nombre_plural + current_label);
                $('ul.media-list').mustache("empty-query", {});
            }
        });
    };


    var appendMediaRow = function(clip) {
        var list = $('ul.media-list');
        $('<li class="media-row" />').addClass('clip-'+clip.id).appendTo(list);
        updateMediaRow(clip);
    };


    var updateMediaRow = function(clip) {
        clip.fecha_texto = getFechaTexto(clip.fecha, true, true);
        var li = $('ul.media-list li.clip-'+clip.id);
        li.empty().mustache('media-row', {clip: clip}).data('clip', clip).css('opacity', 1);
        li.find('.boton-acciones').empty().mustache('boton-acciones', { clip: clip });
    }


    var loadResources = function(callback, resource_names) {
        var requests = [];
        var r = resource_names || resources;

        // load API resources
        $.each(r, function(i, resource) {
            var opts = {}, params = {};
            if (resource == 'programa' || resource == 'setting') {
                opts.cache = false;
                params.nc = Math.random();
                //params.idioma = idioma;
            }
            requests.push($.ajax($.extend(opts, {
                url: api_url + resource + '/',
                data: $.extend(params, { ultimo: 300, activo: true }),
                dataType: 'json'
            })).retry({times:3}).done(function(data) {
                // append custom resource data
                if (resource in custom_resources) {
                    data = data || [];
                    data = data.concat(custom_resources[resource][idioma]);
                }
                // CUSTOM methods
                if (resource == 'programa') {
                    $.each(data, function(i, programa) {
                        programa['mismo_idioma'] = programa.idioma == idioma;
                    });
                }
                // save resource data
                resources_data[resource] = data;
            }));
        });

        // Load required templates
        $.each(templates, function(i, template) {
            requests.push($.Mustache.load(template));
        });

        // call callback once all requests are done
        $.when.apply($, requests).then(function() {
            callback();
        });
    };


    var buildMenus = function() {
        // build menu tipos
        $('ul#menu_tipos').mustache('menu-tipos-item', { tipos: resources_data.tipo_clip });
        // icons
        $('ul#menu_tipos li a').each(function(i) {
            var tipo = $(this).attr('data-tipo');
            if (tipo in icons) {
                $(this).find('em').addClass('icon-' + icons[tipo]);
            } else {
                $(this).find('em').addClass('icon-doc');
            }
        });

        // build menu modos
        $('ul#menu_secciones').mustache('menu-secciones-item', { categorias: resources_data.categoria }).appendTo($('#menu_secciones'));
        $('ul#menu_programas').mustache('menu-programas-item', { programas: resources_data.programa }).appendTo($('#menu_programas'));
        $('ul#menu_corresponsales').mustache('menu-corresponsales-item', { corresponsales: resources_data.corresponsal }).appendTo($('#menu_corresponsales'));
        $('ul#menu_temas').mustache('menu-temas-item', { temas: resources_data.tema }).appendTo($('#menu_temas'));
    };


    //  var setUser = function(login_user) {
    //     user = login_user;
    //     $('.user-block-name').html(user.nombre);
    //     $('.user-block-upper .user-block-name').html(user.nombre.split(" ")[0]);
    //     $('.user-block-role').html(user.equipo);
    //     $('.user-block-info').show();
    //     $('.user-block-upper').show();
    // }

    var setUser = function(login_user) {
        user = login_user;
        $('.user-block-name').html(user.first_name + ' ' + user.last_name);
        $('.user-block-upper .user-block-name').html(user.first_name);
        $('.user-block-role').html(user.email || SITE_NAME);
        $('.user-block-info').show();
        $('.user-block-upper').show();
        $('body').show();
    }


    // logout
    $('a.user-block-logout').on('click', function(ev) {
        top.window.location.href = '/admin/logout/?next=' + top.window.location.href + top.window.location.hash;
        // Cookies.remove('login_email');
        // Cookies.remove('login_password');
        // user = null;
        // login();
        // $('.user-block-info').hide();
        // $('.user-block-upper').hide();
    });

    var checkLogin = function(callback) {
        $.ajax({
            url: USER_INFO_URL,
            dataType: 'json',
        }).done(function(user) {
            if (!user.username) {
                window.location.href = LOGIN_URL;
            } else {
                setUser(user);
            }
        }).fail(function(err) {
            window.location.href = LOGIN_URL;
        });
    };


    var login = function(callback) {
        var login_email = Cookies.get('login_email'),
            login_password = Cookies.get('login_password');

        if (login_email && login_password) {
            $.ajax({
                url: CAPTURA_API + 'login/',
                dataType: 'json',
                type: 'POST',
                data: {
                    email: login_email,
                    password: login_password
                }
            }).done(function(login_user) {
                if (login_user.success) {
                    Cookies.set('login_email', login_email, { expires: 60 });
                    Cookies.set('login_password', login_password, { expires: 60 });
                    setUser(login_user);
                } else {
                    // login error
                    Cookies.remove('login_email');
                    Cookies.remove('login_password');
                    login();
                }
            }).fail(function() {
                bootbox.alert(__('Error al iniciar. Asegúrate te tener conexión a Internet'));
            });
        } else {
            var modal = bootbox.dialog({
                message: '<div class="panel panel-dark panel-flat">' +
                    '<div class="panel-heading text-center">' +
                        '<img src="img/logo.png" alt="Image" class="block-center img-rounded">' +
                    '</div>' +
                    '<div class="panel-body">' +
                        '<p class="text-center pv login-label">' + __('Favor de iniciar sesión para continuar') + '</p>' +
                        '<form role="form" data-parsley-validate="" novalidate="" class="mb-lg">' +
                            '<div class="form-group has-feedback">' +
                                '<input id="login_email" type="email" placeholder="' + __('Correo electrónico') + '" autocomplete="off" required class="form-control">' +
                                '<span class="fa fa-envelope form-control-feedback text-muted"></span>' +
                            '</div>' +
                            '<div class="form-group has-feedback">' +
                                '<input id="login_password" type="password" placeholder="' + __('Contraseña') + '" required class="form-control">' +
                                '<span class="fa fa-lock form-control-feedback text-muted"></span>' +
                            '</div>' +
                            '<div class="clearfix">' +
                                '<div class="checkbox c-checkbox pull-left mt0">' +
                                    '<label>' +
                                        '<input type="checkbox" value="1" id="login_remember" checked="checked" name="remember">' +
                                        '<span class="fa fa-check"></span> ' + __('Recordarme') +
                                    '</label>' +
                                '</div>' +
                             //'<div class="pull-right"><a href="recover.html" class="text-muted">¿Olvidaste tu contraseña?</a></div>' +
                            '</div>' +
                        '</form>' +
                    '</div>' +
                    '</div>',
                closeButton: false,
                size: 'small',
                buttons: {
                    success: {
                        label: __("Iniciar sesión"),
                        className: "btn-primary",
                        callback: function() {
                            $('.parsley-errors-list').remove();
                            $('#login_email, #login_password').removeClass('parsley-error');
                            var error = false;

                            var email = $('#login_email').val(),
                                password = $('#login_password').val();
                            if (!email) {
                                $('#login_email').addClass('parsley-error');
                                $('#login_email').after('<ul class="parsley-errors-list filled" id="parsley-id-6408"><li class="parsley-required">' + __('Correo electrónico requerido.') + '</li></ul>');
                                error = true;
                            }
                            if (!password) {
                                $('#login_password').addClass('parsley-error');
                                $('#login_password').after('<ul class="parsley-errors-list filled" id="parsley-id-6408"><li class="parsley-required">' + __('Contraseña requerida.') + '</li></ul>');
                                error = true;
                            }

                            if (!error) {
                                // perform login on server
                                $.ajax({
                                    url: CAPTURA_API + 'login/',
                                    dataType: 'json',
                                    type: 'POST',
                                    data: {
                                        email: $('#login_email').val(),
                                        password: md5($('#login_password').val())
                                    }
                                }).done(function(login_user) {
                                    if (login_user.success) {
                                        if ($('#login_remember').is(":checked")) {
                                            Cookies.set('login_email', email, { expires: 60 });
                                            Cookies.set('login_password', md5(password), { expires: 60 });
                                        }
                                        setUser(login_user);
                                        bootbox.hideAll();
                                    } else {
                                        // login error
                                        $('.login-label').before('<ul class="parsley-errors-list filled" id="parsley-id-6408"><li class="parsley-required">' + __('Correo y/o contraseña incorrectos') + '</li></ul>');
                                    }
                                }).fail(function() {
                                    console.log('login failed');
                                });
                            }
                        return false;
                        }
                    }
                }
            }).init(function() {
                $('.modal-backdrop.in').css('opacity', 0.92);
                $('#login_email').focus();
            });
        }
    };



    /* * * * * *  MAIN  * * * * */

    $(document).ready(function() {
        translateNodes();
        $('body').hide();  // Until login

        loadResources(function() {
            checkLogin();

            buildMenus();

            var hash = top.location.hash.replace('#', '');

            // if clip requested
            if (hash && !isNaN(hash)) {
                $.ajax({
                    url: api_url + 'clip/' + hash + '/?nc=' + Math.random(),
                    data: { detalle: 'completo', autenticado: 'admin20' },
                    dataType: 'json'
                }).done(function(clip) {
                    // clip ready
                    go('edit-view', {clip: clip});
                });
            } else if (hash == 'nuevo') {
                go('edit-view', { clip: null });
            } else {
                // Simulate click over the first menu item
                $('#list-view').show();
                $('#menu_tipos a:first').trigger('click');
            }
        });
    });

})();
