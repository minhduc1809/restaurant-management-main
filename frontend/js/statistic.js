document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('revenueChart').getContext('2d');
  fetch('/api/statistic/')
    .then(res => res.json())
    .then(data => {
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Doanh thu theo tháng',
            data: data.revenue,
            backgroundColor: '#4caf50'
          }]
        },
        options: {
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    });
});