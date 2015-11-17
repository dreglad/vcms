var getFechaTexto = function(fecha, forzar_ano, incluir_dia) {
    var fecha_actual = new Date();

    function toDate(raw){
        if(typeof raw == 'string'){
            var matches = raw.match(/(\d+)-(\d+)-(\d+)[ T](\d+):(\d+):(\d+)/);
            return new Date( matches[1], // año
                (+matches[2])-1, // mes
                matches[3], // día
                matches[4], // hora
                matches[5], // minuto
                matches[6]); //segundo
        }else if(raw instanceof Date){
            return raw;
        }
    };

    fecha = toDate(fecha);

    var formatoFecha = {
        'es': 'dd de MMMM' + ((forzar_ano || fecha_actual.getYear() != fecha.getYear()) ? ', yyyy' : ''),
        'en': 'MMMM dd' + ((forzar_ano || fecha_actual.getYear() != fecha.getYear()) ? ', yyyy' : ''),
        'pt': 'dd de MMMM' + ((forzar_ano || fecha_actual.getYear() != fecha.getYear()) ? ', yyyy' : '')
    }[idioma];

    if (incluir_dia) {
        formatoFecha = 'ddd ' + formatoFecha;
    }

    return $.format.date(fecha, formatoFecha, idioma);
};

var translateNodes = function(node) {
    if (typeof node == 'undefined') {
        node = document;
    }
    $(node).find('.i18n').each(function() {
        var $this = $(this);
        $this.html(__($this.html()));
    });

    $(node).find('.i18n-title[title]').each(function() {
        var $this = $(this);
        $this.attr('title', __($this.attr('title')));
    });

    $(node).find('.i18n-placeholder[placeholder]').each(function() {
        var $this = $(this);
        $this.attr('placeholder', __($this.attr('placeholder')));
    });

    $(node).find('.i18n-data-placeholder[data-placeholder]').each(function() {
        var $this = $(this);
        $this.attr('data-placeholder', __($this.attr('data-placeholder')));
    });

    $(node).find('.i18n-dot[data-original-title]').each(function() {
        var $this = $(this);
        $this.attr('data-original-title', __($this.attr('data-original-title')));
    });
};



idioma = 'es';  // default

