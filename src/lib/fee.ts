import { PRICING } from '../config/pricing';

export type FeeModel = 'A_counted_exec' | 'B_notcounted_exec' | 'C_charge_upfront' | 'F_flat_exec';

export function computeFee(amountUsdc: number, model: FeeModel, userIsVerified = false, ratePct?: number, flatFeeOverride?: number) {
  const pct = Math.min(ratePct ?? PRICING.percentFeePctDefault, PRICING.maxFeePctCap);
  const flatBase = userIsVerified ? PRICING.flatFeeVerifiedUsdc : PRICING.flatFeeUsdcDefault;
  const flatFee = flatFeeOverride !== undefined ? flatFeeOverride : flatBase;

  let fee = 0;
  if (model === 'F_flat_exec') {
    fee = flatFee;
  } else {
    fee = Math.max(PRICING.minFeeUsdc, amountUsdc * pct);
  }
  // enforce min/max
  if (fee < PRICING.minFeeUsdc) fee = PRICING.minFeeUsdc;
  if (fee > amountUsdc * PRICING.maxFeePctCap) fee = amountUsdc * PRICING.maxFeePctCap;
  return Number(fee.toFixed(6));
}

export function effectiveAmountForCheck(amountUsdc: number, model: FeeModel, fee: number) {
  if (model === 'A_counted_exec') return amountUsdc + fee;
  return amountUsdc;
}
