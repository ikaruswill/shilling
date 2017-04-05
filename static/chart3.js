var title = "Past day's expenditure";
var earliestTime = getEarliestTime(option);

if (option === "lastWeek") {
    title = "Past week's expenditure";
} else if (option === "lastMonth") {
    title = "Past month's expenditure"
}

$("#table tbody tr").remove();

_.each(data, function(transaction, index, transactions) {
    if (transaction.date >= earliestTime) {
        $("#table tbody").append('<tr><td>' + transaction.amount * -1 +
                                 '</td><td>' + transaction.category_id +
                                 '</td><td>' + transaction.item + '</td></tr>');
    }
});