import { describe, expect, it } from 'vitest';
import { computeUnitEconomics, recommendPriceByTargetMarginPct, recommendPriceByTargetMarginRub } from './calculations';

describe('computeUnitEconomics', () => {
  it('calculates key outputs', () => {
    const result = computeUnitEconomics({
      priceRub: 1000,
      costRub: 400,
      acquiringPct: 2,
      commissionPct: 12,
      promo: { type: 'PERCENT', value: 5 },
      fixedCostsRub: { deliveryRub: 50, logisticsRub: 30, firstMileRub: 20, packagingRub: 10 },
    });

    expect(result.acquiringRub).toBeCloseTo(20);
    expect(result.commissionRub).toBeCloseTo(120);
    expect(result.promoRub).toBeCloseTo(50);
    expect(result.ozonFixedRub).toBeCloseTo(110);
    expect(result.payoutRub).toBeCloseTo(700);
    expect(result.marginRub).toBeCloseTo(300);
  });
});

describe('recommendPrice', () => {
  it('calculates price from target margin rub', () => {
    const price = recommendPriceByTargetMarginRub(
      {
        costRub: 400,
        acquiringPct: 2,
        commissionPct: 12,
        promo: { type: 'PERCENT', value: 5 },
        fixedCostsRub: { deliveryRub: 50, logisticsRub: 30, firstMileRub: 20, packagingRub: 10 },
      },
      300,
    );

    expect(price).toBeGreaterThan(0);
  });

  it('calculates price from target margin pct', () => {
    const price = recommendPriceByTargetMarginPct(
      {
        costRub: 400,
        acquiringPct: 2,
        commissionPct: 12,
        promo: { type: 'PERCENT', value: 5 },
        fixedCostsRub: { deliveryRub: 50, logisticsRub: 30, firstMileRub: 20, packagingRub: 10 },
      },
      20,
    );

    expect(price).toBeGreaterThan(0);
  });
});
