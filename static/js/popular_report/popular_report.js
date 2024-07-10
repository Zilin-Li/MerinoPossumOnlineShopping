document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('myChart').getContext('2d');
    const reportData = JSON.parse(document.getElementById('reportData').textContent);
    
    const labels = reportData.map(item => item[0]);
    const quantityData = reportData.map(item => item[2]);
    const salesRevenueData = reportData.map(item => item[1]);

    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quantity',
                data: quantityData,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    document.getElementById('metric').addEventListener('change', function() {
        const metric = this.value;
        const data = metric === 'quantity' ? quantityData : salesRevenueData;
        const label = metric === 'quantity' ? 'Quantity' : 'Sales Revenue';

        myChart.data.datasets[0].data = data;
        myChart.data.datasets[0].label = label;
        myChart.update();
    });
});



  
