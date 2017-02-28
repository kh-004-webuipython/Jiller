jQuery(function ($) {
    function getResult() {
        var url = $('#create_sprint_form').attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: $('#create_sprint_form').serialize(),
            dataType: "json",
            statusCode: {
                400: function (data) {
                    $('#create_sprint_form').addClass('has-error');
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
