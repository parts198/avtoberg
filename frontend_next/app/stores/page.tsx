'use client'

import { FormEvent, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

import { apiFetch, clearToken, getToken } from '@/lib/api'

type Store = {
  id: number
  name: string
  marketplace: 'ozon' | 'wildberries'
  is_enabled: boolean
  connection_status: string
  last_sync_at: string | null
}

export default function StoresPage() {
  const router = useRouter()
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [name, setName] = useState('')
  const [marketplace, setMarketplace] = useState<'ozon' | 'wildberries'>('ozon')
  const [clientId, setClientId] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [wbToken, setWbToken] = useState('')

  async function loadStores() {
    setLoading(true)
    setError('')
    try {
      const data = await apiFetch<Store[]>('/stores')
      setStores(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ошибка загрузки'
      if (message.includes('401')) {
        clearToken()
        router.push('/login')
      }
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!getToken()) {
      router.push('/login')
      return
    }
    loadStores()
  }, [])

  async function createStore(e: FormEvent) {
    e.preventDefault()
    setError('')

    const credentials =
      marketplace === 'ozon'
        ? { client_id: clientId, api_key: apiKey }
        : { token: wbToken }

    try {
      await apiFetch('/stores', {
        method: 'POST',
        body: JSON.stringify({ name, marketplace, credentials }),
      })
      setName('')
      setClientId('')
      setApiKey('')
      setWbToken('')
      loadStores()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания магазина')
    }
  }

  return (
    <>
      <div className="card">
        <h1>Магазины</h1>
        <p>Рабочий сценарий: список + добавление магазина с реальной проверкой API-ключей.</p>
      </div>

      <div className="card">
        <h2>Добавить магазин</h2>
        <form onSubmit={createStore} className="grid" style={{ maxWidth: 520 }}>
          <input placeholder="Название магазина" value={name} onChange={(e) => setName(e.target.value)} required />
          <select value={marketplace} onChange={(e) => setMarketplace(e.target.value as 'ozon' | 'wildberries')}>
            <option value="ozon">Ozon</option>
            <option value="wildberries">Wildberries</option>
          </select>

          {marketplace === 'ozon' ? (
            <>
              <input placeholder="Ozon Client ID" value={clientId} onChange={(e) => setClientId(e.target.value)} required />
              <input placeholder="Ozon API Key" value={apiKey} onChange={(e) => setApiKey(e.target.value)} required />
            </>
          ) : (
            <input placeholder="WB Token" value={wbToken} onChange={(e) => setWbToken(e.target.value)} required />
          )}

          {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}
          <button type="submit">Сохранить и проверить подключение</button>
        </form>
      </div>

      <div className="card">
        <h2>Список магазинов</h2>
        {loading ? <p>Загрузка...</p> : null}
        <div className="grid">
          {stores.map((store) => (
            <div key={store.id} className="card" style={{ margin: 0 }}>
              <b>{store.name}</b> ({store.marketplace})
              <p>Статус: {store.connection_status}</p>
              <p>Последняя синхронизация: {store.last_sync_at || 'ещё не было'}</p>
            </div>
          ))}
          {!stores.length && !loading ? <p>Пока нет магазинов.</p> : null}
        </div>
      </div>
    </>
  )
}
