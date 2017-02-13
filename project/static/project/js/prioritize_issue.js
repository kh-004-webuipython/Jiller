$(function() {
    $('#sortable td').each(function(){
        $(this).css('width', $(this).outerWidth() +'px');
    });

    $('table th').each(function(){
        $(this).css('width', $(this).outerWidth() +'px');
    });

    var csrftoken = getCookie('csrftoken');

    $( "#sortable" ).sortable({
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
                    for(var i = 0; i < order.length; i++) {
                        var item = order[i];
                        item.setAttribute('data-order', (i+1).toString());
                        item.firstElementChild.innerHTML = (i+1).toString();
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    var element = $('#error-message');
                    element.empty();
                    element.append('<h2 class="alert alert-warning">' +
                        'Issue priority wasn\'t changed.</h2>');
                }
            });
        }
    });
});
