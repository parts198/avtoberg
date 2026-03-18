(function () {
  const state = {
    stores: [],
    orders: [],
    summary: null,
    hourly: [],
    filters: {
      store: '',
      date_from: '',
      date_to: '',
      schema: 'ALL',
      offer_id: '',
    },
    loading: false,
    lastLoadedAt: null,
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
  const loadingState = document.getElementById('loading-state');
  const errorText = document.getElementById('error-text');
  const statusText = document.getElementById('status-text');
  const ordersSummary = document.getElementById('orders-summary');
  const scopeNote = document.getElementById('scope-note');
  const hourlyChart = document.getElementById('hourly-chart');
  const hourlyTodo = document.getElementById('hourly-todo');

  function formatMoney(v) {
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(Number(v || 0));
  }

  function formatDate(v) {
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? '-' : d.toLocaleString('ru-RU');
  }

  function formatNumber(v) {
    return new Intl.NumberFormat('ru-RU').format(Number(v || 0));
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function setLoading(value) {
    state.loading = value;
    loadingState.classList.toggle('hidden', !value);
    applyButton.disabled = value;
    resetButton.disabled = value;
    refreshButton.disabled = value;
  }

  function setError(message) {
    if (message) {
      errorText.textContent = message;
      errorText.classList.remove('hidden');
    } else {
      errorText.textContent = '';
      errorText.classList.add('hidden');
    }
  }

  function setDefaultDates() {
    if (dateFromFilter.value || dateToFilter.value) return;
    const now = new Date();
    const from = new Date(now);
    from.setDate(now.getDate() - 27);

    dateToFilter.value = toISODate(now);
    dateFromFilter.value = toISODate(from);
  }

  function toISODate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  async function loadData() {
    setLoading(true);
    setError('');
    statusText.textContent = 'Загрузка данных...';

    state.filters.store = storeFilter.value;
    state.filters.date_from = dateFromFilter.value;
    state.filters.date_to = dateToFilter.value;
    state.filters.schema = schemaFilter.value;
    state.filters.offer_id = offerIdFilter.value.trim();

    const params = new URLSearchParams();
    Object.entries(state.filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    try {
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
      state.stores = payload.stores || [];
      state.orders = payload.orders || [];
      state.summary = payload.summary || {};
      state.hourly = payload.hourly || [];
      state.lastLoadedAt = new Date();

      renderFilters();
      renderSummary();
      renderOrders();
      renderTotals();
      renderHourly();

      statusText.textContent = `Последняя загрузка: ${state.lastLoadedAt.toLocaleString('ru-RU')}`;
      ordersSummary.textContent = `Найдено заказов: ${formatNumber(state.summary.total_orders || 0)}`;
      scopeNote.textContent = state.summary.scope_label || '';
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Ошибка загрузки заказов');
      statusText.textContent = 'Ошибка загрузки. Попробуйте обновить.';
    } finally {
      setLoading(false);
    }
  }

  function renderFilters() {
    const selectedStore = state.filters.store;
    storeFilter.textContent = '';

    const allOption = document.createElement('option');
    allOption.value = '';
    allOption.textContent = 'Все';
    storeFilter.appendChild(allOption);

    state.stores.forEach((store) => {
      const option = document.createElement('option');
      option.value = String(store.id);
      option.textContent = store.name;
      storeFilter.appendChild(option);
    });

    storeFilter.value = selectedStore;
  }

  function createSummaryCard(label, value) {
    const card = document.createElement('article');
    card.className = 'summary-item';
    const labelEl = document.createElement('div');
    labelEl.className = 'label';
    labelEl.textContent = label;
    const valueEl = document.createElement('div');
    valueEl.className = 'value';
    valueEl.textContent = value;
    card.appendChild(labelEl);
    card.appendChild(valueEl);
    return card;
  }

  function renderSummary() {
    summaryContainer.textContent = '';
    const summary = state.summary || {};
    summaryContainer.appendChild(createSummaryCard('Всего заказов', formatNumber(summary.total_orders || 0)));
    summaryContainer.appendChild(createSummaryCard('Строк позиций', formatNumber(summary.total_items || 0)));
    summaryContainer.appendChild(createSummaryCard('Всего штук', formatNumber(summary.total_units || 0)));
    summaryContainer.appendChild(createSummaryCard('Выручка', formatMoney(summary.total_revenue || 0)));
    summaryContainer.appendChild(createSummaryCard('Расходы', formatMoney(summary.total_expenses || 0)));
  }

  function appendCell(row, text) {
    const cell = document.createElement('td');
    cell.textContent = text;
    row.appendChild(cell);
    return cell;
  }

  function renderOrderItemsRow(items) {
    const detailsRow = document.createElement('tr');
    detailsRow.className = 'details-row hidden';
    const detailsCell = document.createElement('td');
    detailsCell.colSpan = 12;

    const itemsTable = document.createElement('table');
    itemsTable.className = 'items-table';

    const head = document.createElement('thead');
    const headTr = document.createElement('tr');
    ['Product ID', 'Offer ID', 'Название', 'Qty', 'Цена', 'Выручка', 'Расходы', 'Наценка факт'].forEach((label) => {
      const th = document.createElement('th');
      th.textContent = label;
      headTr.appendChild(th);
    });
    head.appendChild(headTr);
    itemsTable.appendChild(head);

    const body = document.createElement('tbody');
    items.forEach((item) => {
      const tr = document.createElement('tr');
      appendCell(tr, item.product_id ? String(item.product_id) : '-');
      appendCell(tr, item.offer_id || '-');
      appendCell(tr, item.product_name || '-');
      appendCell(tr, formatNumber(item.qty));
      appendCell(tr, formatMoney(item.price));
      appendCell(tr, formatMoney(item.revenue));
      appendCell(tr, formatMoney(item.expenses_allocated));
      appendCell(tr, item.markup_ratio_fact == null ? '—' : String(item.markup_ratio_fact));
      body.appendChild(tr);
    });
    itemsTable.appendChild(body);

    detailsCell.appendChild(itemsTable);
    detailsRow.appendChild(detailsCell);
    return detailsRow;
  }

  function renderOrders() {
    ordersBody.textContent = '';

    if (!state.orders.length) {
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');

    state.orders.forEach((order) => {
      const orderRow = document.createElement('tr');
      appendCell(orderRow, String(order.id));
      appendCell(orderRow, order.posting_number || '-');
      appendCell(orderRow, order.store_name || '-');
      appendCell(orderRow, order.status || '-');
      appendCell(orderRow, order.schema || '-');
      appendCell(orderRow, order.first_offer_id || '-');
      appendCell(orderRow, formatNumber(order.items_count));
      appendCell(orderRow, formatNumber(order.qty_total));

      const markup = order.markup_ratio_avg == null ? '—' : Number(order.markup_ratio_avg).toFixed(2);
      appendCell(orderRow, markup);
      appendCell(orderRow, formatDate(order.created_at));
      appendCell(orderRow, formatMoney(order.revenue_total));

      const actionCell = document.createElement('td');
      const detailsButton = document.createElement('button');
      detailsButton.className = 'btn';
      detailsButton.textContent = 'Состав';
      actionCell.appendChild(detailsButton);
      orderRow.appendChild(actionCell);

      const detailsRow = renderOrderItemsRow(order.items || []);
      detailsButton.addEventListener('click', () => {
        detailsRow.classList.toggle('hidden');
      });

      ordersBody.appendChild(orderRow);
      ordersBody.appendChild(detailsRow);
    });
  }

  function renderTotals() {
    totals.textContent = '';

    const summary = state.summary || {};
    const topLine = document.createElement('div');
    topLine.textContent = `Заказов: ${formatNumber(summary.total_orders || 0)} • Позиции: ${formatNumber(summary.total_items || 0)} • Штук: ${formatNumber(summary.total_units || 0)}`;
    const financeLine = document.createElement('div');
    financeLine.textContent = `Выручка: ${formatMoney(summary.total_revenue || 0)} • Расходы: ${formatMoney(summary.total_expenses || 0)}`;

    const statusesLine = document.createElement('div');
    const breakdown = (summary.status_breakdown || [])
      .map((x) => `${x.status}: ${x.count}`)
      .join(' • ');
    statusesLine.textContent = `Статусы: ${breakdown || '—'}`;

    totals.appendChild(topLine);
    totals.appendChild(financeLine);
    totals.appendChild(statusesLine);
  }

  function renderHourly() {
    hourlyChart.textContent = '';
    const points = state.hourly || [];
    const maxValue = points.length ? Math.max(...points) : 0;

    if (!points.length || maxValue === 0) {
      hourlyTodo.classList.remove('hidden');
      const noData = document.createElement('p');
      noData.className = 'muted';
      noData.textContent = 'Нет данных для почасового распределения в текущем фильтре.';
      hourlyChart.appendChild(noData);
      return;
    }

    hourlyTodo.classList.add('hidden');
    points.forEach((value, hour) => {
      const row = document.createElement('div');
      row.className = 'hour-row';

      const hourLabel = document.createElement('span');
      hourLabel.textContent = `${String(hour).padStart(2, '0')}:00`;

      const bar = document.createElement('div');
      bar.className = 'hour-bar';
      const barFill = document.createElement('div');
      barFill.className = 'hour-bar-fill';
      barFill.style.width = `${(value / maxValue) * 100}%`;
      bar.appendChild(barFill);

      const valueLabel = document.createElement('span');
      valueLabel.textContent = String(value);

      row.appendChild(hourLabel);
      row.appendChild(bar);
      row.appendChild(valueLabel);
      hourlyChart.appendChild(row);
    });
  }

  applyButton.addEventListener('click', () => {
    loadData();
  });

  refreshButton.addEventListener('click', () => {
    loadData();
  });

  resetButton.addEventListener('click', () => {
    storeFilter.value = '';
    schemaFilter.value = 'ALL';
    offerIdFilter.value = '';
    setDefaultDates();
    loadData();
  });

  setDefaultDates();
  loadData();
})();
