$(document).ready(function() {
    var table = $('#scroll-table');
    var originalTableBody = table.find('tbody').first();
    var clonedTableBody = originalTableBody.clone();

    // Append the cloned table body to the table for a seamless loop
    table.append(clonedTableBody);

    var scrollSpeed = 0.5;  // Speed of scrolling, adjust as needed
    var scrollInterval = 40;  // Interval of scrolling in milliseconds, adjust for smoothness

    setInterval(function () {
        var scrollTop = table.scrollTop();
        var scrollHeight = table.prop('scrollHeight');
        var visibleHeight = table.height();

        // Check if the scroll has reached near the end of the cloned table body
        if (scrollTop + visibleHeight >= scrollHeight - 20) {  // 20 is a small buffer to initiate before hitting the very bottom
            // Clone and append again before reaching the end
            var newClonedBody = originalTableBody.clone();
            table.append(newClonedBody);
        }

        // Smoothly scroll without resetting
        table.scrollTop(scrollTop + scrollSpeed);

    }, scrollInterval);
});
