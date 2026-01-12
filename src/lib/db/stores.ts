import { prisma } from './prisma';
import { encryptSecret } from '@/lib/crypto';

export async function getStores() {
  return prisma.store.findMany({ orderBy: { createdAt: 'desc' } });
}

export async function createStore(data: {
  name: string;
  clientId: string;
  apiKey: string;
}) {
  const apiKeyEnc = encryptSecret(data.apiKey);
  return prisma.store.create({
    data: {
      name: data.name,
      clientId: data.clientId,
      apiKeyEnc,
      defaults: {
        create: {},
      },
    },
  });
}

export async function deleteStore(storeId: string) {
  return prisma.store.delete({ where: { id: storeId } });
}
