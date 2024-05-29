$(document).ready(function() {
    var table = $('#scroll-table');
    var originalTableBody = table.find('tbody').first();
    var clonedTableBody = originalTableBody.clone();
    var divider = $('<div class="divider"></div>');
    table.append(clonedTableBody);
    table.append(divider);

    var scrollSpeed = 0.5;
    var scrollInterval = 35;

    setInterval(function () {
        var scrollTop = table.scrollTop();
        var scrollHeight = table.prop('scrollHeight');
        var visibleHeight = table.height();

        // Check if the scroll has reached near the end of the cloned table body
        if (scrollTop + visibleHeight >= scrollHeight - 20) {
            var newClonedBody = originalTableBody.clone();
            var newDivider = divider.clone();
            table.append(newClonedBody);
            table.append(newDivider);
        }

        table.scrollTop(scrollTop + scrollSpeed);

    }, scrollInterval);
});

