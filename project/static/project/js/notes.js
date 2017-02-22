document.addEventListener("DOMContentLoaded", function () {
    var TIME_BEFORE_SAVE = 1000;
    var csrftoken = getCookie('csrftoken');
    var notes = document.querySelector('.notes');
    var noteQuery = document.querySelectorAll('.note');
    var openedNote;

    // event on button to create new notes
    document.getElementById('btnNew').addEventListener('click', function () {
        addNewNote();
    });

    // make openNote smaller on offset clicks
    window.addEventListener('click', cancelSize, false);

    function cancelSize(e) {
        if (openedNote && e.target != openedNote &&
            !openedNote.contains(e.target)) {
            openedNote.removeAttribute('id');
            openedNote.lastElementChild.classList.add('hide');
            openedNote.getElementsByClassName('fileUpload')[0].classList.add('hide');
            openedNote.getElementsByClassName('note-picture')[0].classList.add('hide');
        }
    }

    // add event handlers on all notes
    noteQuery.forEach(function (note) {
        addNoteEvents(note);
    });

    function addNoteEvents(note) {

        // make notes stay bigger after click
        note.onclick = function () {
            noteQuery.forEach(function (note) {
                note.removeAttribute('id');
                note.lastElementChild.classList.add('hide');
                note.getElementsByClassName('fileUpload')[0].classList.add('hide');
                note.getElementsByClassName('note-picture')[0].classList.add('hide');
            });

            openedNote = this;
            this.id = ('clicked');
            //show trash button
            this.lastElementChild.classList.remove('hide');
            this.lastElementChild.classList.remove('hide');
            this.getElementsByClassName('fileUpload')[0].classList.remove('hide');
            this.getElementsByClassName('note-picture')[0].classList.remove('hide');
/*
            // makes content height depend from content lines
            var content = this.getElementsByClassName('content-text')[0];
            console.log(content.innerText);
            var textareaRows = content.innertext.split("\n");
            if(textareaRows[0] != "undefined" && textareaRows.length
                >= content.rows) {
                content.rows = textareaRows.length + 5;
            }*/
        };

        // send data to server after changing text
        note.getElementsByClassName('note-title')[0].addEventListener('input', function () {
            sendData(note);
        });
        note.getElementsByClassName('note-content')[0].addEventListener('input', function () {
            sendData(note);
        });
         note.getElementsByClassName('note-upload')[0].addEventListener('input', function () {
            sendPicture(note);
        });

        // delete note event
        note.lastElementChild.addEventListener('click', function () {
            if (!note.dataset['id']){
                note.remove();
            } else {
                var xhrd = new XMLHttpRequest();
                var body = 'id=' + encodeURIComponent(note.dataset['id']);
                xhrd.open("DELETE", '/project/' + notes.dataset['pr'] +
                    '/note/', true);
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
            }
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
            var title = note.getElementsByClassName('note-title')[0];
            var content = note.getElementsByClassName('content-text')[0];
            var formData = new FormData();
            formData.append("id", note.dataset['id']);
            formData.append("title",title.value);
            formData.append("content", content.innerText);
            xhr.open("POST", '/project/' + notes.dataset['pr'] + '/note/',
                true);
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    if (!note.dataset['id']) {
                        note.dataset['id'] = xhr.getResponseHeader('note_id');
                    }
                    //TODO: show that data is saved
                }
            };
            xhr.send(formData);
        }
    }

    function sendPicture(note){
        var file  = note.getElementsByClassName('note-upload')[0].files[0];
        if (file) {
            var xhr = new XMLHttpRequest();
            var title = note.getElementsByClassName('note-title')[0];
            var content = note.getElementsByClassName('note-content')[0];
            var formData = new FormData();
            formData.append("title",title.value);
            formData.append("content",content.innerText);
            formData.append("picture", file);
            formData.append("id", note.dataset['id']);
            xhr.open("POST", '/project/' + notes.dataset['pr'] + '/note/', true);
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    if (!note.dataset['id']) {
                        note.dataset['id'] = xhr.getResponseHeader('note_id');
                    }
                    location.reload();
                    //TODO: show that data is saved
                }
            };
            xhr.send(formData);
        }
    }



    //  adds a new note to the 'notes' list
    function addNewNote() {
        // add a new note to the end of the list
        var newNote = document.createElement('div');
        newNote.className = 'note center';
        newNote.innerHTML = "<textarea class='note-title" +
            " text-center' maxlength='25' rows='1'></textarea>" +
            "<textarea class='note-content text-justify'" +
            " maxlength='5000' rows='20'></textarea>" +
            "<div class='hide'><span class='glyphicon glyphicon-trash'>" +
            "</span></div>";
        notes.appendChild(newNote);
        noteQuery = document.querySelectorAll('.note');
        addNoteEvents(newNote);
    }
});
