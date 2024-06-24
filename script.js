document.addEventListener('DOMContentLoaded', function() {
    
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

    var table = document.getElementById('scroll-table');
    var originalTableBody = table.querySelector('tbody');
    var divider = document.createElement('div');
    divider.className = 'divider';
    
    function _scroll() {
        // Determine the height of the first cell in the table header
        var rect = table.querySelector('thead tr').children[0].getBoundingClientRect();
        var topElement = document.elementFromPoint(rect.left + 1, rect.bottom + 1);
        var scrollAmount = topElement.getBoundingClientRect();
        var backupScrollTop = table.scrollTop;
        table.scrollTop += scrollAmount.height;

        // console.log(scrollAmount.height);
        // Check if the table has reached the bottom
        if (table.scrollTop >= table.scrollHeight - table.clientHeight) {
            table.scrollTop = backupScrollTop;
            // Clone the original table body and append it to the table
            var newClonedBody = originalTableBody.cloneNode(true);
            table.appendChild(newClonedBody);
        }
    }

    function startScroll() {
        _scroll(); // Initial scroll
        setInterval(_scroll, 5000); // Set interval for periodic scrolling
    }

    // Call startScroll() to initiate scrolling
    startScroll();
});



