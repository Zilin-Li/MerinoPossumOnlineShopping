// document.addEventListener('DOMContentLoaded', function() {
    // alert('delivery_info.js loaded');
    // Highlight table rows on hover
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            row.classList.add('highlight');
        });
        row.addEventListener('mouseleave', function() {
            row.classList.remove('highlight');
        });
    });
// });



