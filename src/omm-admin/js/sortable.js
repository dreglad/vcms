/**
 * Created by ileana on 16/04/2015.
 */

$('.sortable').sortable({
    forcePlaceholderSize: true,
    items: 'tr' ,
    placeholder : '<tr><td colspan="6">&nbsp;</td></tr>'
    //placeholder: '<div class="box-placeholder p0 m0"><div></div></div>'
}).bind('sortupdate', function(e, ui) {
    var parent = ui.startparent;
    var rows = parent.find("tr");
    var i=0;
    rows.each(function () {
        var orden = $(this).find("td").eq(0).find(".editable-orden").html(i+1);
        i++;
    })
 });


