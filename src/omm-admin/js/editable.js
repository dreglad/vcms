// JavaScript Document
// ----------------------------------- 

(function(window, document, $, undefined){
    
    $(function(){

        // Font Awesome support
        $.fn.editableform.buttons =
          '<button type="submit" class="btn btn-primary btn-sm editable-submit">'+
            '<i class="fa fa-fw fa-check"></i>'+
          '</button>'+
          '<button type="button" class="btn btn-default btn-sm editable-cancel">'+
            '<i class="fa fa-fw fa-times"></i>'+
          '</button>';

       //defaults
       //$.fn.editable.defaults.url = '../server/xeditable.res';
        $.fn.editable.defaults.mode = 'inline';
	   $('.editable-orden').editable({
           disabled:true,
           placement: 'right',
           showbuttons: false,
           source: [
               {value: 1, text: '1'},
               {value: 2, text: '2'},
               {value: 3, text: '3'}
           ],
           success: function(response, newValue) {
               console.log('amdakdm');
           }
       });

	   
	   $('#programas_list').on('click', 'a.editable-descripcion', function(ev) {
            console.log('editable-descripcion');
            ev.preventDefault();
            $(this).editable({
                type: "text-area",
                placeholder:"Editar descripción...",
                title:"Descripción",
                rows: 3,
                inputclass: 'editable-textarea',
                success: function(response, newValue) {
                    console.log('funciono');
                }
            });
        });
        $('#programas_list').on('click', 'a.editable-horario', function(ev) {
            ev.preventDefault();
            console.log($(this));
            console.log($(this).text());
            $(this).editable({
                type:"text",
                inputclass: "ancho200"
            });
        });
	   
	   $('.editable-activo').editable({
            source: [
                {value: 0, text: 'NO'},
                {value: 1, text: 'SI'}
            ],
            display: function(value, sourceData) {
                 var colors = {"": "gray", 0: "red", 1: "green"},
                     elem = $.grep(sourceData, function(o){return o.value == value;});
                     
                 if(elem.length) {
                     $(this).text(elem[0].text).css("color", colors[value]);
                 } else {
                     $(this).empty();
                 }
            },
			 showbuttons: false
        });


	   
	});//$(function(){
})(window, document, window.jQuery);

