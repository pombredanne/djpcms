
module("tablesorter");

function createble(cols) {
    var cols = cols || 5,
        rows = rows || 20,
        el = $('#testcontainer').html('').append($('<table>').append('<thead>').append('<tbody>'));
    return el;
}

test("$.tablesorter", function() {
    var el = createble();
});

