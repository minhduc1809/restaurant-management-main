document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('searchReservation');
  input.addEventListener('input', () => {
    const filter = input.value.toLowerCase();
    document.querySelectorAll('#reservationTable tbody tr').forEach(row => {
      const customer = row.cells[1].textContent.toLowerCase();
      const phone = row.cells[2].textContent.toLowerCase();
      row.style.display = customer.includes(filter) || phone.includes(filter) ? '' : 'none';
    });
  });
});