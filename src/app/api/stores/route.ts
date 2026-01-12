import { NextResponse } from 'next/server';
import { createStore } from '@/lib/db/stores';

export async function POST(request: Request) {
  const form = await request.formData();
  const name = String(form.get('name') ?? '').trim();
  const clientId = String(form.get('clientId') ?? '').trim();
  const apiKey = String(form.get('apiKey') ?? '').trim();

  if (!name || !clientId || !apiKey) {
    return NextResponse.redirect(new URL('/stores?error=missing', request.url));
  }

  await createStore({ name, clientId, apiKey });

  return NextResponse.redirect(new URL('/stores', request.url));
}
