// DASHBOARD MONTHLY CHART
document.addEventListener("DOMContentLoaded", function () {
    const chartElement = document.getElementById("visitsChart");

    if (chartElement) {
        const monthlyCounts = JSON.parse(chartElement.dataset.monthly);

        new Chart(chartElement, {
            type: 'line',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [{
                    label: 'Monthly Visits',
                    data: monthlyCounts,
                    borderWidth: 3,
                    borderColor: "#4e73df",
                    backgroundColor: "rgba(78, 115, 223, 0.1)",
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });cl
    }
});
