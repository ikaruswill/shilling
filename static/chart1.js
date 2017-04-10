var chartData = [];
var title = "Past day's expenditure";
var categoryList = getCategoryList(data);
var earliestTime = getEarliestTime(option);
var colors = ["#1abc9c", "#f1c40f", "#3498db", "#e74c3c", "#34495e", "#95a5a6",
              "#2ecc71", "#e67e22", "#9b59b6", "#16a085", "#f39c12", "#27ae60", 
              "#ecf0f1", "#d35400", "#2980b9", "#c0392b", "#8e44ad", "#bdc3c7"];

_.each(categoryList, function(category, index, categories) {
    var total = 0;
    _.each(data, function(transaction, index, transactions) {
        if (transaction.category_id === category && transaction.date >= earliestTime && transaction.amount < 0) {
            total -= transaction.amount;
        }
    });
    chartData.push(total);
});

if (option === "lastWeek") {
    title = "Past week's expenditure";
} else if (option === "lastMonth") {
    title = "Past month's expenditure"
}

if (myDoughnutChart !== undefined) {
    myDoughnutChart.destroy();
}

var ctx = document.getElementById("chart1Vis").getContext("2d");

ctx.canvas.width = 300;
ctx.canvas.height = 300;

var myDoughnutChart = new Chart(ctx, {
    type: 'doughnut',
    data : {
        labels: categoryList,
        datasets: [
            {
                data: chartData,
                backgroundColor: colors,
                hoverBackgroundColor: colors
            }
        ]
    },
    options: {
        responsive: false,
        legend: {
            display: false
        },
        title: {
            display: true,
            text: title
        }
    }
});