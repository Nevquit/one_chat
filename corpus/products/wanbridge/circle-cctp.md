
# Circle CCTP

Circle's [Cross-Chain Transfer Protocol](https://www.circle.com/pressroom/circle-delivers-usdc-interoperability-across-ecosystems-with-mainnet-launch-of-cross-chain-transfer-protocol) (CCTP) is a permissionless on-chain utility that facilitates USDC transfers between blockchains via native burning and minting. CCTP eliminates the need for bridges to lock assets during cross-chain transfers. With CCTP:

1. USDC is burned on the source chain
2. A signed attestation is fetched from Circle
3. USDC in minted on the destination chain

Wanchain served as a launch partner during the initial launch of CCTP in 2023. Since then. CCTP has been integrated seamlessly in [<mark style="color:blue;">WanBridge</mark>](https://bridge.wanchain.org/). When a user initiates USDC cross-chain transfers using the [<mark style="color:blue;">WanBridge</mark>](https://bridge.wanchain.org/), the bridge will default to CCTP if it is available. If CCTP is not available, the bridge will use [<mark style="color:blue;">WanBridge</mark>](https://bridge.wanchain.org/)’s standard lock, mint, burn, and unlock mechanisms.&#x20;

## Supported Chains

|   Mainnet   | CCTP V1 | CCTP V2 |
| :---------: | :-----: | :-----: |
|   Arbitrum  |    ✅    |    ✅    |
|  Avalanche  |    ✅    |    ✅    |
|     Base    |    ✅    |    ✅    |
|   Ethereum  |    ✅    |    ✅    |
|    Linea    |    🚫   |    ✅    |
|    Noble    |    ✅    |    🚫   |
|  Op Mainnet |    ✅    |    ✅    |
|   Polygon   |    ✅    |    ✅    |
|     Sei     |    🚫   |    ✅    |
|    Solana   |    ✅    |    🚫   |
|    Sonic    |    🚫   |    ✅    |
|     Sui     |    ✅    |    🚫   |
|   Unichain  |    🚫   |    ✅    |
| World Chain |    🚫   |    ✅    |
| XDC Network |    🚫   |    ✅    |
