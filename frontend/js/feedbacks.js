document.addEventListener('DOMContentLoaded', () => {
  fetchFeedbacks();
});

function fetchFeedbacks() {
  fetch('/api/feedbacks')
    .then(res => res.json())
    .then(data => renderFeedbacks(data))
    .catch(err => console.error('Lỗi khi tải phản hồi:', err));
}

function renderFeedbacks(feedbacks) {
  const tbody = document.querySelector('#feedbackTable tbody');
  tbody.innerHTML = '';

  feedbacks.forEach(fb => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${fb.PhanHoiID}</td>
      <td>${fb.HoTenKhachHang || fb.KhachHangID}</td>
      <td>${fb.NoiDung}</td>
      <td>${fb.DiemDanhGia || '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}
