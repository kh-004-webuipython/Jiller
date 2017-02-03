$(function() {
    function getCookie(name) {
        var cookieValue = null;

        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $( "#sortable" ).sortable({
        items: 'tr.sortable-row',
        containment: "parent",
        delay: 200,
        opacity: 0.6,
        cursor: 'move',
        tolerance: 'pointer',
        forcePlaceholderSize: true,
        update: function(event, ui) {
            var alterData = {};
            order = document.querySelectorAll('#sortable tr');

            for(var i = 0; i < order.length; i++) {
                if(i+1 != order[i].getAttribute('data-order')) {
                    var id = order[i].getAttribute('data-id');
                    alterData['' + id] = i + 1;
                }
            }

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
                url: '/project/issue_order/',

                success : function(response){
                    var element = $('#error-message');
                    element.empty();
                    for(var i = 0; i < order.length; i++)
                        order[i].setAttribute('data-order', (i+1).toString())
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    var element = $('#error-message');
                    element.empty();
                    element.append('<h2 class="alert alert-warning">' +
                        'Issue message wasn\'t changed.</h2>');
                }
            });
        }
    });
});