import { getStores } from '@/lib/db/stores';
import StoreForm from './store-form';

export default async function StoresPage() {
  const stores = await getStores();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Магазины</h1>
        <p className="text-sm text-slate-600">
          Добавьте несколько кабинетов Ozon и проверьте подключение через Seller API.
        </p>
      </div>
      <StoreForm />
      <div className="rounded border border-slate-200 bg-white">
        <div className="grid grid-cols-5 gap-4 border-b border-slate-200 px-4 py-3 text-xs font-semibold uppercase text-slate-500">
          <span>Название</span>
          <span>Client-Id</span>
          <span>Обновление</span>
          <span>Ошибка</span>
          <span></span>
        </div>
        {stores.length === 0 ? (
          <div className="px-4 py-6 text-sm text-slate-500">Магазины пока не добавлены.</div>
        ) : (
          stores.map((store) => (
            <div
              key={store.id}
              className="grid grid-cols-5 gap-4 border-b border-slate-100 px-4 py-3 text-sm"
            >
              <span className="font-medium">{store.name}</span>
              <span>{store.clientId}</span>
              <span>{store.updatedAt.toLocaleString('ru-RU')}</span>
              <span className="text-rose-600">{store.lastError ?? '—'}</span>
              <div className="flex gap-2 justify-end">
                <form action={`/api/stores/${store.id}/check`} method="post">
                  <button className="rounded border border-slate-200 px-3 py-1 text-xs">
                    Проверить подключение
                  </button>
                </form>
                <form action={`/api/stores/${store.id}/delete`} method="post">
                  <button className="rounded border border-rose-200 px-3 py-1 text-xs text-rose-600">
                    Удалить
                  </button>
                </form>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
