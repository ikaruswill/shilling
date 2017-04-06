var title = "";
var chartData = [];
var dates = [];
var labels = [];
var earliestTime = getEarliestTime(option);

if (option === "lastDay") {
    title = "Past Day's Expenditure";
} else if (option === "lastWeek") {
    title = "Past Week's Epxenditure";
} else if (option === "lastMonth") {
    title = "Past Month's Expenditure";
}

//Sort data by transaction.date
data = _.sortBy(data, function(transaction){ return transaction.date; });

//Get sum of transaction of each day
_.each(data, function(transaction, index, transactions) {
    if (transaction.date >= earliestTime) {
        var index = _.findIndex(dates, function(date) { return date === transaction.date; });
        if (index > -1) {
            chartData[index] -= transaction.amount;
        } else {
            chartData.push(transaction.amount * -1);
            dates.push(transaction.date);
        }
    }
});

//Push data for chart's x-axis labels
for (var day = 0; day < dates.length; day++) {
    labels.push('Day ' + day);
}

var ctx = document.getElementById("chart2Vis").getContext("2d");
ctx.canvas.width = 300;
ctx.canvas.height = 300;

if (myLineChart !== undefined) {
    myLineChart.destroy();
}

var myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [
            {
                fill: false,
                lineTension: 0.1,
                backgroundColor: "rgba(75,192,192,0.4)",
                borderColor: "rgba(75,192,192,1)",
                borderCapStyle: 'butt',
                borderDash: [],
                borderDashOffset: 0.0,
                borderJoinStyle: 'miter',
                pointBorderColor: "rgba(75,192,192,1)",
                pointBackgroundColor: "#fff",
                pointBorderWidth: 1,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(75,192,192,1)",
                pointHoverBorderColor: "rgba(220,220,220,1)",
                pointHoverBorderWidth: 2,
                pointRadius: 1,
                pointHitRadius: 10,
                data: chartData,
                spanGaps: false,
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