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
  const [creating, setCreating] = useState(false)

  const [editingStoreId, setEditingStoreId] = useState<number | null>(null)
  const [editClientId, setEditClientId] = useState('')
  const [editApiKey, setEditApiKey] = useState('')
  const [editWbToken, setEditWbToken] = useState('')
  const [editing, setEditing] = useState(false)
  const [deletingStoreId, setDeletingStoreId] = useState<number | null>(null)

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
    if (creating) return
    setError('')
    setCreating(true)

    const credentials = marketplace === 'ozon' ? { client_id: clientId, api_key: apiKey } : { token: wbToken }

    try {
      await apiFetch('/stores', {
        method: 'POST',
        body: JSON.stringify({ name, marketplace, credentials }),
      })
      setName('')
      setClientId('')
      setApiKey('')
      setWbToken('')
      await loadStores()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания магазина')
    } finally {
      setCreating(false)
    }
  }

  function openEdit(store: Store) {
    setEditingStoreId(store.id)
    setEditClientId('')
    setEditApiKey('')
    setEditWbToken('')
  }

  async function submitEdit(e: FormEvent, store: Store) {
    e.preventDefault()
    if (editing) return
    setError('')
    setEditing(true)

    const credentials =
      store.marketplace === 'ozon' ? { client_id: editClientId, api_key: editApiKey } : { token: editWbToken }

    try {
      await apiFetch(`/stores/${store.id}/credentials`, {
        method: 'PATCH',
        body: JSON.stringify({ credentials }),
      })
      setEditingStoreId(null)
      await loadStores()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка изменения ключей')
    } finally {
      setEditing(false)
    }
  }

  async function deleteStore(storeId: number) {
    if (deletingStoreId) return
    if (!window.confirm('Удалить магазин?')) return

    setDeletingStoreId(storeId)
    setError('')
    try {
      await apiFetch(`/stores/${storeId}`, { method: 'DELETE' })
      await loadStores()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления магазина')
    } finally {
      setDeletingStoreId(null)
    }
  }

  return (
    <>
      <div className="card">
        <h1>Магазины</h1>
        <p>Список, добавление, изменение ключей и мягкое удаление магазинов.</p>
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
          <button type="submit" disabled={creating}>{creating ? 'Сохраняем...' : 'Сохранить и проверить подключение'}</button>
        </form>
      </div>

      <div className="card">
        <h2>Список магазинов</h2>
        {loading ? <p>Загрузка...</p> : null}
        <div className="grid">
          {stores.map((store) => (
            <div key={store.id} className="card" style={{ margin: 0 }}>
              <p><b>{store.name}</b></p>
              <p>Marketplace: {store.marketplace}</p>
              <p>Статус: {store.connection_status}</p>
              <p>Последняя синхронизация: {store.last_sync_at || 'ещё не было'}</p>

              <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <button type="button" onClick={() => openEdit(store)} disabled={editing || creating || !!deletingStoreId}>
                  Изменить ключи
                </button>
                <button
                  type="button"
                  onClick={() => deleteStore(store.id)}
                  disabled={editing || creating || deletingStoreId === store.id}
                >
                  {deletingStoreId === store.id ? 'Удаляем...' : 'Удалить'}
                </button>
              </div>

              {editingStoreId === store.id ? (
                <form onSubmit={(e) => submitEdit(e, store)} className="grid" style={{ maxWidth: 520 }}>
                  {store.marketplace === 'ozon' ? (
                    <>
                      <input
                        placeholder="Новый Ozon Client ID"
                        value={editClientId}
                        onChange={(e) => setEditClientId(e.target.value)}
                        required
                      />
                      <input
                        placeholder="Новый Ozon API Key"
                        value={editApiKey}
                        onChange={(e) => setEditApiKey(e.target.value)}
                        required
                      />
                    </>
                  ) : (
                    <input
                      placeholder="Новый WB Token"
                      value={editWbToken}
                      onChange={(e) => setEditWbToken(e.target.value)}
                      required
                    />
                  )}
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button type="submit" disabled={editing}>{editing ? 'Сохраняем...' : 'Сохранить ключи'}</button>
                    <button type="button" onClick={() => setEditingStoreId(null)} disabled={editing}>Отмена</button>
                  </div>
                </form>
              ) : null}
            </div>
          ))}
          {!stores.length && !loading ? <p>Пока нет магазинов.</p> : null}
        </div>
      </div>
    </>
  )
}
