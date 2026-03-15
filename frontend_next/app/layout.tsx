import './globals.css'
import { Nav } from '@/components/Nav'

export const metadata = {
  title: 'Seller MVP',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <div className="container">
          <Nav />
          {children}
        </div>
      </body>
    </html>
  )
}
