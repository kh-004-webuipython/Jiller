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

    // add event handlers on all exist notes
    noteQuery.forEach(function (note) {
        addNoteEvents(note);
    });

    // make openNote smaller on offset clicks
    window.addEventListener('click', cancelSize, false);


    //  adds a new note to the 'notes' list
    function addNewNote() {
        // add a new note to the end of the list
        var newNote = document.createElement('div');
        newNote.className = 'note center';
        newNote.innerHTML =
            "<div class='fileUpload btn btn-link hide'>" +
            "<span>Add picture</span>" +
            "<input type='file' name='picture' class='note-upload'/></div>" +
            "<textarea class='note-title" +
            " text-center' maxlength='25' rows='1'></textarea>" +
            "<div class='note-content' contenteditable='true'" +
            " maxlength='10000'>" +
            "<img class='note-picture hide' src='' draggable='false'></div>" +
            "<div class='trash hide'>" +
            "<span class='glyphicon glyphicon-trash'></span></div>";
        notes.appendChild(newNote);
        noteQuery = document.querySelectorAll('.note');
        addNoteEvents(newNote);
    }


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
            this.getElementsByClassName('fileUpload')[0].classList.remove('hide');
            var image = this.getElementsByClassName('note-picture')[0];
            image.classList.remove('hide');
            image.onclick = function () {
                image.classList.toggle('big-image');
            }
        };







        // remember old data for future checks to prevent overwriting data
        note.oldText= {};
        var title = note.getElementsByClassName('note-title')[0];
        var content = note.getElementsByClassName('note-content')[0];
        note.oldText['title'] = title.value;
        note.oldText['content'] = content.innerText;

        // send data to server after changing text
        title.addEventListener(
            'input', function () {
                console.log(note.getElementsByClassName('note-title')[0].value);
                console.log(note.oldText['title']);
                console.log(note.oldText['content']);
                sendData(note);
        });

        content.addEventListener(
            'input', function () {
                console.log(note.getElementsByClassName('note-title')[0].innerText);
                console.log(note.oldText['title']);
                console.log(note.oldText['content']);
                sendData(note);
        });

         note.getElementsByClassName('note-upload')[0].addEventListener(
             'change', function () {
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
                    if (xhrd.readyState == 4) {
                        if (xhrd.status == 200) {
                            note.remove();
                        } else {
                            alert("Error, this note hasn't been deleted!")
                        }
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
            var content = note.getElementsByClassName('note-content')[0];
            var formData = new FormData();
            formData.append("id", note.dataset['id']);
            formData.append("title",title.value);
            formData.append("oldTitle", note.oldText['title']);
            formData.append("content", content.innerText);
            formData.append("oldContent", note.oldText['content']);
            xhr.open("POST", '/project/' + notes.dataset['pr'] + '/note/',
                true);
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        note.oldText['title'] = title.value;
                        note.oldText['content'] = content.innerText;
                        if (!note.dataset['id']) {
                            note.dataset['id'] = xhr.getResponseHeader('note_id');
                        }
                    } else {
                        if (xhr.getResponseHeader('refresh')) {
                            alert('Oops, someone has updated this note before you, please refresh page and then write new changes!')
                        } else {
                            alert("Error, this note hasn't been saved!")
                        }

                    }
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
            formData.append("oldTitle", note.oldText['title']);
            formData.append("content", content.innerText);
            formData.append("oldContent", note.oldText['content']);
            formData.append("picture", file);
            formData.append("id", note.dataset['id']);
            xhr.open("POST", '/project/' + notes.dataset['pr'] + '/note/', true);
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    note.oldText['title'] = title.value;
                    note.oldText['content'] = content.innerText;
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

    function cancelSize(e) {
        if (openedNote && e.target != openedNote &&
            !openedNote.contains(e.target)) {
            openedNote.removeAttribute('id');
            openedNote.lastElementChild.classList.add('hide');
            openedNote.getElementsByClassName('fileUpload')[0].classList.add('hide');
            openedNote.getElementsByClassName('note-picture')[0].classList.add('hide');
        }
    }
});
