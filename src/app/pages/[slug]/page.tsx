import { getPageBySlug } from '@/lib/db/pages';

export default async function PageDetail({ params }: { params: { slug: string } }) {
  const page = await getPageBySlug(params.slug);

  if (!page) {
    return <div className="text-sm text-slate-500">Страница не найдена.</div>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{page.title}</h1>
      <pre className="whitespace-pre-wrap rounded border border-slate-200 bg-white p-4 text-sm">
        {page.markdownContent}
      </pre>
    </div>
  );
}
