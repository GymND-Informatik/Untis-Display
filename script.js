$(document).ready(function() {
    var table = $('#scroll-table');
    var originalTableBody = table.find('tbody').first();
    var clonedTableBody = originalTableBody.clone();
    var divider = $('<div class="divider"></div>');
    table.append(clonedTableBody);
    table.append(divider);

    var scrollSpeed = 1;
    var scrollInterval = 65;
    //
    // setInterval(function () {
    //     var scrollTop = table.scrollTop();
    //     var scrollHeight = table.prop('scrollHeight');
    //     var visibleHeight = table.height();
    //
    //     // Check if the scroll has reached near the end of the cloned table body
    //     if (scrollTop + visibleHeight >= scrollHeight - 20) {
            var newClonedBody = originalTableBody.clone();
            var newDivider = divider.clone();
            table.append(newClonedBody);
            table.append(newDivider);
    //     }
    //
    //     table.animate()
    //
    // }, scrollInterval);
    let counter = 1;
    function FilipStupid() {
        table.animate({
            scrollTop: table.height() * (counter++)
        }, 40000, 'linear', () => {
            var newClonedBody = originalTableBody.clone();
            var newDivider = divider.clone();
            table.append(newClonedBody);
            table.append(newDivider);
            console.log("added new element")
        });
        FilipStupid();

    }
    FilipStupid();


});

function isPositionStickySupported() {
    var testElement = document.createElement('div');
    testElement.style.position = 'sticky';
    return testElement.style.position === 'sticky';
}

if (isPositionStickySupported()) {
    console.log('position: sticky is supported');
    // Add a class or perform some action
} else {
    console.log('position: sticky is not supported');
    // Fallback or other actions
}

