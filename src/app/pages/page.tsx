import { getPages } from '@/lib/db/pages';

export default async function PagesIndex() {
  const pages = await getPages();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Страницы</h1>
        <p className="text-sm text-slate-600">Markdown страницы для заметок и инструкций.</p>
      </div>
      <form action="/api/pages" method="post" className="rounded border border-slate-200 bg-white p-4">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="text-sm">
            <span className="block text-xs text-slate-500">Заголовок</span>
            <input name="title" required className="mt-1 w-full rounded border border-slate-200 px-3 py-2" />
          </label>
          <label className="text-sm">
            <span className="block text-xs text-slate-500">Slug</span>
            <input name="slug" required className="mt-1 w-full rounded border border-slate-200 px-3 py-2" />
          </label>
        </div>
        <label className="mt-4 block text-sm">
          <span className="block text-xs text-slate-500">Markdown</span>
          <textarea name="content" rows={6} className="mt-1 w-full rounded border border-slate-200 px-3 py-2" />
        </label>
        <div className="mt-4 flex justify-end">
          <button className="rounded bg-slate-900 px-4 py-2 text-sm text-white">Создать</button>
        </div>
      </form>
      <div className="rounded border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3 text-xs font-semibold uppercase text-slate-500">Созданные страницы</div>
        {pages.length === 0 ? (
          <div className="px-4 py-6 text-sm text-slate-500">Пока страниц нет.</div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {pages.map((page) => (
              <li key={page.id} className="px-4 py-3 text-sm">
                <a className="text-slate-900 underline" href={`/pages/${page.slug}`}>
                  {page.title}
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
