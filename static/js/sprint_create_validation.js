jQuery(function ($) {
    function getResult() {
        var url = $('#create_sprint_form').attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: $('#create_sprint_form').serialize(),
            dataType: "json",
            statusCode: {
                201: function (data) {
                    window.location.replace(data.redirect_url);
                },
                400: function (data) {
                    $('#id_duration').css({'border-color': '#f2a696', 'color': '#d68273;'});
                    $('label[for="'+$('#id_duration').attr('id')+'"]').css('color', '#d16e6c');
                    $('#create_sprint_modal-body').prepend('<div class="alert alert-warning"><button class="close" type="button" data-dismiss="alert"><i class="ace-icon fa fa-times"></i></button>'+ data.responseJSON.error.duration +'</div>')
                }
            }
        })
    }
    $('body').on('click', '#create_sprint_modal_btn', function (event) {
        event.preventDefault();
        $('div.alert.alert-warning').remove();
        getResult()
    });
});
