import Link from 'next/link'

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
  return (
    <div className="card" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
      {links.map(([label, href]) => (
        <Link key={href} href={href}>
          {label}
        </Link>
      ))}
    </div>
  )
}
