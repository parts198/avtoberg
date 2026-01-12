import { NextResponse } from 'next/server';
import { deleteStore } from '@/lib/db/stores';

export async function POST(request: Request, { params }: { params: { id: string } }) {
  await deleteStore(params.id);
  return NextResponse.redirect(new URL('/stores', request.url));
}
