$(function() {
    var csrftoken = getCookie('csrftoken');
    var project = $('div.page-header').data('project');

    sortable();

    function sortable() {
        $('.sortable').sortable({
            delay: 200,
            connectWith: '.sortable',
            opacity: 0.6,
            cursor: 'move',
            dropOnEmpty: true,
            containment: '#main-container',
            revert: true,
            tolerance: 'pointer',
            start: function (event, ui) {
                var placeToDrop = $('#workload-template .sortable');
                for(var i = 0; i < placeToDrop.length; i++) {
                    placeToDrop[i].classList.add('contain-box');
                    placeToDrop[i].classList.add('over');
                }

                ui.item.closest('div').removeClass('over');
            },
            out: function () {
                var placeToDrop = $('#workload-template .sortable');
                for(var i = 0; i < placeToDrop.length; i++)
                    placeToDrop[i].classList.remove('over');

                placeToDrop.on("sortover", function ( event, ui ) {
                    ui.placeholder.closest('div').addClass('over');
                });
            },
            stop: function (event, ui) {
                var placeToDrop = $('#workload-template .sortable');
                placeToDrop.off('sortover');

                for(var i = 0; i < placeToDrop.length; i++)
                    placeToDrop[i].classList.remove('contain-box');
            },
            remove: function (event, ui) {
                var alterData = {};
                alterData['issue'] = ui.item.data('issue');
                alterData['relate'] = ui.item.parent().data('relate');
                var sprintStatus = $('#sprint-status').data('status');

                $.ajax({
                    data: { data: JSON.stringify(alterData) },
                    type: 'POST',
                    url: '/project/' + project + '/workload_manager/' + sprintStatus + '/',

                    success : function(data){
                        var element = $('#error-message');
                        element.empty();
                        $('#workload-template').html(data);
                        moveProgressBar();
                        sortable();
                    },
                    error: function (error) {
                        var message = 'Something go wrong';
                        if(error.responseText)
                            message = error.responseText;
                        var element = $('#error-message');
                        element.empty();
                        element.html('<h2 class="alert alert-warning">' +
                            message + '</h2>');
                        setTimeout(location.reload.bind(window.location), 3500);
                    }
                });
            }
        });
    }
});

