import { prisma } from './prisma';

export async function getAccrualsOverview() {
  const postings = await prisma.posting.findMany({
    include: { items: true },
    take: 200,
  });

  return postings.map((posting) => ({
    postingNumber: posting.postingNumber,
    scheme: posting.scheme,
    factMarginRub: null,
    planMarginRub: null,
    factMarginPct: null,
    planMarginPct: null,
  }));
}
