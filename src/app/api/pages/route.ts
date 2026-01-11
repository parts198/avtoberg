import { NextResponse } from 'next/server';
import { createPage } from '@/lib/db/pages';

export async function POST(request: Request) {
  const form = await request.formData();
  const title = String(form.get('title') ?? '').trim();
  const slug = String(form.get('slug') ?? '').trim();
  const markdownContent = String(form.get('content') ?? '').trim();

  if (!title || !slug) {
    return NextResponse.redirect(new URL('/pages?error=missing', request.url));
  }

  await createPage({ title, slug, markdownContent });

  return NextResponse.redirect(new URL('/pages', request.url));
}
