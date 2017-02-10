moveProgressBar();
// on browser resize...
$(window).resize(function() {
    moveProgressBar();
});

// SIGNATURE PROGRESS
function moveProgressBar() {
    var items = document.querySelectorAll('.progress-wrap');
    $.each(items, function(index, value) {
        var getPercent = ($(value).data('progress-percent') / 100);
        var getProgressWrapWidth = $('.progress-wrap').width();
        var progressTotal = getPercent * getProgressWrapWidth;
        var animationLength = 2500;

        // on page load, animate percentage bar to data percentage length
        // .stop() used to prevent animation queueing
        $(value.firstElementChild).stop().animate({
            left: progressTotal
        }, animationLength);
    })
}