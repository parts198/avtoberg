'use client'

import { FormEvent, Fragment, useEffect, useMemo, useState } from 'react'

import { apiFetch } from '@/lib/api'

import styles from './orders.module.css'

type DashboardItem = {
  product_id: number | null
  offer_id: string
  product_name: string
  qty: number
  price: number
  revenue: number
  expenses_allocated: number
  markup_ratio_fact: number | null
}

type DashboardOrder = {
  id: number
  posting_number: string
  status: string
  schema: string
  created_at: string
  store_id: number
  store_name: string
  first_offer_id: string
  items_count: number
  qty_total: number
  revenue_total: number
  expenses_total: number
  markup_ratio_avg: number | null
  items: DashboardItem[]
}

type DashboardStore = {
  id: number
  name: string
}

type DashboardSummary = {
  total_orders: number
  total_items: number
  total_units: number
  total_revenue: number
  total_expenses: number
  status_breakdown: Array<{ status: string; count: number }>
  scope: string
  scope_label: string
}

type DashboardResponse = {
  stores: DashboardStore[]
  filters: Record<string, string>
  summary: DashboardSummary
  hourly: number[]
  orders: DashboardOrder[]
}

type Filters = {
  store_id: string
  date_from: string
  date_to: string
  schema: 'ALL' | 'FBS' | 'FBO'
  offer_id: string
  search: string
}

function formatMoney(value: number) {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(Number(value || 0))
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('ru-RU').format(Number(value || 0))
}

