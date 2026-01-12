import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { decryptSecret } from '@/lib/crypto';
import { fetchWarehouseList } from '@/lib/ozon/ozonClient';

export async function POST(request: Request, { params }: { params: { id: string } }) {
  const store = await prisma.store.findUnique({ where: { id: params.id } });
  if (!store) {
    return NextResponse.redirect(new URL('/stores?error=notfound', request.url));
  }

  try {
    const apiKey = decryptSecret(store.apiKeyEnc);
    await fetchWarehouseList({ clientId: store.clientId, apiKey });
    await prisma.store.update({
      where: { id: store.id },
      data: { lastError: null },
    });
  } catch (error) {
    await prisma.store.update({
      where: { id: store.id },
      data: { lastError: (error as Error).message },
    });
  }

  return NextResponse.redirect(new URL('/stores', request.url));
}
