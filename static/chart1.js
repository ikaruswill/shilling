var chart1Data = data; //TODO: Parse this to proper format for visualisation
var chart1Option = option; //[weekly|monthly|yearly]

var ctx = document.getElementById("chart1Vis").getContext("2d");

var myDoughnutChart = new Chart(ctx, {
    type: 'doughnut',
    data : {
        labels: [
            "Red",
            "Blue",
            "Yellow"
        ],
        datasets: [
            {
                data: [300, 50, 100],
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
        responsive: true
    }
});