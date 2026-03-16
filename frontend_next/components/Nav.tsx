'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

import { clearToken, getToken } from '@/lib/api'

const links = [
  ['Регистрация', '/register'],
  ['Вход', '/login'],
  ['Магазины', '/stores'],
  ['Заказы', '/orders'],
  ['Цены', '/prices'],
  ['FBO', '/fbo'],
  ['Аналитика', '/analytics'],
  ['Остатки и возвраты', '/stocks-returns'],
]

export function Nav() {
  const router = useRouter()
  const [isAuthorized, setIsAuthorized] = useState(false)

  useEffect(() => {
    setIsAuthorized(Boolean(getToken()))
  }, [])

  const handleLogout = () => {
    clearToken()
    router.push('/login')
  }

  return (
    <div className="card" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
      {links.map(([label, href]) => (
        <Link key={href} href={href}>
          {label}
        </Link>
      ))}
      {isAuthorized && (
        <button type="button" onClick={handleLogout}>
          Выход
        </button>
      )}
    </div>
  )
}
