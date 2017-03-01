jQuery(function ($) {
    function getResult() {
        var url = $('#create-issue-form-modal').attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: $('#create-issue-form-modal').serialize(),
            dataType: "json",
            statusCode: {
                201: function (data) {
                    window.location.replace(data.redirect_url);
                },
                400: function (data) {
                    $('#id_estimation').css({'border-color': '#f2a696', 'color': '#d68273;'});
                    $('label[for="'+$('#id_estimation').attr('id')+'"]').css('color', '#d16e6c');
                    $('#create_issue_modal-body').prepend('<div class="alert alert-warning"><button class="close" type="button" data-dismiss="alert"><i class="ace-icon fa fa-times"></i></button>'+ data.responseJSON.error.estimation +'</div>')
                }
            }
        })
    }
    $('body').on('click', '#create_issue_modal_btn', function (event) {
        event.preventDefault();
        $('div.alert.alert-warning').remove();
        getResult()
    });
});
