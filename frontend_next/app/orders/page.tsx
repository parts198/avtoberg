'use client'

import { FormEvent, useState } from 'react'

import { apiFetch } from '@/lib/api'

type Order = {
  id: number
  store_id: number
  external_order_id: string
  status: string
  order_date: string
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')

  async function loadOrders(e?: FormEvent) {
    e?.preventDefault()
    setError('')
    try {
      const qs = search ? `?search=${encodeURIComponent(search)}` : ''
      const data = await apiFetch<Order[]>(`/orders${qs}`)
      setOrders(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки заказов')
    }
  }

  return (
    <>
      <div className="card"><h1>Заказы</h1><p>Реальные данные, полученные из маркетплейса во время initial sync.</p></div>
      <div className="card">
        <form onSubmit={loadOrders} style={{ display: 'flex', gap: 8 }}>
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Поиск по номеру/sku/артикулу" />
          <button type="submit">Найти</button>
        </form>
        {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}
        <button onClick={() => loadOrders()} style={{ marginTop: 8 }}>Обновить</button>
        <div className="grid" style={{ marginTop: 12 }}>
          {orders.map((o) => (
            <div className="card" key={o.id} style={{ margin: 0 }}>
              <b>{o.external_order_id}</b>
              <p>Store: {o.store_id}</p>
              <p>Status: {o.status}</p>
              <p>Date: {o.order_date}</p>
            </div>
          ))}
          {!orders.length ? <p>Заказы не найдены.</p> : null}
        </div>
      </div>
    </>
  )
}
