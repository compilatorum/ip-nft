export const PRICING = {
  percentFeePctDefault: 0.0015, // 0.15%
  percentFeePctOptions: [0.001, 0.0015, 0.003], // 0.10%, 0.15%, 0.30%
  flatFeeUsdcDefault: 1.0,
  flatFeeVerifiedUsdc: 0.5,
  minFeeUsdc: 0.1,
  maxFeePctCap: 0.01, // 1%
  feeCurrency: 'USDC',
  antiSpam: {
    defaultRateLimitPerMin: 10,
    spikeThresholdPerHour: 50,
    elevatedFlatFeeUsdc: 3.0,
  },
};
