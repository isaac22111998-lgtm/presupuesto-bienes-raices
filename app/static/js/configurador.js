document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('configForm');
  if (!form) return;

  const itemsJsonInput = document.getElementById('itemsJson');
  const supervisionCb = document.getElementById('supervision');
  const contingencyCb = document.getElementById('contingency');

  function fmtMXN(n) {
    return '$' + Math.round(n).toLocaleString('es-MX');
  }

  function getSelectedItems() {
    const items = [];
    document.querySelectorAll('.component-card').forEach(card => {
      const cb = card.querySelector('.comp-checkbox');
      if (!cb || (!cb.checked && !cb.disabled)) return;
      if (cb.disabled && !cb.checked) return;
      const id = parseInt(card.dataset.compId);
      const qty = parseInt(card.querySelector('.qty-input').value, 10) || 1;
      const price = parseFloat(card.dataset.price);
      items.push({ id, qty, price });
    });
    return items;
  }

  function updateTotals() {
    const items = getSelectedItems();
    let subtotal = 0;
    const catTotals = {};

    items.forEach(item => {
      const card = document.querySelector(`.component-card[data-comp-id="${item.id}"]`);
      if (!card) return;
      const sub = item.price * item.qty;
      subtotal += sub;

      // update component subtotal display
      const display = card.querySelector('.comp-subtotal-display');
      if (display) display.textContent = fmtMXN(sub);

      const catId = card.dataset.cat;
      catTotals[catId] = (catTotals[catId] || 0) + sub;
    });

    // Update category badges
    Object.entries(catTotals).forEach(([catId, total]) => {
      const badge = document.querySelector(`.cat-subtotal[data-cat="${catId}"]`);
      if (badge) badge.textContent = fmtMXN(total);
    });
    // Zero out categories with no selection
    document.querySelectorAll('.cat-subtotal').forEach(badge => {
      const catId = badge.dataset.cat;
      if (!catTotals[catId]) badge.textContent = '$0';
    });

    const supervision = supervisionCb && supervisionCb.checked ? subtotal * 0.15 : 0;
    const contingency = contingencyCb && contingencyCb.checked ? subtotal * 0.10 : 0;
    const total = subtotal + supervision + contingency;

    document.getElementById('subtotalDisplay').textContent = fmtMXN(subtotal);
    document.getElementById('supervisionDisplay').textContent = fmtMXN(supervision);
    document.getElementById('contingencyDisplay').textContent = fmtMXN(contingency);
    document.getElementById('totalDisplay').textContent = fmtMXN(total);

    const supervisionRow = document.getElementById('supervisionRow');
    const contingencyRow = document.getElementById('contingencyRow');
    if (supervisionRow) supervisionRow.style.display = supervision > 0 ? '' : 'none';
    if (contingencyRow) contingencyRow.style.display = contingency > 0 ? '' : 'none';

    // Category summary in panel
    const summary = document.getElementById('categorySummary');
    if (summary) {
      const lines = Object.entries(catTotals)
        .filter(([, v]) => v > 0)
        .map(([catId, total]) => {
          const badge = document.querySelector(`.cat-subtotal[data-cat="${catId}"]`);
          const headerEl = badge ? badge.closest('.card-header') : null;
          const name = headerEl ? headerEl.querySelector('span')?.textContent?.trim().replace(/^\S+\s*/, '') || '' : '';
          return `<div class="d-flex justify-content-between"><span class="text-muted">${name}</span><span>${fmtMXN(total)}</span></div>`;
        });
      summary.innerHTML = lines.slice(0, 6).join('');
      if (lines.length > 6) summary.innerHTML += `<div class="text-muted text-center small">+${lines.length - 6} más...</div>`;
    }

    // Store JSON for form submission
    itemsJsonInput.value = JSON.stringify(
      items.map(i => ({ id: i.id, qty: i.qty }))
    );
  }

  // Handle checkbox toggle
  document.querySelectorAll('.comp-checkbox').forEach(cb => {
    if (!cb.disabled) {
      cb.addEventListener('change', function () {
        const card = this.closest('.component-card');
        const group = card.dataset.group;

        if (this.checked && group) {
          // Uncheck others in same group
          document.querySelectorAll(`.component-card[data-group="${group}"]`).forEach(otherCard => {
            if (otherCard !== card) {
              const otherCb = otherCard.querySelector('.comp-checkbox');
              if (otherCb && !otherCb.disabled) {
                otherCb.checked = false;
                otherCard.classList.remove('selected');
              }
            }
          });
        }

        card.classList.toggle('selected', this.checked);
        updateTotals();
      });
    }
  });

  // Click on card toggles checkbox (if not disabled)
  document.querySelectorAll('.component-card').forEach(card => {
    card.addEventListener('click', function (e) {
      if (e.target.closest('.qty-control') || e.target.closest('.comp-check')) return;
      const cb = this.querySelector('.comp-checkbox');
      if (cb && !cb.disabled) {
        cb.checked = !cb.checked;
        cb.dispatchEvent(new Event('change'));
      }
    });
  });

  // Quantity buttons
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const id = this.dataset.id;
      const input = document.getElementById(`qty-${id}`);
      if (!input) return;
      let val = parseInt(input.value, 10) || 1;
      if (this.classList.contains('qty-plus')) val = Math.min(val + 1, 10000);
      else val = Math.max(val - 1, 1);
      input.value = val;
      updateTotals();
    });
  });

  // Quantity input changes — force integers only
  document.querySelectorAll('.qty-input').forEach(input => {
    input.addEventListener('input', function () {
      let val = parseInt(this.value, 10);
      if (isNaN(val) || val < 1) val = 1;
      this.value = val;
      updateTotals();
    });
    input.addEventListener('click', e => e.stopPropagation());
  });

  // Supervision / contingency toggles
  if (supervisionCb) supervisionCb.addEventListener('change', updateTotals);
  if (contingencyCb) contingencyCb.addEventListener('change', updateTotals);

  // Mark required cards as selected visually
  document.querySelectorAll('.component-card[data-required="true"]').forEach(card => {
    card.classList.add('selected');
  });

  // Smooth scroll to category via nav (optional keyboard shortcut)
  document.querySelectorAll('.cat-subtotal').forEach(badge => {
    badge.style.cursor = 'pointer';
    badge.addEventListener('click', function () {
      const catId = this.dataset.cat;
      const section = document.getElementById(`cat-${catId}`);
      if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // Form submit validation
  form.addEventListener('submit', function (e) {
    const items = getSelectedItems();
    if (items.length === 0) {
      e.preventDefault();
      alert('Selecciona al menos un componente para continuar.');
    }
  });

  // Initial render
  updateTotals();
});
