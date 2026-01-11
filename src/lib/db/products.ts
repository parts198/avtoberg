import { prisma } from './prisma';
import { computeUnitEconomics } from '@/lib/calculations/calculations';

export async function getProductsSummary() {
  const products = await prisma.product.findMany({
    include: {
      economics: true,
      priceSnapshots: { take: 1, orderBy: { capturedAt: 'desc' } },
      store: { include: { defaults: true } },
    },
    take: 200,
  });

  return products.map((product) => {
    const defaults = product.store.defaults;
    const economics = product.economics;
    const priceRub = product.priceSnapshots[0]
      ? Number(product.priceSnapshots[0].priceRub)
      : null;

    if (!defaults) {
      return {
        sku: product.sku,
        priceRub,
      };
    }

    const computed = computeUnitEconomics({
      priceRub: priceRub ?? 0,
      costRub: Number(economics?.costRub ?? 0),
      acquiringPct: Number(economics?.acquiringPct ?? defaults.acquiringPct),
      commissionPct: Number(economics?.commissionPct ?? defaults.commissionPct),
      promo: {
        type: economics?.promoType ?? defaults.promoType ?? 'FIXED',
        value: Number(economics?.promoValue ?? defaults.promoValue ?? 0),
      },
      fixedCostsRub: {
        deliveryRub: Number(economics?.deliveryRub ?? defaults.deliveryRub),
        logisticsRub: Number(economics?.logisticsRub ?? defaults.logisticsRub),
        firstMileRub: Number(economics?.firstMileRub ?? defaults.firstMileRub),
        packagingRub: Number(economics?.packagingRub ?? defaults.packagingRub),
      },
    });

    return {
      sku: product.sku,
      priceRub,
      acquiringPct: computed.acquiringPct,
      commissionPct: computed.commissionPct,
      deliveryRub: computed.fixedCostsRub.deliveryRub,
      logisticsRub: computed.fixedCostsRub.logisticsRub,
      firstMileRub: computed.fixedCostsRub.firstMileRub,
      packagingRub: computed.fixedCostsRub.packagingRub,
      promoValue: computed.promoRub,
      commissionRub: computed.commissionRub,
      costRub: Number(economics?.costRub ?? 0),
      ozonTotalRub: computed.ozonTotalRub,
      payoutRub: computed.payoutRub,
      marginRub: computed.marginRub,
      marginPct: computed.marginPct,
      stockFbs: null,
      stockFbo: null,
    };
  });
}
