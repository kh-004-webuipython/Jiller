document.addEventListener("DOMContentLoaded", function () {
    var csrftoken = getCookie('csrftoken');
    var tables = document.querySelectorAll('.drop');
    var startRow;
    var startTable;

    tables.forEach(
        function (table) {
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
