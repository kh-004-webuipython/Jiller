$(function() {
    moveProgressBar();
    // on browser resize...
    $(window).resize(function() {
        moveProgressBar();
    });

    // SIGNATURE PROGRESS
    function moveProgressBar() {
        var items = document.querySelectorAll('.progress-wrap');
        $.each(items, function(index, value) {
            var getPercent = ($(value).data('progress-percent') / 100);
            var getProgressWrapWidth = $('.progress-wrap').width();
            var progressTotal = getPercent * getProgressWrapWidth;
            var animationLength = 2500;

            // on page load, animate percentage bar to data percentage length
            // .stop() used to prevent animation queueing
            $(value.firstElementChild).stop().animate({
                left: progressTotal
            }, animationLength);
        })
    }

    var csrftoken = getCookie('csrftoken');
    var project = $('div.page-header').data('project');

    var sortable = document.querySelectorAll('.sortable');

    $.each(sortable, function(i, item) {
        $(item).sortable({
            delay: 200,
            connectWith: "div",
            opacity: 0.6,
            cursor: 'move',
            tolerance: 'pointer',
            dropOnEmpty: true,
            stop: function (event, ui) {
                var alterData = {};
                alterData['issue'] = ui.item.data('issue');
                alterData['employee'] = ui.item.parent().data('employee');

                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                });

                $.ajax({
                    data: { data: JSON.stringify(alterData) },
                    type: 'POST',
                    url: '/project/' + project + '/workload_manager',

                    success : function(data){
                        window.location.reload();
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        var element = $('#error-message');
                        element.empty();
                        element.append('<h2 class="alert alert-warning">' +
                            'Something went wrong.</h2>');
                    }
                });
            }
        });
    });
});

