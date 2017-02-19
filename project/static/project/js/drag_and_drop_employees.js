document.addEventListener("DOMContentLoaded", function () {
    var csrftoken = getCookie('csrftoken');
    var tables = document.querySelectorAll('[data-table]');
    var rows = document.querySelectorAll('[data-id]')
    var srcRow, srcTable;

    tables.forEach(
        function (table) {
            table.addEventListener('dragover', allowDrop);
            table.addEventListener('drop', drop);
        });

    rows.forEach(
        function (row) {
            row.addEventListener('dragstart', drag);
            row.addEventListener('drop', drop);
            row.addEventListener('dragend', drop);
        });

    function allowDrop(ev) {
        if (ev.preventDefault) {
            ev.preventDefault();
        }

        ev.dataTransfer.dropEffect = 'move';
        return false;
    }

    function drag(ev) {
        this.style.opacity = '0.4';
        srcRow = this;
        srcTable = srcRow.offsetParent;
        ev.dataTransfer.effectAllowed = 'move';
        ev.dataTransfer.setData("text/html", this);
    }

    function drop(ev) {
        if (ev.stopPropagation) {
            ev.stopPropagation(); // stops the browser from redirecting.
        }
        this.style.opacity = '1';

        if (! srcTable.contains(ev.target)) {
        tables.forEach(
            function (table) {
                 if (table != srcTable && table.contains(ev.target)) {
                    sendRow();
                }
            });
        }
    }

    function sendRow() {
    var xhttp;

    if (window.XMLHttpRequest){
        xhttp = new XMLHttpRequest();
    }
    else {
        xhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    var data = ''
    if (srcRow.offsetParent.dataset['table'] == 'table_cur') {
        data = 'remove'
    } else {
        data = 'add'
    }
    var url = "/project/" + String(srcRow.dataset['pr_id']) + "/" +
                            String(srcRow.dataset['id']) + "/" +
                            String(srcRow.dataset['team_id']) + "/change/";
    xhttp.open('POST', url, true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.setRequestHeader("X-CSRFTOKEN", csrftoken);
    xhttp.onreadystatechange=function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            location.reload();
        } else {
            alert('Error');
        }
    };
    xhttp.send(data);
    }
});


