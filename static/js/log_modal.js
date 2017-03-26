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
                    $('.modal-body').empty();
                    $('.modal-footer').empty();
                    $('#logs-tab .comments').empty()
                    $('.modal-body').append('<h3>' + $('#log-modal').attr('data-success-title') + '</h3>');
                    $('div.progress-bar').css('width', data.completion_rate + '%');
                    $('div.progress.pos-rel').attr('data-percent', data.completion_rate + '%');
                    $('#logs-tab .comments').prepend('<div class="itemdiv commentdiv"><div class="user"></div><div class="body"><div class="name"><a href=""'+ data.user_link +'">'+ data.user +'</a><span>'+ '(' + data.cost +' hours)'+ '</span></div><div class="time"><span>'+ data.date_created +'</span></div><div class="text">'+ data.note +'</div> </div> </div>')
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