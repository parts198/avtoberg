(function () {
  const state = {
    stores: [],
    orders: [],
    summary: null,
    filters: {
      store: '',
      date_from: '',
      date_to: '',
      schema: 'ALL',
      offer_id: '',
    },
  };

  const storeFilter = document.getElementById('store-filter');
  const dateFromFilter = document.getElementById('date-from-filter');
  const dateToFilter = document.getElementById('date-to-filter');
  const schemaFilter = document.getElementById('schema-filter');
  const offerIdFilter = document.getElementById('offer-id-filter');
  const applyButton = document.getElementById('apply-filters-btn');
  const resetButton = document.getElementById('reset-filters-btn');
  const refreshButton = document.getElementById('refresh-btn');
  const summaryContainer = document.getElementById('summary');
  const ordersBody = document.getElementById('orders-body');
  const emptyState = document.getElementById('empty-state');
  const totals = document.getElementById('totals');

  function formatMoney(v) {
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(Number(v || 0));
  }

  function formatDate(v) {
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? '-' : d.toLocaleString('ru-RU');
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  async function loadData() {
    state.filters.store = storeFilter.value;
    state.filters.date_from = dateFromFilter.value;
    state.filters.date_to = dateToFilter.value;
    state.filters.schema = schemaFilter.value;
    state.filters.offer_id = offerIdFilter.value.trim();

    const params = new URLSearchParams();
    Object.entries(state.filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    const response = await fetch(`/api/orders/dashboard-data/?${params.toString()}`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken') || '',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }

    const payload = await response.json();
    state.stores = payload.stores;
    state.orders = payload.orders;
    state.summary = payload.summary;
    renderFilters();
    renderSummary();
    renderOrders();
    renderTotals();
  }

  function renderFilters() {
    const selectedStore = state.filters.store;
    const options = ['<option value="">Все</option>']
      .concat(state.stores.map((s) => `<option value="${s.id}">${s.name}</option>`))
      .join('');
    storeFilter.innerHTML = options;
    storeFilter.value = selectedStore;
  }

  function renderSummary() {
    const summary = state.summary || {};
    const cards = [
      ['Всего заказов', summary.total_orders || 0],
      ['Всего позиций', summary.total_items || 0],
      ['Выручка', formatMoney(summary.total_revenue || 0)],
      ['Расходы', formatMoney(summary.total_expenses || 0)],
    ];
    summaryContainer.innerHTML = cards
      .map(([label, value]) => `<article class="summary-item"><div class="label">${label}</div><div class="value">${value}</div></article>`)
      .join('');
  }

  function buildItemsTable(items) {
    return `<table class="items-table"><thead><tr><th>Product ID</th><th>Offer ID</th><th>Название</th><th>Qty</th><th>Цена</th><th>Выручка</th><th>Расходы</th><th>Наценка факт</th></tr></thead><tbody>${items
      .map(
        (item) => `<tr>
          <td>${item.product_id || '-'}</td>
          <td>${item.offer_id || '-'}</td>
          <td>${item.product_name || '-'}</td>
          <td>${item.qty}</td>
          <td>${formatMoney(item.price)}</td>
          <td>${formatMoney(item.revenue)}</td>
          <td>${formatMoney(item.expenses_allocated)}</td>
          <td>${item.markup_ratio_fact}</td>
        </tr>`
      )
      .join('')}</tbody></table>`;
  }

  function renderOrders() {
    if (!state.orders.length) {
      ordersBody.innerHTML = '';
      emptyState.classList.remove('hidden');
      return;
    }
    emptyState.classList.add('hidden');

    ordersBody.innerHTML = state.orders
      .map((order) => {
        const orderRevenue = order.items.reduce((acc, item) => acc + Number(item.revenue || 0), 0);
        return `<tr>
          <td>${order.id}</td>
          <td>${order.posting_number}</td>
          <td>${order.store_name || '-'}</td>
          <td>${order.status}</td>
          <td>${order.schema}</td>
          <td>${formatDate(order.created_at)}</td>
          <td>${formatMoney(orderRevenue)}</td>
          <td><button class="btn" data-toggle="details-${order.id}">Состав</button></td>
        </tr>
        <tr id="details-${order.id}" class="details-row hidden"><td colspan="8">${buildItemsTable(order.items)}</td></tr>`;
      })
      .join('');

    ordersBody.querySelectorAll('[data-toggle]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = document.getElementById(button.dataset.toggle);
        target.classList.toggle('hidden');
      });
    });
  }

  function renderTotals() {
    const breakdown = (state.summary?.status_breakdown || [])
      .map((x) => `${x.status}: ${x.count}`)
      .join(' • ');
    totals.innerHTML = `<span>Статусы: ${breakdown || '—'}</span>`;
  }

  applyButton.addEventListener('click', () => loadData().catch(alert));
  refreshButton.addEventListener('click', () => loadData().catch(alert));
  resetButton.addEventListener('click', () => {
    storeFilter.value = '';
    dateFromFilter.value = '';
    dateToFilter.value = '';
    schemaFilter.value = 'ALL';
    offerIdFilter.value = '';
    loadData().catch(alert);
  });

  loadData().catch((e) => alert(e.message));
})();
