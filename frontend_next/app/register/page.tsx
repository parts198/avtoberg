'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'

import { apiFetch, setToken } from '@/lib/api'

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')

    const passwordBytes = new TextEncoder().encode(password).length
    if (passwordBytes > 72) {
      setError('Пароль слишком длинный для bcrypt (максимум 72 байта).')
      return
    }

    setLoading(true)
    try {
      const data = await apiFetch<{ access_token: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setToken(data.access_token)
      router.push('/stores')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка регистрации')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h1>Регистрация</h1>
      <form onSubmit={onSubmit} className="grid" style={{ maxWidth: 420 }}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input
          placeholder="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
        {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}
        <button disabled={loading}>{loading ? 'Создаём...' : 'Зарегистрироваться'}</button>
      </form>
    </div>
  )
}
