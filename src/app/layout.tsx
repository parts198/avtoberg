import './globals.css';
import type { ReactNode } from 'react';
import Link from 'next/link';
import { getPages } from '@/lib/db/pages';

export const metadata = {
  title: 'Ozon Margin Dashboard',
  description: 'API-first unit economics dashboard for Ozon sellers.',
};

const navigation = [
  { href: '/', label: 'Обзор' },
  { href: '/stores', label: 'Магазины' },
  { href: '/products', label: 'Товары' },
  { href: '/accruals', label: 'Начисления' },
  { href: '/pages', label: 'Страницы' },
];

export default async function RootLayout({ children }: { children: ReactNode }) {
  const pages = await getPages();

  return (
    <html lang="ru">
      <body>
        <div className="min-h-screen flex">
          <aside className="w-60 bg-white border-r border-slate-200 p-4">
            <div className="text-lg font-semibold mb-6">Ozon Margin</div>
            <nav className="space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block rounded px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
                >
                  {item.label}
                </Link>
              ))}
              {pages.length > 0 && (
                <div className="pt-4 text-xs font-semibold uppercase text-slate-400">Pages</div>
              )}
              {pages.map((page) => (
                <Link
                  key={page.id}
                  href={`/pages/${page.slug}`}
                  className="block rounded px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
                >
                  {page.title}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="flex-1 p-6">
            <div className="max-w-6xl mx-auto">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
