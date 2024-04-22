$(document).ready(function() {
    var table = $('#scroll-table');
    var originalTableBody = table.find('tbody').first();
    var clonedTableBody = originalTableBody.clone();

    table.append(clonedTableBody);

    var scrollSpeed = 0.5;
    var scrollInterval = 40;

    setInterval(function () {
        var scrollTop = table.scrollTop();
        var scrollHeight = table.prop('scrollHeight');
        var visibleHeight = table.height();

        // Check if the scroll has reached near the end of the cloned table body
        if (scrollTop + visibleHeight >= scrollHeight - 20) {  // 20 is a small buffer to initiate before hitting the very bottom
            var newClonedBody = originalTableBody.clone();
            table.append(newClonedBody);
        }

        table.scrollTop(scrollTop + scrollSpeed);

    }, scrollInterval);
});
