import { prisma } from './prisma';

export async function getPages() {
  return prisma.page.findMany({ orderBy: { createdAt: 'desc' } });
}

export async function createPage(data: { title: string; slug: string; markdownContent: string }) {
  return prisma.page.create({ data });
}

export async function getPageBySlug(slug: string) {
  return prisma.page.findUnique({ where: { slug } });
}
