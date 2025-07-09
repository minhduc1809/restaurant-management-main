document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('searchSchedule');
  if (input) {
    input.addEventListener('input', () => {
      const filter = input.value.toLowerCase();
      document.querySelectorAll('#scheduleTable tbody tr').forEach(row => {
        const name = row.cells[1].textContent.toLowerCase();
        row.style.display = name.includes(filter) ? '' : 'none';
      });
    });
  }
});