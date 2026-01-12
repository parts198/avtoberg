export default function HomePage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Обзор</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-medium text-slate-500">Data freshness</h2>
          <p className="text-lg font-semibold">Данные ещё не синхронизированы</p>
        </div>
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-medium text-slate-500">Ошибки синков</h2>
          <p className="text-lg font-semibold">Нет ошибок</p>
        </div>
      </div>
      <div className="rounded border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-medium text-slate-500">Explainability</h2>
        <p className="text-sm text-slate-600">
          В карточках товара и заказа будут доступны breakdown расходов и формулы расчёта.
        </p>
      </div>
    </div>
  );
}
