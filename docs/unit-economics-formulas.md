# Unit Economics Formulas

## Входные параметры
- `priceRub`
- `costRub`
- `acquiringPct`
- `commissionPct`
- `promo`: процент или фикс
- `fixedCostsRub`: доставка, логистика, первая миля, упаковка, фикс. промо

## Выходные метрики
- `acquiringRub = priceRub * acquiringPct / 100`
- `commissionRub = priceRub * commissionPct / 100`
- `promoRub = priceRub * promoPct / 100` или `promoFixed`
- `ozonVariableRub = acquiringRub + commissionRub + promoRub` (только при promo %)
- `ozonFixedRub = deliveryRub + logisticsRub + firstMileRub + packagingRub (+ promoFixed)` (если promo фикс)
- `ozonTotalRub = ozonVariableRub + ozonFixedRub`
- `payoutRub = priceRub - ozonTotalRub`
- `marginRub = payoutRub - costRub`
- `marginPct = marginRub / priceRub * 100`
- `markupRub = marginRub`

## Обратный расчёт цены
### По targetMarginRub
```
price = (costRub + ozonFixedRub + targetMarginRub)
        / (1 - (acquiringPct + commissionPct + promoPct) / 100)
```

### По targetMarginPct
```
price = (costRub + ozonFixedRub)
        / (1 - (acquiringPct + commissionPct + promoPct) / 100 - targetMarginPct/100)
```

## Округление
Хранить как Decimal, вывод — до 2 знаков, цена — до целых или 2 знаков (настройка магазина).
