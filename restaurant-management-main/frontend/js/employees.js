document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('searchEmployee');
  input.addEventListener('input', () => {
    const filter = input.value.toLowerCase();
    document.querySelectorAll('#employeeTable tbody tr').forEach(row => {
      const name = row.cells[1].textContent.toLowerCase();
      row.style.display = name.includes(filter) ? '' : 'none';
    });
  });
});