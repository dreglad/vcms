/**
 * Created by ileana on 16/04/2015.
 */
$('#anadir-metadatos').click(function(){
    if($('#metadata-key').val()=='' || $('#metadata-valor').val()=='')
        return;
    if( $('.table-responsive').hasClass('hidden'))
    {
        $('.table-responsive').removeClass('hidden');
        $('.table-responsive').addClass('show');
    }

    var newrow= "<tr><td>"+$('#metadata-key').val()+"</td><td>"+$('#metadata-valor').val()+"</td></tr>";
    $('#metadata-key').val('');
    $('#metadata-valor').val('');
    $('#tabla-metadatos tbody').append(newrow);
});


/*

$('td').click(function(){

    var row = $(this).parent().parent().children().index($(this).parent()); alert('Row: ' + row );
});

*/

	   