function toDateInputValue(date: Date) {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

function defaultDateRange(): Pick<Filters, 'date_from' | 'date_to'> {
  const now = new Date()
  const from = new Date(now)
  from.setDate(from.getDate() - 27)
  return {
    date_from: toDateInputValue(from),
    date_to: toDateInputValue(now),
  }
}

export default function OrdersPage() {
  const defaults = defaultDateRange()

  const [filters, setFilters] = useState<Filters>({
    store_id: '',
    date_from: defaults.date_from,
    date_to: defaults.date_to,
    schema: 'ALL',
    offer_id: '',
    search: '',
  })

  const [stores, setStores] = useState<DashboardStore[]>([])
  const [orders, setOrders] = useState<DashboardOrder[]>([])
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [hourly, setHourly] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [lastLoadedAt, setLastLoadedAt] = useState<string>('')
  const [expanded, setExpanded] = useState<Record<number, boolean>>({})

  const summaryBadge = useMemo(() => {
    return `Найдено заказов: ${formatNumber(summary?.total_orders ?? 0)}`
  }, [summary?.total_orders])

  async function loadDashboard(e?: FormEvent, forcedFilters?: Filters) {
    e?.preventDefault()
    setLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      const sourceFilters = forcedFilters || filters
      Object.entries(sourceFilters).forEach(([key, value]) => {
        if (value) params.set(key, value)
      })

      const payload = await apiFetch<DashboardResponse>(`/orders/dashboard?${params.toString()}`)
      setStores(payload.stores)
      setOrders(payload.orders)
      setSummary(payload.summary)
      setHourly(payload.hourly)
      setLastLoadedAt(new Date().toLocaleString('ru-RU'))

      setExpanded((prev) => {
        const next: Record<number, boolean> = {}
        payload.orders.forEach((o) => {
          if (prev[o.id]) next[o.id] = true
        })
        return next
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки заказов')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function updateFilter<K extends keyof Filters>(key: K, value: Filters[K]) {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  function resetFilters() {
    const dates = defaultDateRange()
    const nextFilters: Filters = {
      store_id: '',
      schema: 'ALL',
      offer_id: '',
      search: '',
      date_from: dates.date_from,
      date_to: dates.date_to,
    }
    setFilters(nextFilters)
    loadDashboard(undefined, nextFilters)
  }

  function toggleOrder(orderId: number) {
    setExpanded((prev) => ({ ...prev, [orderId]: !prev[orderId] }))
  }

  const maxHourly = hourly.length ? Math.max(...hourly) : 0

  return (
    <>
      <div className="card">
        <div className={styles.topbar}>
          <div>
            <h1>Заказы</h1>
            <p className="status-line">
              {loading
                ? 'Загрузка данных...'
                : lastLoadedAt
                  ? `Последняя загрузка: ${lastLoadedAt}`
                  : 'Готово к загрузке'}
            </p>
          </div>
          <button type="button" onClick={() => loadDashboard()} disabled={loading}>
            Обновить
          </button>
        </div>
      </div>

      <div className="card">
        <p className={styles.summaryBadge}>{summaryBadge}</p>
        <p className={styles.scopeNote}>{summary?.scope_label || '—'}</p>
        {error ? <p className={styles.error}>{error}</p> : null}
      </div>

      <div className="card">
        <form onSubmit={loadDashboard} className={styles.filters}>
          <label>
            <span>Магазин</span>
            <select
              value={filters.store_id}
              onChange={(e) => updateFilter('store_id', e.target.value)}
              disabled={loading}
            >
              <option value="">Все</option>
              {stores.map((store) => (
                <option value={store.id} key={store.id}>
                  {store.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Дата от</span>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => updateFilter('date_from', e.target.value)}
              disabled={loading}
            />
          </label>

          <label>
            <span>Дата до</span>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => updateFilter('date_to', e.target.value)}
              disabled={loading}
            />
          </label>

          <label>
            <span>Схема</span>
            <select
              value={filters.schema}
              onChange={(e) => updateFilter('schema', e.target.value as Filters['schema'])}
              disabled={loading}
            >
              <option value="ALL">ALL</option>
              <option value="FBS">FBS</option>
              <option value="FBO">FBO</option>
            </select>
          </label>

          <label>
            <span>Offer ID</span>
            <input
              value={filters.offer_id}
              onChange={(e) => updateFilter('offer_id', e.target.value)}
              placeholder="Поиск по offer_id"
              disabled={loading}
            />
          </label>

          <label>
            <span>Поиск</span>
            <input
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              placeholder="posting/payload"
              disabled={loading}
            />
          </label>

          <div className={styles.actions}>
            <button type="submit" disabled={loading}>Применить</button>
            <button
              type="button"
              onClick={() => {
                resetFilters()
              }}
              disabled={loading}
            >
              Сбросить
            </button>
          </div>
        </form>
      </div>

      <div className={styles.summaryGrid}>
        <div className="card"><b>Заказы:</b> {formatNumber(summary?.total_orders ?? 0)}</div>
        <div className="card"><b>Позиции:</b> {formatNumber(summary?.total_items ?? 0)}</div>
        <div className="card"><b>Штук:</b> {formatNumber(summary?.total_units ?? 0)}</div>
        <div className="card"><b>Выручка:</b> {formatMoney(summary?.total_revenue ?? 0)}</div>
        <div className="card"><b>Расходы:</b> {formatMoney(summary?.total_expenses ?? 0)}</div>
      </div>

      <div className="card">
        <h2>Список заказов</h2>
        {loading ? <p>Загрузка заказов…</p> : null}
        {!loading && !orders.length ? <p>Заказы не найдены для выбранных фильтров.</p> : null}

        <div className="table-wrap">
          <table className="prices-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Posting</th>
                <th>Магазин</th>
                <th>Статус</th>
                <th>Схема</th>
                <th>1-й offer_id</th>
                <th>Позиций</th>
                <th>Штук</th>
                <th>Наценка</th>
                <th>Создан</th>
                <th>Выручка</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => {
                const isOpen = Boolean(expanded[order.id])
                return (
                  <Fragment key={order.id}>
                    <tr>
                      <td>{order.id}</td>
                      <td>{order.posting_number}</td>
                      <td>{order.store_name}</td>
                      <td>{order.status}</td>
                      <td>{order.schema}</td>
                      <td>{order.first_offer_id || '—'}</td>
                      <td>{formatNumber(order.items_count)}</td>
                      <td>{formatNumber(order.qty_total)}</td>
                      <td>{order.markup_ratio_avg == null ? '—' : order.markup_ratio_avg.toFixed(2)}</td>
                      <td>{new Date(order.created_at).toLocaleString('ru-RU')}</td>
                      <td>{formatMoney(order.revenue_total)}</td>
                      <td>
                        <button type="button" onClick={() => toggleOrder(order.id)}>
                          {isOpen ? 'Скрыть' : 'Состав'}
                        </button>
                      </td>
                    </tr>
                    {isOpen ? (
                      <tr key={`${order.id}-items`}>
                        <td colSpan={12}>
                          <table className="prices-table">
                            <thead>
                              <tr>
                                <th>Product ID</th>
                                <th>Offer ID</th>
                                <th>Название</th>
                                <th>Qty</th>
                                <th>Цена</th>
                                <th>Выручка</th>
                                <th>Расходы</th>
                                <th>Наценка факт</th>
                              </tr>
                            </thead>
                            <tbody>
                              {order.items.map((item, index) => (
                                <tr key={`${order.id}-${item.offer_id}-${index}`}>
                                  <td>{item.product_id ?? '—'}</td>
                                  <td>{item.offer_id || '—'}</td>
                                  <td>{item.product_name || '—'}</td>
                                  <td>{formatNumber(item.qty)}</td>
                                  <td>{formatMoney(item.price)}</td>
                                  <td>{formatMoney(item.revenue)}</td>
                                  <td>{formatMoney(item.expenses_allocated)}</td>
                                  <td>{item.markup_ratio_fact == null ? '—' : item.markup_ratio_fact}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2>Итоги по выборке</h2>
        <p>
          Заказов: {formatNumber(summary?.total_orders ?? 0)} • Позиции: {formatNumber(summary?.total_items ?? 0)} •
          Штук: {formatNumber(summary?.total_units ?? 0)}
        </p>
        <p>
          Выручка: {formatMoney(summary?.total_revenue ?? 0)} • Расходы: {formatMoney(summary?.total_expenses ?? 0)}
        </p>
        <p>
          Статусы:{' '}
          {summary?.status_breakdown?.length
            ? summary.status_breakdown.map((item) => `${item.status}: ${item.count}`).join(' • ')
            : '—'}
        </p>
      </div>

      <div className="card">
        <h2>Распределение заказов по часам</h2>
        {hourly.length && maxHourly > 0 ? (
          <div className={styles.hourlyChart}>
            {hourly.map((value, hour) => (
              <div className={styles.hourRow} key={hour}>
                <span>{String(hour).padStart(2, '0')}:00</span>
                <div className={styles.hourBar}>
                  <div className={styles.hourBarFill} style={{ width: `${(value / maxHourly) * 100}%` }} />
                </div>
                <span>{value}</span>
              </div>
            ))}
          </div>
        ) : (
          <p>TODO: расширить блок графиков и прогнозов на будущей итерации.</p>
        )}
      </div>
    </>
  )
}
