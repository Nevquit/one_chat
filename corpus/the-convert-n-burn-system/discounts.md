
# Discounts

Users can stake or hold WAN coins to receive discounts on cross-chain transactions. Discounts function differently depending on the type of network involved in any given cross-chain transaction. In short: the more WAN you have, the greater the discount.

## Transactions from EVM networks

For cross-chain transactions from EVM networks (i.e., from Ethereum), if either the sending or the receiving address has at least 10,000 [WAN coins](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) on the [Wanchain L1 blockchain](broken://pages/ZiJoxkixshZnOyHGATRR), you will receive a discount on the [Service Fee](https://docs.wanchain.org/the-convert-n-burn-system/bridge-fees.md). The address’ [WAN coin](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) balance on the [Wanchain L1 blockchain](broken://pages/ZiJoxkixshZnOyHGATRR) and any [WAN coin](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) that it has [staked/delegated to a Wanchain Bridge Node](https://docs.wanchain.org/products/xstake.md) are counted. Discounts are tiered as follows:

|   Threshold   | Service Fee Discount |
| :-----------: | :------------------: |
|   10,000 WAN  |          10%         |
|   25,000 WAN  |          25%         |
|   50,000 WAN  |          50%         |
|  100,000 WAN  |          60%         |
|  500,000 WAN  |          70%         |
| 1,000,000 WAN |          80%         |

## Transactions from non-EVM networks

For cross-chain transactions from non-EVM networks (i.e., from Bitcoin), if the receiving address has at least 10,000 [WAN coins](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) on the [Wanchain L1 blockchain](broken://pages/ZiJoxkixshZnOyHGATRR), you will receive a discount on the [Service Fee](https://docs.wanchain.org/the-convert-n-burn-system/bridge-fees.md). The address’ [WAN coin](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) balance on the [Wanchain L1 blockchain](broken://pages/ZiJoxkixshZnOyHGATRR) and any [WAN coin](https://docs.wanchain.org/cross-chain-infrastructure/wan-coin.md) that it has [staked/delegated to a Wanchain Bridge Node](https://docs.wanchain.org/products/xstake.md) are counted. Discounts are tiered as follows:

|   Threshold   | Service Fee Discount |
| :-----------: | :------------------: |
|   10,000 WAN  |          10%         |
|   25,000 WAN  |          25%         |
|   50,000 WAN  |          50%         |
|  100,000 WAN  |          60%         |
|  500,000 WAN  |          70%         |
| 1,000,000 WAN |          80%         |

## The Fineprint

* The discount also applies to the Service Fee’s lower and upper limits. Without the discount, the lower and upper limits are set to $0.2 and $100, respectively. With a 50% discount applied, the lower and upper limits would be $0.1 and $50.
* While both an address’ WAN balance on the Wanchain L1 blockchain and any WAN that it has staked/delegated to a Wanchain Bridge Node count towards the discount thresholds, WAN staked in PoS Validator Nodes and WAN bridged to other networks are not included.
