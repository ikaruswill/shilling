var categoryList = getCategoryList(data);
var earliestTime = getEarliestTime(option);
var chartData = [];
_.each(categoryList, function(category, index, categories) {
    var total = 0;
    _.each(data, function(transaction, index, transactions) {
        if (transaction.category_id === category) {
            total -= transaction.amount;
        }
    });
    chartData.push(total);
});

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
                backgroundColor: [
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56"
                ],
                hoverBackgroundColor: [
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56"
                ]
            }
        ]
    },
    options: {
        responsive: false,
        legend: {
            display: false
         }
    }
});