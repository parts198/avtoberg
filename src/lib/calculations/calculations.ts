export type PromoInput = {
  type: 'PERCENT' | 'FIXED';
  value: number;
};

export type FixedCostsInput = {
  deliveryRub: number;
  logisticsRub: number;
  firstMileRub: number;
  packagingRub: number;
};

export type UnitEconomicsInput = {
  priceRub: number;
  costRub: number;
  acquiringPct: number;
  commissionPct: number;
  promo: PromoInput;
  fixedCostsRub: FixedCostsInput;
};

export type UnitEconomicsResult = {
  priceRub: number;
  costRub: number;
  acquiringPct: number;
  commissionPct: number;
  promoRub: number;
  acquiringRub: number;
  commissionRub: number;
  ozonVariableRub: number;
  ozonFixedRub: number;
  ozonTotalRub: number;
  payoutRub: number;
  marginRub: number;
  marginPct: number;
  markupRub: number;
  fixedCostsRub: FixedCostsInput;
};

export function computeUnitEconomics(input: UnitEconomicsInput): UnitEconomicsResult {
  const promoRub =
    input.promo.type === 'PERCENT'
      ? (input.priceRub * input.promo.value) / 100
      : input.promo.value;

  const acquiringRub = (input.priceRub * input.acquiringPct) / 100;
  const commissionRub = (input.priceRub * input.commissionPct) / 100;
  const ozonVariableRub =
    acquiringRub + commissionRub + (input.promo.type === 'PERCENT' ? promoRub : 0);
  const ozonFixedRub =
    input.fixedCostsRub.deliveryRub +
    input.fixedCostsRub.logisticsRub +
    input.fixedCostsRub.firstMileRub +
    input.fixedCostsRub.packagingRub +
    (input.promo.type === 'FIXED' ? promoRub : 0);
  const ozonTotalRub = ozonVariableRub + ozonFixedRub;
  const payoutRub = input.priceRub - ozonTotalRub;
  const marginRub = payoutRub - input.costRub;
  const marginPct = input.priceRub === 0 ? 0 : (marginRub / input.priceRub) * 100;

  return {
    priceRub: input.priceRub,
    costRub: input.costRub,
    acquiringPct: input.acquiringPct,
    commissionPct: input.commissionPct,
    promoRub,
    acquiringRub,
    commissionRub,
    ozonVariableRub,
    ozonFixedRub,
    ozonTotalRub,
    payoutRub,
    marginRub,
    marginPct,
    markupRub: marginRub,
    fixedCostsRub: input.fixedCostsRub,
  };
}

export function recommendPriceByTargetMarginRub(
  base: Omit<UnitEconomicsInput, 'priceRub'>,
  targetMarginRub: number,
): number {
  const variablePct = (base.acquiringPct + base.commissionPct + (base.promo.type === 'PERCENT' ? base.promo.value : 0)) / 100;
  const fixedRub =
    base.fixedCostsRub.deliveryRub +
    base.fixedCostsRub.logisticsRub +
    base.fixedCostsRub.firstMileRub +
    base.fixedCostsRub.packagingRub +
    (base.promo.type === 'FIXED' ? base.promo.value : 0);
  const denominator = 1 - variablePct;
  if (denominator <= 0) {
    return 0;
  }
  return (base.costRub + fixedRub + targetMarginRub) / denominator;
}

export function recommendPriceByTargetMarginPct(
  base: Omit<UnitEconomicsInput, 'priceRub'>,
  targetMarginPct: number,
): number {
  const variablePct = (base.acquiringPct + base.commissionPct + (base.promo.type === 'PERCENT' ? base.promo.value : 0)) / 100;
  const m = targetMarginPct / 100;
  const fixedRub =
    base.fixedCostsRub.deliveryRub +
    base.fixedCostsRub.logisticsRub +
    base.fixedCostsRub.firstMileRub +
    base.fixedCostsRub.packagingRub +
    (base.promo.type === 'FIXED' ? base.promo.value : 0);
  const denominator = 1 - variablePct - m;
  if (denominator <= 0) {
    return 0;
  }
  return (base.costRub + fixedRub) / denominator;
}
