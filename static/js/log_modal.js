jQuery(function ($) {
    function getResult() {
        var url = $('#log-modal-form').attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: $('#log-modal-form').serialize(),
            dataType: "json",
            statusCode: {
                201: function (data) {
                    console.log(data);
                    $('.modal-body').empty();
                    $('.modal-footer').empty();
                    $('.modal-body').append('<h3>' + $('#log-modal').attr('data-success-title') + '</h3>');
                    $('div.progress-bar').css('width', data.completion_rate + '%');
                    $('div.progress.pos-rel').attr('data-percent', data.completion_rate + '%')
                },
                400: function (data) {
                    $('#log-modal-form').addClass('has-error');
                    $('div.help-block').append("<span class='error-block'>" + data.responseJSON.error.cost + "</span>")
                }
            }
        })
    }

    $('body').on('click', '#log-save', function (event) {
        event.preventDefault();
        $('div.help-block span').remove();
        getResult()
    });
});