var strings = {

    "Cargando...": {'en': 'Loading...', 'pt': 'Cargando...'},

    "Usuario": {'en': 'User', 'pt': 'Usuario'},
    "Equipo": {'en': 'Team', 'pt': 'Equipo'},
    "Nuevo": {'en': 'New', 'pt': 'Nuevo'},
    'Clips de video': {'en': 'Video clips', 'pt': 'Clips de video'},
    "Lista de programas": {'en': 'Shows list', 'pt': 'Lista de programas'},
    "Cargados": {'en': 'Uploaded', 'pt': 'Cargados'},
    "Vistas completas": {'en': 'Full views', 'pt': 'Vistas completas'},
    "EDITAR": {'en': 'EDIT', 'pt': 'EDITAR'},
    "Cerrar": {'en': 'Close', 'pt': 'Cerrar'},

    "Programa original de otro idioma": {'en': 'Original from another language', 'pt': 'Programa original de otro idioma'},
    "Este programa es original de otro idioma. En Español sólo se permiten modificar algunos campos. Puede modificar los datos completos dede el idioma original.": {'en': "This is an original show from another language. In English you can only modify some fields. You can modify all fields from the original language site.", 'pt': 'Este programa es original de otro idioma. En Español sólo se permiten modificar algunos campos. Puede modificar los datos completos dede el idioma original.'},
    "Este clip NO se encuentra publicado": {'en': "this video clip isn't published", 'pt': 'Este clip NO se encuentra publicado'},
    "SELECCIÓN": {'en': "EDITOR'S CHOICE", 'pt': 'SELECCIÓN'},
    "DESPUBLICADO": {'en': 'UNPUBLISHED', 'pt': 'DESPUBLICADO'},
    "Ubicación (ciudad y país)": {'en': 'Location (city and country)', 'pt': 'Ubicación (ciudad y país)'},
    "Programa de origen": {'en': 'Source show', 'pt': 'Programa de origen'},
    "Inserte su búsqueda y presione enter...": {'en': 'Type your search and press enter...', 'pt': 'Inserte su búsqueda y presione enter...'},
    "Buscar": {'en': 'Search', 'pt': 'Buscar'},
    "SIN RESULTADOS": {'en': 'NO RESULTS', 'pt': 'SIN RESULTADOS'},
    "Sin Decripción": {'en': 'No description', 'pt': 'Sin Decripción'},
    

    "Información del video": {'en': 'Video data', 'pt': 'Información del video'},
    "Insertar título": {'en': 'Type title', 'pt': 'Insertar título'},
    "Insertar ciudad": {'en': 'Type city', 'pt': 'Insertar ciudad'},
    "Insertar descripción": {'en': 'Type description', 'pt': 'Insertar descripción'},
    "Insertar título": {'en': 'Type title', 'pt': 'Insertar título'},
    "Insertar sinopsis": {'en': 'Type description', 'pt': 'Insertar sinopsis'},
    "Últimas 3 horas": {'en': 'Last 3 hours', 'pt': 'Últimas 3 horas'},
    "Sin sinopsis": {'en': 'No description', 'pt': 'Sin sinopsis'},
    "Hoy": {'en': 'Today', 'pt': 'Hoy'},
    "Ayer": {'en': 'Yesterday', 'pt': 'Ayer'},
    "Última semana": {'en': 'Last week', 'pt': 'Última semana'},


    "Publicados": {'en': 'Published', 'pt': 'Publicados'},
    "Cargados manualmente": {'en': 'Uploaded', 'pt': 'Cargados manualmente'},
    'Configuración': {'en': 'Settings', 'pt': 'Configuración'},
    "Mostrar más": {'en': 'Show more', 'pt': 'Mostrar más'},
    "Categoría": {'en': 'Category', 'pt': 'Categoría'},
    "vistas": {'en': 'views', 'pt': 'vistas'},
    "Acciones": {'en': 'Actions', 'pt': 'Acciones'},
    "Subir nuevo clip": {'en': 'Upload new video', 'pt': 'Subir nuevo clip'},
    "Salir": {'en': 'Log out', 'pt': 'Salir'},

    "Subir archivo...": {'en': 'Upload file...', 'pt': 'Subir archivo...'},
    "Error al subir archivo, por favor intente de nuevo": {'en': 'Error while uploading file, please try again', 'pt': 'Error al subir archivo, por favor intente de nuevo'},
    "Archivo subido correctamente.": {'en': 'File successfully uploaded', 'pt': 'Archivo subido correctamente.'},
    "Subir nuevo clip": {'en': 'Upload new video', 'pt': 'Subir nuevo clip'},

    "Búsqueda": {'en': 'Search', 'pt': 'Búsqueda'},

    "Por favor introduzca un título": {'en': 'Please enter a title', 'pt': 'Por favor introduzca un título'},
    "Por favor introduzca un título más largo": {'en': 'Please enter a longer title', 'pt': 'Por favor introduzca un título más largo'},
    "Por favor especifique el tipo de clip": {'en': 'Please select a clip type', 'pt': 'Por favor especifique el tipo de clip'},
    "Un clip de tipo programa debe especificar el programa de origen": {'en': 'Clips of type "Show" must specify a source show', 'pt': 'Un clip de tipo programa debe especificar el programa de origen'},
    "Búsqueda": {'en': 'Search', 'pt': 'Búsqueda'},

    "Favor de iniciar sesión para continuar": {'en': 'Please log in to continue', 'pt': 'Favor de iniciar sesión para continuar'},
    "Correo electrónico": {'en': 'Email address', 'pt': 'Correo electrónico'},
    "Contraseña": {'en': 'Password', 'pt': 'Contraseña'},
    "Recordarme": {'en': 'Remember me', 'pt': 'Recordarme'},
    "Iniciar sesión": {'en': 'Log in', 'pt': 'Iniciar sesión'},

    "Correo electrónico requerido.": {'en': 'Email address is required.', 'pt': 'Correo electrónico requerido.'},
    "Contraseña requerida.": {'en': 'Password is required.', 'pt': 'Contraseña requerida.'},
    "Correo y/o contraseña incorrectos": {'en': 'Wrong email and/or password', 'pt': 'Correo y/o contraseña incorrectos'},
    "Contraseña": {'en': 'Password', 'pt': 'Contraseña'},

    'Reproductor de video': {'en': 'Video player', 'pt': 'Reproductor de video'},
    

    'Para desarrolladores e integración de sistemas': {'en': 'For developers and systems integrators', 'pt': 'Para desarrolladores e integración de sistemas'},
    'URL oficial para compartir': {'en': 'URL for sharing', 'pt': 'URL oficial para compartir'},
    'Código embed': {'en': 'Embed code', 'pt': 'Código embed'},
    'Ppara incrustar en una página web con comportamiento responsive': {'en': 'HTML code for embedding within a web page', 'pt': 'Ppara incrustar en una página web con comportamiento responsive'},
    'Para incrustar como iframe, generalmente para ambientes donde no se pueda usar Javascript': {'en': 'For embedding as an iframe or using where Javascript is not supported', 'pt': 'Para incrustar como iframe, generalmente para ambientes donde no se pueda usar Javascript'},
    'URL de Player': {'en': 'Player URL', 'pt': 'URL de Player'},
    'URL de Player SSL': {'en': 'Player URL (SSL)', 'pt': 'URL de Player SSL'},    
    'Para incrustar como iframe via SSL': {'en': 'For embedding within a secure (SSL) web page', 'pt': 'Para incrustar como iframe via SSL'},
    'Archivo': {'en': 'File', 'pt': 'Archivo'},
    'de video': {'en': 'Direct video file ', 'pt': 'de video'},


    'Contenido de Home': {'en': 'Home contents', 'pt': 'Contenido de Home'},
    'Home de Sitio de Videos': {'en': 'Video Website Home Page Settings', 'pt': 'Home de Sitio de Videos'},
    'Modo': {'en': 'Mode', 'pt': 'Modo'},
    'Filtro': {'en': 'Filter', 'pt': 'Filtro'},
    'Vistos recientemente': {'en': 'Recently watched', 'pt': 'Vistos recientemente'},
    'Última búsqueda': {'en': 'Latest search', 'pt': 'Última búsqueda'},
    'Tipo': {'en': 'Type', 'pt': 'Tipo'},
    'Modo': {'en': 'Mode', 'pt': 'Modo'},
    'Programa': {'en': 'Show', 'pt': 'Programa'},
    'Tema': {'en': 'Topic', 'pt': 'Tema'},
    'Todos': {'en': 'All', 'pt': 'Todos'},
    'Primero': {'en': 'First', 'pt': 'Primero'},
    'Último': {'en': 'Last', 'pt': 'Último'},
    'Último': {'en': 'Last', 'pt': 'Último'},
    'Añadir fila': {'en': 'Add row', 'pt': 'Añadir fila'},
    'Configuración de Home actualiada': {'en': 'Home page settings saved successfully', 'pt': 'Configuración de Home actualiada'},

    'Especifique los IDs de los videos que desea mostrar': {'en': 'Specify the video IDs you want to be displayed', 'pt': 'Especifique los IDs de los videos que desea mostrar'},
    'Especifique los criterios de filtrado que desea aplicar': {'en': 'Specify the filtering criteria you want to apply', 'pt': 'Especifique los criterios de filtrado que desea aplicar'},
    'Se mostrarán los últimos videos vistos por el usuario': {'en': "It will diplay the user's most recently watched videos", 'pt': 'Se mostrarán los últimos videos vistos por el usuario'},
    'Se mostrarán los resultados de la última búsqueda que realizó el usuario': {'en': "It will display the user's latest search results", 'pt': 'Se mostrarán los resultados de la última búsqueda que realizó el usuario'},
    'Especifique un clip para mostrar sus videos relacionados.': {'en': 'Specify a video ID to display videos related o it', 'pt': 'Especifique un clip para mostrar sus videos relacionados.'},
    'Especifique una búsqueda de texto. Adicionalmente puede filtrar el resultado': {'en': 'Specify a text search, additionally you can filter the results.', 'pt': 'Especifique una búsqueda de texto. Adicionalmente puede filtrar el resultado'},
    'Todos los videos': {'en': 'All videos', 'pt': 'Todos los videos'},
    'Todos los tipos': {'en': 'Any type', 'pt': 'Todos los tipos'},
    'Todos los programas': {'en': 'Any show', 'pt': 'Todos los programas'},
    'Todos los temas': {'en': 'Any topic', 'pt': 'Todos los temas'},
    'Todas las categorías': {'en': 'Any category', 'pt': 'Todas las categorías'},
    'Todos los países': {'en': 'Any country', 'pt': 'Todos los países'},
    'Todos los corresponsales': {'en': 'Any correspondent', 'pt': 'Todos los corresponsales'},

    'Volver': {'en': 'Back', 'pt': 'Volver'},
    'Anterior': {'en': 'Previous', 'pt': 'Anterior'},
    'Siguiente': {'en': 'Next', 'pt': 'Siguiente'},
    'reproducciones': {'en': 'views', 'pt': 'reproducciones'},
    'Categoría': {'en': 'Category', 'pt': 'Categoría'},
    'Programa': {'en': 'Show', 'pt': 'Programa'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Serie': {'en': 'Series', 'pt': 'Serie'},
    'Embeber': {'en': 'Embed', 'pt': 'Embeber'},
    'Descargar': {'en': 'Download', 'pt': 'Descargar'},
    'Recomendados': {'en': 'Recomended', 'pt': 'Recomendados'},

    'Noticia': {'en': 'News', 'pt': 'Notícia'},
    'Entrevista': {'en': 'Interview', 'pt': 'Entrevista'},
    'Documental': {'en': 'Documentary', 'pt': 'Documentário'},
    'Reportaje': {'en': 'Report', 'pt': 'Reportagen'},
    'Independiente': {'en': 'Indepentant', 'pt': 'Independiente'},
    'independientes': {'en': 'independants', 'pt': 'independientes'},
    'Promocional': {'en': 'promotional', 'pt': 'promocional'},
    'promocionales': {'en': 'promotionals', 'pt': 'promocionales'},
    'Síntesis Web': {'en': 'Web Synthesis', 'pt': 'Síntesis Web'},
    'Especial Web': {'en': 'Web Special', 'pt': 'Especiais Web'},
    'Infográfico': {'en': 'Infographic', 'pt': 'Infográfico'},

    'Archivo': {'en': 'File', 'pt': 'Archivo'},
    'Archivo subtitulado': {'en': 'Subtitled file', 'pt': 'Archivo subtitulado'},
    'Subtítulos': {'en': 'Subtitles', 'pt': 'Subtítulos'},

    'Filtros': {'en': 'Filters', 'pt': 'Filtros'},

    'Política': { en: 'Politics', pt: 'Política' },
    'politica': { en: 'politics', pt: 'politica' },
    'Economía': { en: 'Economy', pt: 'Economia' },
    'economia': { en: 'economy', pt: 'economia' },
    'Medio Ambiente': { en: 'Environment', pt: 'Meio Ambiente' },
    'Ciencia': { en: 'Science', pt: 'Ciência' },
    'Salud': { en: 'Health', pt: 'Salud' },
    'Ciencia y Tecnologia': { en: 'Science and Technology', pt: 'Ciência e Tecnologia' },
    'Cultura': { en: 'Culture', pt: 'Cultura' },
    'Deportes': { en: 'Sports', pt: 'Esporte' },

    'mes': {'en': 'month', 'pt': 'mes'},
    'meses': {'en': 'months', 'pt': 'meses'},
    'semana': {'en': 'week', 'pt': 'semana'},
    'semanas': {'en': 'weeks', 'pt': 'semanas'},
    'día': {'en': 'day', 'pt': 'día'},
    'días': {'en': 'days', 'pt': 'días'},
    'hora': {'en': 'hours', 'pt': 'hora'},
    'horas': {'en': 'hours', 'pt': 'horas'},
    'minuto': {'en': 'minute', 'pt': 'minuto'},
    'minutos': {'en': 'minutes', 'pt': 'minutos'},
    'segundo': {'en': 'second', 'pt': 'segundo'},
    'segundos': {'en': 'seconds', 'pt': 'segundos'},
    'justo ahora': {'en': 'just now', 'pt': 'justo ahora'},

    'Actualizar': {'en': 'Refresh', 'pt': 'Actualizar'},

    'Fecha': {'en': 'Date', 'pt': 'Fecha'},
    'Vistas': {'en': 'Views', 'pt': 'Vistas'},
    'Ubicación': {'en': 'Location', 'pt': 'Ubicación'},
    'País secundario': {'en': 'Secondary country', 'pt': 'País secundario'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},

    'Editar': {'en': 'Edit', 'pt': 'Editar'},
    'Links y embed': {'en': 'Links & embed', 'pt': 'Links y embed'},
    'Despublicar': {'en': 'Unpublish', 'pt': 'Despublicar'},
    'Publicar': {'en': 'Publish', 'pt': 'Publicar'},
    'Descargar video': {'en': 'Download video', 'pt': 'Descargar video'},
    'Eliminar': {'en': 'Delete', 'pt': 'Fecha'},

    'Título': {'en': 'Title', 'pt': 'Título'},
    'Descripción': {'en': 'Description', 'pt': 'Descripción'},
    'Tipo de clip': {'en': 'Clip type', 'pt': 'Tipo de clip'},
    'Ciudad': {'en': 'City', 'pt': 'Ciudad'},
    'País': {'en': 'Country', 'pt': 'País'},
    'Categoría informativa': {'en': 'Category', 'pt': 'Categoría'},
    'Seleccionado': {'en': 'Choosen', 'pt': 'Seleccionado'},
    'Selección del Editor': {'en': "Editor's Choice", 'pt': 'Selección del Editor'},
    '(Selección del Editor)': {'en': "(Editor's Choice)", 'pt': '(Selección del Editor)'},
    '(publicar inmediatamente)': {'en': '(publish inmediately)', 'pt': '(publicar inmediatamente)'},
    'Cancelar': {'en': 'Cancel', 'pt': 'Cancelar'},
    'Seleccionar Venezuela': {'en': 'Select Venezuela', 'pt': 'Seleccionar Venezuela'},
    'Guardar cambios': {'en': 'Save changes', 'pt': 'Guardar cambios'},
    'Guardar': {'en': 'Save', 'pt': 'Guardar'},
    'Restaurar': {'en': 'Restore', 'pt': 'Restaurar'},
    'Debe especificar un título antes de guardar': {'en': 'You must enter a title before saving', 'pt': 'Debe especificar un título antes de guardar'},
    'El título no puede ser mayor a 120 caracteres': {'en': "Title can't be longer than 12 characters", 'pt': 'El título no puede ser mayor a 120 caracteres'},
    'Al elegir el tipo "programa" es necesario también elegir un prgorama de origen': {'en': 'When selecting the "show" type you must also select a source show from the listing', 'pt': 'Al elegir el tipo "programa" es necesario también elegir un prgorama de origen'},
    'Reemplazar imagen': {'en': 'Replace thumbnail', 'pt': 'Reemplazar imagen'},
    'Cancelar reemplazo de imagen': {'en': 'Canel thumbnail replacement', 'pt': 'Cancelar reemplazo de imagen'},
    'Elegir archivo...': {'en': 'Select file...', 'pt': 'Elegir archivo...'},
    'Reemplazar imagen': {'en': 'Replace image', 'pt': 'Reemplazar imagen'},
    'Archivo subido correctamente': {'en': 'File was successfully uploaded', 'pt': 'Archivo subido correctamente'},
    'Genera una nueva imagen miniatura extraida de una posición aleatoria': {'en': 'Auto-generates a new thumbnail based on a random position', 'pt': 'Genera una nueva imagen miniatura extraida de una posición aleatoria'},
    'Confirme que desea auto-generar una nueva imagen/thumbnail para este clip extraida de una posición aleatoria': {'en': 'Confirm you really want to auto-generate a new thumbnail for this clip based on a random position', 'pt': 'Confirme que desea auto-generar una nueva imagen/thumbnail para este clip extraida de una posición aleatoria'},
    

    'Link permanente': {'en': 'Permalink', 'pt': 'Link permanente'},
    'URL canónica': {'en': 'Chanonical URL', 'pt': 'URL canónica'},
    'Embed inline': {'en': 'Inline embed', 'pt': 'EMbed inline'},
    'Recomendado': {'en': 'Recomended', 'pt': 'Recomendado'},
    'No recomendado': {'en': 'Not recomended', 'pt': 'No recomendado'},
    'URL de Player': {'en': 'Player URL', 'pt': 'URL de Player'},
    'Para desarrolladores': {'en': 'For developers', 'pt': 'Para desarrolladores'},
    'Cerrar': {'en': 'Close', 'pt': 'Cerrar'},

    'Archivo de video': {'en': 'Video file', 'pt': 'Archivo de video'},
    'Datos del clip': {'en': 'Clip info', 'pt': 'Datos del clip'},

    '(Máx 75 caracteres)': {'en': '(75 chars maximum)', 'pt': 'Max 75 caracteres'},
    
    'publicados': {'en': 'published', 'pt': 'publicados'},
    'Publicado': {'en': 'Published', 'pt': 'Publicado'},
    'Publicar clip inmediatamente': {'en': 'Publish after creation', 'pt': 'Publicar clip inmediatamente'},
    'despublicados': {'en': 'unpublished', 'pt': 'despublicados'},
    'Despublicados': {'en': 'Unpublished', 'pt': 'Despublicados'},


    'Confirme que desea despublicar este clip': {'en': 'Confirm you really want to unpublish this clip', 'pt': 'Confirme que desea despublicar este clip'},
    'Confirme que desea publicar este clip': {'en': 'Confirm you really want to publish this clip', 'pt': 'Confirme si desea publicar este clip'},
    'Confirme que desea eliminar este clip': {'en': 'Confirm you really want to delete this video clip', 'pt': 'Confirme que desea eliminar este clip'},
    'Video agregado corectamente. Puede tardar unos minutos en procesarse según la cola de trabajo.': {'en': 'Video added successfully. It may take some minutes before it is available.', 'pt': 'Video agregado corectamente. Puede tardar unos minutos en procesarse según la cola de trabajo.'},
    'Ocurrió un error. Intente de nuevo y si el problema persiste contacte al administrador.': {'en': 'An error ocurred. Please try again, if the issue persist contact the administrator.', 'pt': '"Ocurrió un error. Intente de nuevo y si el problema persiste contacte al administrador.'},
    'Procesando...': {'en': 'Processing...', 'pt': 'Procesando...'},

    // ERRORES
    "Error al iniciar. Asegúrese te tener conexión a Internet": {'en': 'Error while initializing, please make sure you have Internet access', 'pt': 'Error al iniciar. Asegúrese te tener conexión a Internet'},
    'Error eliminando clip, verifique que aún tiene conexión a Internet e intente de nuevo.': {'en': 'Error while deleting clip. Please make sure you still have Internet access and try again', 'pt': 'Error eliminando clip, verifique que aún tiene conexión a Internet e intente de nuevo.'},
    'Error despublicando clip, verifique que aún tiene conexión a Internet e intente de nuevo.': {'en': 'Error while unpublishing clip. Please make sure you still have Internet access and try again', 'pt': 'Error despublicando clip, verifique que aún tiene conexión a Internet e intente de nuevo.'},
    'Error publicando clip, verifique que aún tiene conexión a Internet e intente de nuevo.': {'en': 'Error while publishing clip. Please make sure you still have Internet access and try again', 'pt': 'Error publicando clip, verifique que aún tiene conexión a Internet e intente de nuevo.'},
    'Error guardando la información. Verifique que aún tenga conexión a Internet e intente de nuevo': {'en': 'Error sending data. Please make sure you still have Internet access and try again', 'pt': 'Error guardando la información. Verifique que aún tenga conexión a Internet e intente de nuevo'},

    // Progreso
    "Puede esperar o cerrar esta ventana en cualquier momento": {'en': 'You can either wait or close this window at any moment', 'pt': 'Puede esperar o cerrar esta ventana en cualquier momento'},
    'Iniciando...': {'en': 'Starting', 'pt': 'Iniciando...'},
    'En cola...': {'en': 'Queued...', 'pt': 'En cola...'},
    'Preparando archivo...': {'en': 'Prepairing file', 'pt': 'Preparando archivo...'},
    'Procesando video...': {'en': 'Processing video...', 'pt': 'Procesando video...'},
    'Finalizando...': {'en': 'Finalizing', 'pt': 'Finalizando...'},
    'Archivo de video inválido.': {'en': 'Invalid video file', 'pt': 'Archivo de video inválido.'},
    'Verificando...': {'en': 'Verifying', 'pt': 'Verificando...'},
    'Completado': {'en': 'Completed', 'pt': 'Completado'},
    'Insertar horario': {'en': 'Type schedule', 'pt': 'Insertar horario'},

    // Programas
    'Horario': {'en': 'Schedule', 'pt': 'Horario'},
    'Tipo de programa': {'en': 'Show type', 'pt': 'Tipo de programa'},
    'Widget de Twitter': {'en': 'Twitter widget', 'pt': 'Widget de Twitter'},
    'Nombre del conductor': {'en': 'Name of host', 'pt': 'Nombre del conductor'},
    'Twitter del conductor': {'en': 'Twitter of host', 'pt': 'Twitter del conductor'},
    'Widget de Twitter del conductor': {'en': 'Twitter widget of host', 'pt': 'Widget de Twitter del conductor'},
    'Sinopsis': {'en': 'Description', 'pt': 'Descripción'},
    'Banner del programa': {'en': "Show's banner", 'pt': 'Banner del programa'},

    // filtrador
    'países': {'en': 'countries', 'pt': 'paises'},
    'categorías': {'en': 'categories', 'pt': 'categorías'},
    'Categorías': {'en': 'Categories', 'pt': 'Categorías'},
    'perosnajes': {'en': 'people', 'pt': 'personajes'},
    'temas': {'en': 'topics', 'pt': 'temas'},
    'corresponsales': {'en': 'correspondents', 'pt': 'corresponsales'},
    'Corresponsales': {'en': 'Correspondents', 'pt': 'Corresponsales'},
    'fecha': {'en': 'date', 'pt': 'fecha'},
    'Fecha': {'en': 'Date', 'pt': 'Fecha'},
    'fechas': {'en': 'dates', 'pt': 'fechas'},
    'Fechas': {'en': 'Dates', 'pt': 'Fechas'},
    'entrevistados': {'en': 'interviewed', 'pt': 'entrevistados'},
    'programas': {'en': 'shows', 'pt': 'programas'},
    'Programas': {'en': 'Shows', 'pt': 'Programas'},
    'Aceptar': {'en': 'Go', 'pt': 'Aceptar'},
    'Desde': {'en': 'From', 'pt': 'desde'},
    'Hasta': {'en': 'To', 'pt': 'hasta'},

    'Sin resultados': {'en': 'No results', 'pt': 'Sin resultados'},
    'Sin resultados para': {'en': 'No results for', 'pt': 'Sin resultados para'},


    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'},
    'Corresponsal': {'en': 'Correspondent', 'pt': 'Corresponsal'}

};

function __(txt) {
    if (idioma != 'es' && txt in strings)
        return strings[txt][idioma];
    else
        return txt;
}





