'use client'

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'

import { apiFetch, getToken } from '@/lib/api'

type Store = {
  id: number
  name: string
  marketplace: 'ozon' | 'wildberries'
}

type PriceLogEntry = {
  id: number
  message: string
  created_at: string
}

type PriceRow = {
  product_id: number
  offer_id: string
  title: string
  stock: number
  fbs: number
  fbo: number
  current_price: number
  min_price: number
  acquiring: number
  customer_delivery: number
  logistics: number
  first_mile: number
  packaging: number
  promotion: number
  promotion_percent: number
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
  logs: PriceLogEntry[]
}

const PAGE_SIZES = [100, 500, 1000, 5000]
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

const money = (value: number) => `${value.toFixed(2)} ₽`
const pct = (value: number) => `${value.toFixed(2)}%`

function recalcRow(
  row: PriceRow,
  next: { price?: number; markup?: number; cost?: number; promotionPercent?: number; packaging?: number },
): PriceRow {
  const currentPrice = next.price ?? row.current_price
  const costPrice = next.cost ?? row.cost_price
  const customerDelivery = row.customer_delivery
  const logistics = row.logistics
  const firstMile = row.first_mile
  const packaging = next.packaging ?? row.packaging
  const promotionPercent = next.promotionPercent ?? row.promotion_percent
  const fbsCost = row.fbs_cost
  const commissionPercent = row.ozon_commission_percent

  const denominator = 1 - 0.019 - promotionPercent / 100 - commissionPercent / 100
  const priceFromMarkup = (markupValue: number) => {
    if (denominator <= 0) return currentPrice
    const payoutTarget = costPrice * (1 + markupValue / 100)
    return Number(((payoutTarget + customerDelivery + logistics + firstMile + packaging + fbsCost) / denominator).toFixed(2))
  }

  const effectivePrice = next.markup !== undefined ? priceFromMarkup(next.markup) : currentPrice
  const acquiring = Number((effectivePrice * 0.019).toFixed(2))
  const promotion = Number(((effectivePrice * promotionPercent) / 100).toFixed(2))
  const commission = Number(((effectivePrice * commissionPercent) / 100).toFixed(2))
  const payout = Number(
    (
      effectivePrice - acquiring - customerDelivery - logistics - firstMile - packaging - promotion - commission - fbsCost
    ).toFixed(2),
  )
  const markupPercent = costPrice ? Number((((payout / costPrice) - 1) * 100).toFixed(2)) : 0
  const marginRub = Number((payout - costPrice).toFixed(2))
  const marginPercent = effectivePrice ? Number(((marginRub / effectivePrice) * 100).toFixed(2)) : 0
  const minPrice = Number(Math.min(row.min_price, effectivePrice).toFixed(2))

  return {
    ...row,
    current_price: effectivePrice,
    min_price: minPrice,
    cost_price: costPrice,
    packaging,
    promotion_percent: promotionPercent,
    acquiring,
    promotion,
    ozon_commission_rub: commission,
    payout_to_seller: payout,
    markup_percent: markupPercent,
    margin_rub: marginRub,
    margin_percent: marginPercent,
  }
}

function humanPriceError(message: string): string {
  if (message.toLowerCase().includes('ozon')) return message
  if (message.includes('403') || message.includes('401')) return 'Нет доступа к обновлению цены в Ozon. Проверьте API-ключи магазина.'
  return 'Не удалось обновить цену в Ozon. Попробуйте ещё раз.'
}

