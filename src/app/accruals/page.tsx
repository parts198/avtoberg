import { getAccrualsOverview } from '@/lib/db/accruals';

export default async function AccrualsPage() {
  const rows = await getAccrualsOverview();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Начисления / Заказы / Факт vs План</h1>
        <p className="text-sm text-slate-600">
          Для каждого posting_number фиксируется плановый слепок и отображается фактическая маржа.
        </p>
      </div>
      <div className="rounded border border-slate-200 bg-white">
        <div className="grid grid-cols-[200px_100px_120px_120px_120px_120px] gap-4 border-b border-slate-200 px-4 py-3 text-xs font-semibold uppercase text-slate-500">
          <span>Posting</span>
          <span>Схема</span>
          <span>Факт маржа</span>
          <span>План маржа</span>
          <span>Факт %</span>
          <span>План %</span>
        </div>
        {rows.length === 0 ? (
          <div className="px-4 py-6 text-sm text-slate-500">Нет заказов.</div>
        ) : (
          rows.map((row) => (
            <div
              key={row.postingNumber}
              className="grid grid-cols-[200px_100px_120px_120px_120px_120px] gap-4 border-b border-slate-100 px-4 py-3 text-xs"
            >
              <span className="font-medium">{row.postingNumber}</span>
              <span>{row.scheme}</span>
              <span>{row.factMarginRub ?? '—'}</span>
              <span>{row.planMarginRub ?? '—'}</span>
              <span>{row.factMarginPct ?? '—'}%</span>
              <span>{row.planMarginPct ?? '—'}%</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
