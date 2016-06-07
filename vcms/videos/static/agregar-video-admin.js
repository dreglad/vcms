(function($) {
    $(function() {
        // Está en tab nuevo ?
        if ($('.suit-tab-nuevo').length) {

            $('button[name="_continue"],button[name="_addanother"]').hide();
            function toogleOrigenFieldSet(value) {
                $('fieldset.externo, fieldset.local').hide();
                $('fieldset.' + value).show();
            }

            var val = $('input[name=origen][value=local]').is(':checked') ?
                          'local' : 'externo';
            toogleOrigenFieldSet(val);


            $('input[name=origen]').change(function() {
                var val = $('input[name=origen][value=local]').is(':checked')?
                          'local' : 'externo';
                toogleOrigenFieldSet(val);
            });
        }
    });
})(django.jQuery);
