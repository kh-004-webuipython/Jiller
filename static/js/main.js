$( function() {
    $( "#sortable" ).sortable({
        items: 'tr.sortable-row',
        containment: "parent",
        delay: 200,
        opacity: 0.6,
        cursor: 'move',
        tolerance: 'pointer',
        forcePlaceholderSize: true
    });
    $( "#sortable" ).disableSelection();
} );