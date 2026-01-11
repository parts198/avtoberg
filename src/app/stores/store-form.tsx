'use client';

import { useState } from 'react';

export default function StoreForm() {
  const [loading, setLoading] = useState(false);

  return (
    <form
      action="/api/stores"
      method="post"
      className="rounded border border-slate-200 bg-white p-4"
      onSubmit={() => setLoading(true)}
    >
      <div className="grid gap-4 md:grid-cols-3">
        <label className="text-sm">
          <span className="block text-xs text-slate-500">Название</span>
          <input
            name="name"
            required
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm"
            placeholder="Main Store"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-slate-500">Client-Id</span>
          <input
            name="clientId"
            required
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-slate-500">API Key</span>
          <input
            name="apiKey"
            type="password"
            required
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm"
          />
        </label>
      </div>
      <div className="mt-4 flex justify-end">
        <button
          disabled={loading}
          className="rounded bg-slate-900 px-4 py-2 text-sm text-white"
        >
          {loading ? 'Сохраняем...' : 'Добавить магазин'}
        </button>
      </div>
    </form>
  );
}