export default function PricesPage() {
  const [stores, setStores] = useState<Store[]>([])
  const [storeId, setStoreId] = useState<number | null>(null)
  const [rows, setRows] = useState<PriceRow[]>([])
  const [logs, setLogs] = useState<PriceLogEntry[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(100)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState<'stock' | 'price' | 'offer_id'>('stock')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [markup, setMarkup] = useState('25')
  const [minMarkup, setMinMarkup] = useState('5')
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [status, setStatus] = useState('Готов к работе')
  const [error, setError] = useState('')
  const costFileInputRef = useRef<HTMLInputElement | null>(null)

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  const selectedCount = useMemo(() => rows.filter((r) => selectedIds.includes(r.offer_id)).length, [rows, selectedIds])

  useEffect(() => {
    void loadStores()
  }, [])

  async function loadStores() {
    try {
      const data = await apiFetch<Store[]>('/stores')
      const ozonStores = data.filter((store) => store.marketplace === 'ozon')
      setStores(ozonStores)
      if (ozonStores.length) {
        setStoreId((prev) => prev ?? ozonStores[0].id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки магазинов')
    }
  }

  async function loadPrices(nextPage = page, nextPageSize = pageSize, e?: FormEvent) {
    e?.preventDefault()
    if (!storeId) {
      setError('Выберите магазин')
      return
    }

    setStatus('Загружаем данные...')
    setError('')

    const query = new URLSearchParams({
      store_id: String(storeId),
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
      setLogs(data.logs)
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

  async function reloadData() {
    if (!storeId) return
    setStatus('Обновляем данные...')
    setError('')

    try {
      await apiFetch('/prices/reload', {
        method: 'POST',
        body: JSON.stringify({ store_id: storeId }),
      })
      await loadPrices(1, pageSize)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления данных')
      setStatus('Ошибка обновления данных')
    }
  }

  async function applyMarkupToAll() {
    if (!storeId) return
    const markupValue = Number(markup)
    const minMarkupValue = Number(minMarkup)
    if (!Number.isFinite(markupValue) || !Number.isFinite(minMarkupValue)) {
      setError('Введите корректные значения наценки')
      return
    }

    setStatus('Применяем наценку...')
    setError('')

    try {
      await apiFetch<PriceListResponse>(`/prices/apply-markup?store_id=${storeId}`, {
        method: 'POST',
        body: JSON.stringify({
          markup_percent: markupValue,
          min_price_markup_percent: minMarkupValue,
        }),
      })
      await loadPrices(page, pageSize)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка применения наценки')
      setStatus('Ошибка применения наценки')
    }
  }

  async function updateSingle(offerId: string) {
    if (!storeId) return
    const row = rows.find((item) => item.offer_id === offerId)
    if (!row) return

    try {
      const updated = await apiFetch<PriceRow>(`/prices/${encodeURIComponent(offerId)}?store_id=${storeId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          new_price: row.current_price,
          min_price: row.min_price,
          markup_percent: row.markup_percent,
          cost_price: row.cost_price,
          promotion_percent: row.promotion_percent,
          packaging: row.packaging,
        }),
      })
      setRows((prev) => prev.map((item) => (item.offer_id === offerId ? updated : item)))
      setStatus(`Позиция ${offerId} обновлена в Ozon и перечитана`)
    } catch (err) {
      setError(humanPriceError(err instanceof Error ? err.message : 'Ошибка обновления позиции'))
      setStatus(`Ошибка обновления ${offerId}`)
    }
  }

  async function updateBulk(offerIds: string[]) {
    if (!storeId || !offerIds.length) return
    const updates = rows.filter((row) => offerIds.includes(row.offer_id)).map((row) => ({
      offer_id: row.offer_id,
      new_price: row.current_price,
      min_price: row.min_price,
    }))

    if (!updates.length) return

    try {
      await apiFetch(`/prices/bulk-update?store_id=${storeId}`, {
        method: 'POST',
        body: JSON.stringify({ updates }),
      })
      await loadPrices(page, pageSize)
      setStatus(`Обновлено товаров: ${updates.length}`)
    } catch (err) {
      setError(humanPriceError(err instanceof Error ? err.message : 'Ошибка массового обновления'))
      setStatus('Ошибка обновления')
    }
  }

  async function exportXlsx() {
    if (!storeId) return
    setError('')

    try {
      const token = getToken()
      const query = new URLSearchParams({ store_id: String(storeId) })
      if (search.trim()) query.set('search', search.trim())
      const response = await fetch(`${API_URL}/prices/export-xlsx?${query.toString()}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'ozon-prices.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка экспорта XLSX')
    }
  }

  async function importCostXlsx(file: File) {
    if (!storeId) return
    setError('')
    setStatus('Импортируем себестоимость...')

    const token = getToken()
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await fetch(`${API_URL}/prices/import-cost-xlsx?store_id=${storeId}`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      })
      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as { detail?: string } | null
        throw new Error(body?.detail || `HTTP ${response.status}`)
      }
      await loadPrices(page, pageSize)
      setStatus('Себестоимость импортирована')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка импорта XLSX себестоимости')
      setStatus('Ошибка импорта себестоимости')
    } finally {
      if (costFileInputRef.current) {
        costFileInputRef.current.value = ''
      }
    }
  }

  function toggleSelection(offerId: string) {
    setSelectedIds((prev) => (prev.includes(offerId) ? prev.filter((id) => id !== offerId) : [...prev, offerId]))
  }

  function setPrice(offerId: string, value: string) {
    const next = Number(value)
    if (!Number.isFinite(next) || next <= 0) return

    setRows((prev) => prev.map((row) => (row.offer_id === offerId ? recalcRow(row, { price: next }) : row)))
  }

  function setMarkupValue(offerId: string, value: string) {
    const next = Number(value)
    if (!Number.isFinite(next)) return

    setRows((prev) => prev.map((row) => (row.offer_id === offerId ? recalcRow(row, { markup: next }) : row)))
  }

  function setCostPrice(offerId: string, value: string) {
    const next = Number(value)
    if (!Number.isFinite(next) || next < 0) return

    setRows((prev) => prev.map((row) => (row.offer_id === offerId ? recalcRow(row, { cost: next }) : row)))
  }

  function setPromotionPercent(offerId: string, value: string) {
    const next = Number(value)
    if (!Number.isFinite(next) || next < 0) return

    setRows((prev) => prev.map((row) => (row.offer_id === offerId ? recalcRow(row, { promotionPercent: next }) : row)))
  }

  function setPackaging(offerId: string, value: string) {
    const next = Number(value)
    if (!Number.isFinite(next) || next < 0) return

    setRows((prev) => prev.map((row) => (row.offer_id === offerId ? recalcRow(row, { packaging: next }) : row)))
  }

  return (
    <>
      <div className="card">
        <h1>Цены OZON</h1>
        <p>Формулы берутся из Ozon API: эквайринг, доставка, логистика, комиссия и себестоимость.</p>
      </div>

      <div className="card prices-card">
        <div className="status-line">{status}</div>
        {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}

        <form className="prices-toolbar" onSubmit={(e) => void loadPrices(1, pageSize, e)}>
          <select value={storeId ?? ''} onChange={(e) => setStoreId(Number(e.target.value))} aria-label="Выбор магазина">
            <option value="" disabled>
              Выберите магазин
            </option>
            {stores.map((store) => (
              <option key={store.id} value={store.id}>
                {store.name}
              </option>
            ))}
          </select>
          <input type="search" placeholder="Фильтр по артикулу" value={search} onChange={(e) => setSearch(e.target.value)} />
          <button type="button" onClick={reloadData}>Обновить данные</button>
          <button type="submit">Загрузить цены</button>

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
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as 'stock' | 'price' | 'offer_id')}>
              <option value="stock">Остаток</option>
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
          <button type="button" onClick={() => void updateBulk(selectedIds)}>Обновить выбранные ({selectedCount})</button>
          <button type="button" onClick={() => void updateBulk(rows.map((r) => r.offer_id))}>Обновить все на листе</button>
          <button type="button" onClick={exportXlsx}>Скачать XLSX</button>
          <button type="button" onClick={() => costFileInputRef.current?.click()}>Загрузить себестоимость XLSX</button>
          <input
            ref={costFileInputRef}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            style={{ display: 'none' }}
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) {
                void importCostXlsx(file)
              }
            }}
          />
        </div>

        <details className="log-panel">
          <summary>Лог запросов</summary>
          <div className="log-entries">
            {logs.map((log) => (
              <div key={log.id}>{new Date(log.created_at).toLocaleString()} · {log.message}</div>
            ))}
            {!logs.length ? <div>Логи пока пустые</div> : null}
          </div>
        </details>

        <div className="table-wrap">
          <table className="prices-table">
            <thead>
              <tr>
                <th aria-label="Выбор строки"></th>
                <th><span className="th-label">Артикул</span></th>
                <th><span className="th-label">FBS</span></th>
                <th><span className="th-label">FBO</span></th>
                <th><span className="th-label">Остаток</span></th>
                <th><span className="th-label">Цена</span></th>
                <th><span className="th-label">Min price</span></th>
                <th><span className="th-label">Эквайринг</span></th>
                <th><span className="th-label">Доставка</span></th>
                <th><span className="th-label">Логистика</span></th>
                <th><span className="th-label">Упаковка</span></th>
                <th><span className="th-label">Продвижение %</span></th>
                <th><span className="th-label">Продвижение, ₽</span></th>
                <th><span className="th-label">Комиссия %</span></th>
                <th><span className="th-label">Комиссия ₽</span></th>
                <th><span className="th-label">Себестоимость</span></th>
                <th><span className="th-label">Затраты FBS</span></th>
                <th><span className="th-label">К выплате</span></th>
                <th><span className="th-label">Наценка</span></th>
                <th><span className="th-label">Маржа</span></th>
                <th><span className="th-label">Действия</span></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.product_id}>
                  <td>
                    <input type="checkbox" checked={selectedIds.includes(row.offer_id)} onChange={() => toggleSelection(row.offer_id)} />
                  </td>
                  <td title={row.title}>{row.offer_id}</td>
                  <td>{row.fbs}</td>
                  <td>{row.fbo}</td>
                  <td>{row.stock}</td>
                  <td><input value={row.current_price} type="number" step="0.01" onChange={(e) => setPrice(row.offer_id, e.target.value)} style={{ width: 84 }} /></td>
                  <td>{money(row.min_price)}</td>
                  <td>{money(row.acquiring)}</td>
                  <td>{money(row.customer_delivery)}</td>
                  <td>{money(row.logistics)}</td>
                  <td><input value={row.packaging} type="number" step="0.01" onChange={(e) => setPackaging(row.offer_id, e.target.value)} style={{ width: 72 }} /></td>
                  <td><input value={row.promotion_percent} type="number" step="0.01" onChange={(e) => setPromotionPercent(row.offer_id, e.target.value)} style={{ width: 72 }} /></td>
                  <td>{money(row.promotion)}</td>
                  <td>{pct(row.ozon_commission_percent)}</td>
                  <td>{money(row.ozon_commission_rub)}</td>
                  <td><input value={row.cost_price} type="number" step="0.01" onChange={(e) => setCostPrice(row.offer_id, e.target.value)} style={{ width: 84 }} /></td>
                  <td>{money(row.fbs_cost)}</td>
                  <td>{money(row.payout_to_seller)}</td>
                  <td><input value={row.markup_percent} type="number" step="0.01" onChange={(e) => setMarkupValue(row.offer_id, e.target.value)} style={{ width: 84 }} /></td>
                  <td>{money(row.margin_rub)}</td>
                  <td><button type="button" onClick={() => void updateSingle(row.offer_id)}>Обновить</button></td>
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
