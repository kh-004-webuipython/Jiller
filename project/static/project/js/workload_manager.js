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

    var sortable = document.querySelectorAll('.sortable');

    $.each(sortable, function(i, item) {
        $(item).sortable({
            delay: 200,
            connectWith: "div",
            opacity: 0.6,
            cursor: 'move',
            tolerance: 'pointer',
            dropOnEmpty: true
            // update: handler(event, ui)
        });
    });

    // function handler(event, ui) {
    //     var alterData = {};
    //     order = document.querySelectorAll('#sortable tr');
    //
    //     for(var i = 0; i < order.length; i++) {
    //         if(i+1 != order[i].getAttribute('data-order')) {
    //             var id = order[i].getAttribute('data-id');
    //             alterData['' + id] = i + 1;
    //         }
    //     }
    //
    //     $.ajaxSetup({
    //         beforeSend: function(xhr, settings) {
    //             if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    //                 xhr.setRequestHeader("X-CSRFToken", csrftoken);
    //             }
    //         }
    //     });
    //
    //     $.ajax({
    //         data: { data: JSON.stringify(alterData) },
    //         type: 'POST',
    //         url: '/project/issue_order/',
    //
    //         success : function(response){
    //             var element = $('#error-message');
    //             element.empty();
    //             for(var i = 0; i < order.length; i++)
    //                 order[i].setAttribute('data-order', (i+1).toString())
    //         },
    //         error: function (xhr, ajaxOptions, thrownError) {
    //             var element = $('#error-message');
    //             element.empty();
    //             element.append('<h2 class="alert alert-warning">' +
    //                 'Issue priority wasn\'t changed.</h2>');
    //         }
    //     });
    // }
});

