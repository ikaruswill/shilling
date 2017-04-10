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
    	var inOrOut = transaction.amount < 0 ? 'Out' : 'In';
    	var amount = transaction.amount < 0 ? transaction.amount * -1 : transaction.amount;
        $("#table tbody").append('<tr><td>' + amount +
                                 '</td><td>' + transaction.category_id +
                                 '</td><td>' + transaction.item + 
                                 '</td><td class="' + inOrOut + '">' + inOrOut + '</td></tr>');
    }
});