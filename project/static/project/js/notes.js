document.addEventListener("DOMContentLoaded", function () {
    var notewindow = document.getElementById('notes');
    var notes = document.querySelectorAll('.note');
    var openedNote;
    /*titleNotes.forEach(function (title) {
        title.addEventListener('click', openNote, false);
    });
    document.querySelectorAll('.note-title').forEach(function (title) {
        title.addEventListener('click', openNote, false);
    });*/
    // on click hide other notes, and open current
    notes.forEach(function (title) {
        title.onclick = function(e) {
            openedNote = this;
            console.log (this);/*
            notes.forEach(function (note) {
                if (openedNote != note) {
                    note.offsetParent.style.width = '54%';
                    note.offsetParent.style.height = '500px';
                    note.offsetParent.focus();
                    note.style.width = '100%';
                    note.style.height = '100%';
                }
            });*/
            openNote(openedNote);
        }

    });


    function openNote(note) {
        /*note.offsetParent.style.width = '54%';
        note.offsetParent.style.height = '500px';
        note.style.width = '100%';
        note.style.height = '100%';

*/

        console.log();

    }

});

/*

$(document).ready(function() {
    notes = $("#notes"); // get references to the 'notes' list
    // clicking the 'New Note' button adds a new note to the list
    $("#btnNew").click(function() {
        addNewNote();
    });
});

//  adds a new note to the 'notes' list
function addNewNote(title, content) {

    // add a new note to the end of the list
    notes.append("<li><div class='note'>" +
        "<textarea class='note-title text-center' disabled maxlength='50'/>" +
        "<textarea class='note-content' maxlength='5000'/>" +
        //"<img class='hide' src='http://iconizer.net/files/Shimmer_Icons/thumb/128/delete.png'/>" +
        "</div></li>");
//""
    // get the new note that's just been added and attach the click event handler to its close button
    var newNote = notes.find("li:last");
    newNote.find("img").click(function() {
        newNote.remove();
    });

    // hook up event handlers to show/hide close button as appropriate
    addNoteEvent(newNote);
    // if a title is provided then set the title of the new note
    if (title) {
        // get the title textarea element and set its value
        newNote.find("textarea.note-title").val(title);
    }

    // if a content is provided then set the content of the new note
    if (content) {
        // get the content textarea element and set its value
        newNote.find("textarea.note-content").val(content);
    }
}

function addNoteEvent(noteElement) {
    noteElement.focus(function () {
        $(this).find(".img").removeClass("hide");
    }).hover(function() {
        $(this).find("img").removeClass("hide");
    }, function () {
        $(this).find("img").addClass("hide");
    });
}











/*


$(document).ready(function() {
    notes = $("#notes"); // get references to the 'notes' list
    // clicking the 'New Note' button adds a new note to the list
    $("#btnNew").click(function() {
        addNewNote();
    });
});

//  adds a new note to the 'notes' list
function addNewNote(title, content) {

    // add a new note to the end of the list
    notes.append("<li><div>" +
                 "<textarea class='note-title text-center' placeholder='Empty' maxlength='50'/>" +
                 "<textarea class='note-content'/>" +
                  +
                 "</div></li>");
//"<img class='hide' src='http://iconizer.net/files/Shimmer_Icons/thumb/128/delete.png'/>"
    // get the new note that's just been added and attach the click event handler to its close button
    var newNote = notes.find("li:last");
    newNote.find("img").click(function() {
        newNote.remove();
    });

    // hook up event handlers to show/hide close button as appropriate
    addNoteEvent(newNote);
    // if a title is provided then set the title of the new note
    if (title) {
        // get the title textarea element and set its value
        newNote.find("textarea.note-title").val(title);
    }

    // if a content is provided then set the content of the new note
    if (content) {
        // get the content textarea element and set its value
        newNote.find("textarea.note-content").val(content);
    }
}

function addNoteEvent(noteElement) {
    noteElement.focus(function () {
        $(this).find(".img").removeClass("hide");
    }).hover(function() {
        $(this).find("img").removeClass("hide");
    }, function () {
        $(this).find("img").addClass("hide");
    });
}



*/