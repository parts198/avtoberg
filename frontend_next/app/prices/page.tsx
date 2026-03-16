'use client'

import { FormEvent, useMemo, useState } from 'react'

import { apiFetch } from '@/lib/api'

type PriceRow = {
  product_id: number
  offer_id: string
  title: string
  stock: number
  fbs: number
  fbo: number
  current_price: number
  previous_price: number | null
  acquiring: number
  customer_delivery: number
  logistics: number
  first_mile: number
  packaging: number
  promotion: number
  ozon_commission_percent: number
  ozon_commission_rub: number
  cost_price: number
  fbs_cost: number
  payout_to_seller: number
  markup_percent: number
  margin_rub: number
  margin_percent: number
}

type PriceListResponse = {
  total: number
  page: number
  page_size: number
  items: PriceRow[]
}

const PAGE_SIZES = [100, 500, 1000, 5000]

const money = (value: number) => `${value.toFixed(2)} ₽`
const pct = (value: number) => `${value.toFixed(2)}%`

export default function PricesPage() {
  const [rows, setRows] = useState<PriceRow[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(100)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState<'price' | 'offer_id'>('price')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [markup, setMarkup] = useState('25')
  const [minMarkup, setMinMarkup] = useState('5')
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [status, setStatus] = useState('Готов к работе')
  const [error, setError] = useState('')

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  const selectedCount = useMemo(
    () => rows.filter((r) => selectedIds.includes(r.product_id)).length,
    [rows, selectedIds],
  )

  async function loadPrices(nextPage = page, nextPageSize = pageSize, e?: FormEvent) {
    e?.preventDefault()
    setStatus('Загружаем данные...')
    setError('')

    const query = new URLSearchParams({
      page: String(nextPage),
      page_size: String(nextPageSize),
      sort_by: sortBy,
      sort_order: sortOrder,
    })
    if (search.trim()) {
      query.set('search', search.trim())
    }

    try {
      const data = await apiFetch<PriceListResponse>(`/prices?${query.toString()}`)
      setRows(data.items)
      setTotal(data.total)
      setPage(data.page)
      setPageSize(data.page_size)
      setSelectedIds([])
      setStatus(`Загружено ${data.items.length} записей`) 
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки цен')
      setStatus('Ошибка загрузки')
    }
  }

  async function applyMarkupToAll() {
    const markupValue = Number(markup)
    const minMarkupValue = Number(minMarkup)
    if (!Number.isFinite(markupValue) || !Number.isFinite(minMarkupValue)) {
      setError('Введите корректные значения наценки')
      return
    }

    setStatus('Применяем наценку...')
    setError('')

    try {
      await apiFetch<PriceListResponse>('/prices/apply-markup', {
        method: 'POST',
        body: JSON.stringify({
          markup_percent: markupValue,
          min_price_markup_percent: minMarkupValue,
        }),
      })
      setStatus('Наценка применена')
      await loadPrices(1, pageSize)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка применения наценки')
      setStatus('Ошибка применения наценки')
    }
  }

  async function updateSelected() {
    if (!selectedIds.length) {
      setError('Выберите хотя бы один товар')
      return
    }

    setStatus('Обновляем выбранные позиции...')
    setError('')

    try {
      const updates = rows
        .filter((row) => selectedIds.includes(row.product_id))
        .map((row) => ({ product_id: row.product_id, new_price: row.current_price }))

      await apiFetch<PriceListResponse>('/prices/bulk-update', {
        method: 'POST',
        body: JSON.stringify({ updates }),
      })

      setStatus(`Обновлено товаров: ${updates.length}`)
      await loadPrices(page, pageSize)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления выбранных')
      setStatus('Ошибка обновления')
    }
  }

  async function updateAll() {
    if (!rows.length) {
      setError('Нет данных для обновления')
      return
    }

    setStatus('Обновляем все позиции на листе...')
    setError('')

    try {
      const updates = rows.map((row) => ({ product_id: row.product_id, new_price: row.current_price }))
      await apiFetch<PriceListResponse>('/prices/bulk-update', {
        method: 'POST',
        body: JSON.stringify({ updates }),
      })
      setStatus(`Обновлено товаров: ${updates.length}`)
      await loadPrices(page, pageSize)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления всех')
      setStatus('Ошибка обновления')
    }
  }

  function toggleSelection(productId: number) {
    setSelectedIds((prev) =>
      prev.includes(productId) ? prev.filter((id) => id !== productId) : [...prev, productId],
    )
  }

  function setPrice(productId: number, value: string) {
    const next = Number(value)
    setRows((prev) =>
      prev.map((row) => {
        if (row.product_id !== productId) return row
        if (!Number.isFinite(next) || next <= 0) return row
        const acquiring = Number((next * 0.019).toFixed(2))
        const promotion = Number((next * 0.01).toFixed(2))
        const commission = Number((next * row.ozon_commission_percent / 100).toFixed(2))
        const payout = Number((
          next -
          acquiring -
          row.customer_delivery -
          row.logistics -
          row.first_mile -
          row.packaging -
          promotion -
          commission -
          row.fbs_cost
        ).toFixed(2))
        const marginRub = Number((payout - row.cost_price).toFixed(2))
        const marginPercent = Number(((marginRub / next) * 100).toFixed(2))
        const markupPercent = Number((((next - row.cost_price) / row.cost_price) * 100).toFixed(2))

        return {
          ...row,
          current_price: next,
          acquiring,
          promotion,
          ozon_commission_rub: commission,
          payout_to_seller: payout,
          margin_rub: marginRub,
          margin_percent: marginPercent,
          markup_percent: markupPercent,
        }
      }),
    )
  }

  return (
    <>
      <div className="card">
        <h1>Цены OZON</h1>
        <p>Упаковка: 40 ₽ · Продвижение: 1% от цены · Эквайринг: 1.9%.</p>
      </div>

      <div className="card">
        <div className="status-line">{status}</div>
        {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}

        <form className="prices-toolbar" onSubmit={(e) => loadPrices(1, pageSize, e)}>
          <input
            type="search"
            placeholder="Фильтр по артикулу / SKU"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit">Обновить данные</button>

          <label>
            Товаров на листе
            <select
              value={pageSize}
              onChange={(e) => {
                const size = Number(e.target.value)
                setPageSize(size)
                void loadPrices(1, size)
              }}
            >
              {PAGE_SIZES.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>

          <label>
            Сортировка
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as 'price' | 'offer_id')}>
              <option value="price">Цена</option>
              <option value="offer_id">Артикул</option>
            </select>
          </label>

          <label>
            Порядок
            <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}>
              <option value="desc">По убыванию</option>
              <option value="asc">По возрастанию</option>
            </select>
          </label>
        </form>

        <div className="prices-toolbar">
          <input value={markup} onChange={(e) => setMarkup(e.target.value)} type="number" step="0.01" placeholder="Наценка, %" />
          <input value={minMarkup} onChange={(e) => setMinMarkup(e.target.value)} type="number" step="0.01" placeholder="Мин. наценка, %" />
          <button type="button" onClick={applyMarkupToAll}>Применить ко всем</button>
          <button type="button" onClick={updateSelected}>Обновить выбранные ({selectedCount})</button>
          <button type="button" onClick={updateAll}>Обновить все на листе</button>
        </div>

        <div className="table-wrap">
          <table className="prices-table">
            <thead>
              <tr>
                <th></th>
                <th>Артикул</th>
                <th>Наименование</th>
                <th>FBS</th>
                <th>FBO</th>
                <th>Остаток</th>
                <th>Цена</th>
                <th>Эквайринг</th>
                <th>Доставка</th>
                <th>Логистика</th>
                <th>Первая миля</th>
                <th>Упаковка</th>
                <th>Продвижение</th>
                <th>Комиссия %</th>
                <th>Комиссия ₽</th>
                <th>Себестоимость</th>
                <th>FBS затраты</th>
                <th>К выплате</th>
                <th>Наценка</th>
                <th>Маржа</th>
                <th>Маржинальность</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.product_id}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(row.product_id)}
                      onChange={() => toggleSelection(row.product_id)}
                    />
                  </td>
                  <td>{row.offer_id}</td>
                  <td>{row.title}</td>
                  <td>{row.fbs}</td>
                  <td>{row.fbo}</td>
                  <td>{row.stock}</td>
                  <td>
                    <input
                      value={row.current_price}
                      type="number"
                      step="0.01"
                      onChange={(e) => setPrice(row.product_id, e.target.value)}
                      style={{ width: 96 }}
                    />
                  </td>
                  <td>{money(row.acquiring)}</td>
                  <td>{money(row.customer_delivery)}</td>
                  <td>{money(row.logistics)}</td>
                  <td>{money(row.first_mile)}</td>
                  <td>{money(row.packaging)}</td>
                  <td>{money(row.promotion)}</td>
                  <td>{pct(row.ozon_commission_percent)}</td>
                  <td>{money(row.ozon_commission_rub)}</td>
                  <td>{money(row.cost_price)}</td>
                  <td>{money(row.fbs_cost)}</td>
                  <td>{money(row.payout_to_seller)}</td>
                  <td>{pct(row.markup_percent)}</td>
                  <td>{money(row.margin_rub)}</td>
                  <td>{pct(row.margin_percent)}</td>
                </tr>
              ))}
              {!rows.length ? (
                <tr>
                  <td colSpan={21}>Нажмите «Обновить данные», чтобы загрузить цены.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

        <div className="prices-pager">
          <button type="button" disabled={page <= 1} onClick={() => void loadPrices(page - 1, pageSize)}>
            ← Предыдущий лист
          </button>
          <span>Лист {page} из {totalPages}</span>
          <button type="button" disabled={page >= totalPages} onClick={() => void loadPrices(page + 1, pageSize)}>
            Следующий лист →
          </button>
        </div>
      </div>
    </>
  )
}
