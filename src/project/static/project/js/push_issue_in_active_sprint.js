document.addEventListener("DOMContentLoaded", function () {
    var csrftoken = getCookie('csrftoken');
    var tables = document.querySelectorAll('.drop');
    var startRow;
    var startTable;
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
        startRow = e.target;   // remember start drag row
        startTable = startRow.offsetParent.offsetParent;
        curDragOverTable = startTable;
        makeTableBackgroundBigger();
    }

    function makeTableBackgroundBigger() {
        tables.forEach(function (table) {
            if (table != startTable) {
                var position = table.getBoundingClientRect();
                var windowHeight = document.documentElement.clientHeight;
                var additionalHeight = windowHeight - position.top;
                //check need to prevent sub-scroll bar thru table borders
                if (additionalHeight > table.clientHeight) {
                    table.style.height = additionalHeight + 'px';
                }
                table.classList.add('over');
            }
        });
    }

     // remark tables borders over drag
    function handleDragEnter(e) {
        tables.forEach(function (table) {
            // mark hover table
            if (table.contains(e.target) && table != curDragOverTable &&
                table != startTable) {
                curDragOverTable.classList.remove('over');
                curDragOverTable = table;
                curDragOverTable.classList.add('over');
            } else {
                // unmark borders of 3rd table in first hover
                if (!startTable.contains(e.target) &&
                    table != curDragOverTable) {
                    table.classList.remove('over');
                }
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
            table.style.height = '';
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
                if (table != startTable && table.contains(e.target)) {
                    makePost(table.children[0]);
                }
            }
        );
        return false;
    }

    function makePost(table) {
        var xhr = new XMLHttpRequest();
        var body = 'table=' + encodeURIComponent(table.dataset['issuetype']) +
            '&id=' + encodeURIComponent(startRow.dataset['id']);
        xhr.open("POST", '/project/issue_push/', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    // make change in page on post 200
                    remakePage(table);
                } else {
                    alert("Push hasn't taken effect!")
                }
            }
        };
        xhr.send(body);
    }

    function remakePage(table) {
        var tableBody = table.getElementsByTagName('tbody')[0];
        var rows = tableBody.children;
        if (!rows.length) {
            tableBody.append(startRow);
        } else {
            for (var i = 0; i < rows.length; i++) {
                if (rows[i].dataset['id'] > startRow.dataset['id']) {
                    tableBody.insertBefore(startRow, tableBody.children[i]);
                    return
                }
            }
            tableBody.append(startRow);
        }
    }
});
