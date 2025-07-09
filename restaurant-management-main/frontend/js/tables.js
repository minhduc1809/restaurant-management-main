document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/banan/')  // 👈 Đúng route
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#tableTable tbody');
      tbody.innerHTML = '';
      data.forEach(table => {
        const row = `
          <tr>
            <td>${table.BanAnID}</td>
            <td>${table.SoBan}</td>
            <td>${table.TrangThai}</td>
          </tr>
        `;
        tbody.innerHTML += row;
      });
    })
    .catch(error => {
      console.error('Lỗi khi tải danh sách bàn:', error);
    });
});
