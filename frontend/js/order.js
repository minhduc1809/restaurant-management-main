ocument.addEventListener('DOMContentLoaded', () => {
  const select = document.querySelectorAll('.menu-item');
  const tableBody = document.querySelector('#orderTable tbody');
  const totalEl = document.getElementById('totalAmount');

  let total = 0;

  document.querySelectorAll('.add-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      const name = row.querySelector('.item-name').textContent;
      const price = parseFloat(row.querySelector('.item-price').textContent);
      const qty = parseInt(row.querySelector('.item-qty').value);

      const lineTotal = price * qty;
      total += lineTotal;

      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${name}</td><td>${qty}</td><td>${price}</td><td>${lineTotal}</td>`;
      tableBody.appendChild(tr);

      totalEl.textContent = total.toFixed(2);
    });
  });
});