document.addEventListener("DOMContentLoaded", function () {
    var csrftoken = getCookie('csrftoken');
    var tables = document.querySelectorAll('[data-issueType]');
    var dragSrcRow;
    var curDragOverTable;

    tables.forEach(
        function (table) {
            table.addEventListener('dragenter', handleDragEnter, false);
            table.addEventListener('dragover', handleDragOver, false);
            table.addEventListener('drop', handleDrop, false);
        });

    document.querySelectorAll('[data-id]').forEach(
        function (row) {
            row.addEventListener('dragstart', handleDragStart, false);
            row.addEventListener('drop', handleDrop, false);
            row.addEventListener('dragend', handleDragEnd, false);
        });

    function handleDragStart(e) {
        this.classList.add('chosen');
        dragSrcRow = e.target;   // remember start drag row
        curDragOverTable = dragSrcRow.offsetParent;
    }

    // mark tables borders over drag
    function handleDragEnter(e) {
        tables.forEach(function (table) {
            if (table.contains(e.target) && table != curDragOverTable) {
                curDragOverTable.classList.remove('over');
                curDragOverTable = table;
                curDragOverTable.classList.add('over');
            }
        });
    }

    //need for mark borders
    function handleDragOver(e) {
        e.preventDefault();
    }

    // unmark borders of tables and start row
    function handleDragEnd(e) {
        tables.forEach(function (table) {
            table.classList.remove('over');
            e.target.classList.remove('chosen');
        });
    }

    function handleDrop(e) {
        if (e.stopPropagation) {
            e.stopPropagation(); // stops the browser from redirecting.
        }
        e.preventDefault();
        tables.forEach(
            function (table) {
                if (table != dragSrcRow.offsetParent) {
                    if (table.contains(e.target)) {
                        // Post request
                        var xhr = new XMLHttpRequest();
                        var body = 'table=' + encodeURIComponent(table.dataset['issuetype']) +
                            '&id=' + encodeURIComponent(dragSrcRow.dataset['id']);
                        xhr.open("POST", '/project/issue_push/', true);
                        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                        xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
                        xhr.onreadystatechange = function() {
                            if (xhr.readyState == 4 && xhr.status == 200) {
                                window.location.reload();
                            }
                        };
                        xhr.send(body);
                    }

                }
            }
        );

        return false;
    }
});