document.addEventListener("DOMContentLoaded", function () {
    var TIME_BEFORE_SAVE = 2000;
    var csrftoken = getCookie('csrftoken');
    var notes = document.querySelector('.notes');
    var noteQuery = document.querySelectorAll('.note');
    var openedNote;

    // event on button to create new notes
    document.getElementById('btnNew').addEventListener('click', function () {
        addNewNote();
    });

    // make openNote smalle on offset clicks
    window.addEventListener('click', cancelSize, false);

    function cancelSize(e) {
        if (openedNote && e.target != openedNote &&
            !openedNote.contains(e.target)) {
            openedNote.removeAttribute('id');
            openedNote.lastElementChild.classList.add('hide');
        }
    }

    // add event handlers on all notes
    noteQuery.forEach(function (note) {
        addNoteEvents(note);
    });

    function addNoteEvents(note) {

        // make notes bigger after click
        note.onclick = function () {
            noteQuery.forEach(function (note) {
                note.removeAttribute('id');
                note.lastElementChild.classList.add('hide');
            });
            openedNote = this;
            this.id = ('clicked');
            this.lastElementChild.classList.remove('hide');
        };

        // send data to server after changing text
        note.children[0].addEventListener('input', function () {
            sendData(note);
        });
        note.children[1].addEventListener('input', function () {
            sendData(note);
        });

        // delete note event
        note.lastElementChild.addEventListener('click', function () {
            var xhrd = new XMLHttpRequest();
            var body = 'id=' + encodeURIComponent(note.dataset['id']);
            xhrd.open("DELETE", '/project/' + notes.dataset['pr'] + '/note/',
                true);
            xhrd.setRequestHeader('Content-Type',
                'application/x-www-form-urlencoded');
            xhrd.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhrd.onreadystatechange = function () {
                if (xhrd.readyState == 4 && xhrd.status == 200) {
                    // TODO confirm
                    note.remove();
                }
            };
            xhrd.send(body);
        });
    }

    // send data only if data will not be changed in next few seconds
    var sendInterval;

    function sendData(note) {
        stopSend();
        sendInterval = setTimeout(sendToServer, TIME_BEFORE_SAVE);

        function stopSend() {
            clearTimeout(sendInterval);
        }

        function sendToServer() {
            var xhr = new XMLHttpRequest();
            var body = 'id=' + encodeURIComponent(note.dataset['id']) +
                '&title=' + encodeURIComponent(note.children[0].value) +
                '&content=' + encodeURIComponent(note.children[1].value);
            xhr.open("POST", '/project/' + notes.dataset['pr'] + '/note/',
                true);
            xhr.setRequestHeader('Content-Type',
                'application/x-www-form-urlencoded');
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    if (!note.dataset['id']) {
                        note.dataset['id'] = xhr.getResponseHeader('note_id');
                    }
                    //TODO: show that data is saved
                }
            };
            xhr.send(body);
        }
    }

    //  adds a new note to the 'notes' list
    function addNewNote() {
        // add a new note to the end of the list
        var newNote = document.createElement('div');
        newNote.className = 'note';
        newNote.innerHTML = "<textarea class='note-title center" +
            "text-center' maxlength='15'></textarea>" +
            "<textarea class='note-content text-justify' " +
            "maxlength='5000'></textarea>" +
            "<div class='hide'><span class='glyphicon glyphicon-trash'>" +
            "</span></div>";
        notes.appendChild(newNote);
        addNoteEvents(newNote);

    }
});
