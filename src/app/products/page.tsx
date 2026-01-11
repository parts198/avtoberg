import { getProductsSummary } from '@/lib/db/products';

export default async function ProductsPage() {
  const rows = await getProductsSummary();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Товары / Юнит-экономика</h1>
        <p className="text-sm text-slate-600">
          Таблица поддерживает редактирование себестоимости и расчёт рекомендованной цены.
        </p>
      </div>
      <div className="rounded border border-slate-200 bg-white overflow-hidden">
        <div className="grid grid-cols-[140px_repeat(5,120px)_repeat(5,140px)_120px_120px_140px_140px] gap-2 border-b border-slate-200 px-4 py-3 text-[11px] font-semibold uppercase text-slate-500">
          <span>Артикул</span>
          <span>Цена</span>
          <span>Эквайринг</span>
          <span>Доставка</span>
          <span>Логистика</span>
          <span>Первая миля</span>
          <span>Упаковка</span>
          <span>Продвижение</span>
          <span>Комиссия %</span>
          <span>Комиссия ₽</span>
          <span>Себестоимость</span>
          <span>Затраты FBS</span>
          <span>К выплате</span>
          <span>Наценка</span>
          <span>Маржа %</span>
          <span>FBS остаток</span>
          <span>FBO остаток</span>
        </div>
        {rows.length === 0 ? (
          <div className="px-4 py-6 text-sm text-slate-500">Нет товаров. Запустите синхронизацию.</div>
        ) : (
          rows.map((row) => (
            <div
              key={row.sku}
              className="grid grid-cols-[140px_repeat(5,120px)_repeat(5,140px)_120px_120px_140px_140px] gap-2 border-b border-slate-100 px-4 py-3 text-xs"
            >
              <span className="font-medium">{row.sku}</span>
              <span>{row.priceRub ?? '—'}</span>
              <span>{row.acquiringPct ?? '—'}%</span>
              <span>{row.deliveryRub ?? '—'}</span>
              <span>{row.logisticsRub ?? '—'}</span>
              <span>{row.firstMileRub ?? '—'}</span>
              <span>{row.packagingRub ?? '—'}</span>
              <span>{row.promoValue ?? '—'}</span>
              <span>{row.commissionPct ?? '—'}%</span>
              <span>{row.commissionRub ?? '—'}</span>
              <span>{row.costRub ?? '—'}</span>
              <span>{row.ozonTotalRub ?? '—'}</span>
              <span>{row.payoutRub ?? '—'}</span>
              <span>{row.marginRub ?? '—'}</span>
              <span>{row.marginPct ?? '—'}%</span>
              <span>{row.stockFbs ?? '—'}</span>
              <span>{row.stockFbo ?? '—'}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
