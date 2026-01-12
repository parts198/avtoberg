import { PrismaClient } from '@prisma/client';
import { encryptSecret } from '../src/lib/crypto.js';

const prisma = new PrismaClient();

async function main() {
  const demoClientId = process.env.OZON_CLIENT_ID;
  const demoApiKey = process.env.OZON_API_KEY;

  if (demoClientId && demoApiKey) {
    const apiKeyEnc = encryptSecret(demoApiKey);
    await prisma.store.upsert({
      where: { clientId: demoClientId },
      update: {},
      create: {
        name: 'Demo Store',
        clientId: demoClientId,
        apiKeyEnc,
        defaults: {
          create: {},
        },
      },
    });
  }

  const existingPage = await prisma.page.findFirst({ where: { slug: 'welcome' } });
  if (!existingPage) {
    await prisma.page.create({
      data: {
        title: 'Welcome',
        slug: 'welcome',
        markdownContent: 'Добро пожаловать в Ozon Margin Dashboard.',
      },
    });
  }
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
