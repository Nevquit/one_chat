
# XFlows API

## 1. Overview

### **What is XFlows?**

XFlows is Wanchain’s canonical cross-chain swap platform. It enables decentralized native-to-native asset swaps across multiple EVM and non-EVM networks.

### **Core Technical Features**

#### **Native-to-Native Transfers**

XFlows' standout feature is its ability to facilitate true native-to-native cross-chain asset conversions. This means users can move assets between different blockchains while maintaining their native properties, eliminating the need for wrapped tokens or other intermediary forms.

#### **Decentralized Liquidity Pool Mechanism**

The protocol leverages decentralized liquidity pools to provide liquidity support for cross-chain transfers. This design eliminates dependence on centralized exchanges, enhancing both security and decentralization of the system.

### **Technical Advantages**

#### **Non-Custodial Nature**

XFlows provides easy, non-custodial transfers, ensuring users maintain complete control over their assets throughout the entire cross-chain process without needing to custody assets with third parties.

#### **Cross-Chain Bridge Infrastructure**

The protocol leverages Wanchain's powerful cross-chain bridge technology to provide users with secure and efficient cross-chain experiences. As the world's original decentralized blockchain interoperability solution, Wanchain's technical foundation provides reliable support for XFlows.

### **Practical Use Cases**

XFlows is particularly suitable for users and developers who need to frequently move native assets between multiple blockchain networks. Through this protocol, users can:

* Achieve fast, cost-effective cross-chain asset swaps
* Maintain native asset properties
* Avoid complex wrapping and unwrapping processes
* Enjoy decentralized security guarantees

### **Market Impact and Innovation**

XFlows represents a significant innovation in Wanchain's cross-chain technology portfolio, contributing importantly to the development of Web3 ecosystem interoperability. The protocol addresses the growing need for seamless asset movement across different blockchain networks while maintaining security and decentralization principles.

The launch of XFlows demonstrates Wanchain's commitment to building comprehensive cross-chain infrastructure that empowers developers to build the future of Web3 applications with enhanced interoperability capabilities.

### Foundational Technology

XFlows is built using multiple decentralised cross-chain technologies. It also aggregates select existing cross-chain products. As shown in the figure below, XFlows leverages WanBridge, Wanchain’s decentralised, direct, non-custodial value-transfer bridge, and XPort, Wanchain’s cross-chain data transfer protocol, amongst others.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FwwOLKvejH4yx9UmfofPR%2Fimage.png?alt=media&amp;token=acd6746f-a86d-4e0c-b964-e2853a700154" alt=""><figcaption></figcaption></figure>

Cross-chain Swap Working Principle:

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FHGhl2KlnMCT6zbHP1gff%2FUntitled.png?alt=media&amp;token=ea8a5f75-782b-479b-aa4f-c2ecfd680350" alt=""><figcaption></figcaption></figure>

QUiX Working Principle:

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FdmVj0vsqLpV3fWiTZwnC%2Fimage%201.png?alt=media&amp;token=4dfb1355-4fa5-496b-86a4-86c16d6eda3a" alt=""><figcaption></figcaption></figure>

This document describes the interfaces and methods for accessing and using XFlows products through API-based integration.

XFlows supports six working modes:

1. A standard cross-chain bridge transaction to the target chain, using WanBridge;
2. A rapid cross-chain bridge transaction to the target chain, using QUiX;
3. A standard cross-chain bridge transaction to the target chain, followed by a swap on the target chain;
4. A standard cross-chain bridge transaction an intermediary chain (the Wanchain L1 blockchain), followed by a swap on the intermediary chain, followed by a standard cross-chain bridge transaction to the target chain;
5. A standard DEX swap on the Wanchain L1 blockchain or on other chains, using select 3rd party DEX aggregators;
6. A standard DEX swap on the Wanchain L1 blockchain, followed by a standard cross-chain bridge transaction to the target chain.

## 2. Quick Start

XFlows Cross-Chain Integration Process:

1. **Get Cross-Chain Asset Quote Information**
   * API Endpoint: <https://xflows.wanchain.org/api/v3/quote>
   * Purpose: Retrieve cross-chain support status and quote information for specified assets across different chains.
2. **Build Cross-Chain Transaction Data**
   * API Endpoint: <https://xflows.wanchain.org/api/v3/buildTx>
   * Purpose: Generate ready-to-use cross-chain swap transaction data based on user-selected cross-chain direction and parameters.
   * Usage: The returned data can be directly passed to the user's wallet for signing and execution.
3. **Query Cross-Chain Transaction Status**
   * API Endpoint: <https://xflows.wanchain.org/api/v3/status>
   * Purpose: Track the execution progress of cross-chain transactions, including statuses such as initiated, processing, completed, or failed.
4. **Parameter Acquisition Methods for APIs**

| Parameter        | Description                                                                                                                                                                                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fromChainId      | Source chain ID, obtain the corresponding ChainID through API `https://xflows.wanchain.org/api/v3/supported/chains` (e.g., `1`: Ethereum)                                                                                                                              |
| toChainId        | Target chain ID, same acquisition method as fromChainId (e.g., `56`: BNB Smart Chain)                                                                                                                                                                                  |
| fromTokenAddress | Source token contract address (e.g., `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`). Obtain TokenAddress through API `https://xflows.wanchain.org/api/v3/supported/tokens`. Note: TokenAddress is the WanBridge-encoded tokenContractAddress, not the asciiTokenAddress |
| toTokenAddress   | Target token contract address (e.g., `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`). Same acquisition method as fromTokenAddress                                                                                                                                        |
| fromAddress      | Source chain wallet address, must be a valid user address that conforms to the corresponding chain's address format                                                                                                                                                    |
| toAddress        | Target chain wallet address, same requirements as source chain                                                                                                                                                                                                         |
| bridge           | Optional, specify a particular Bridge to use, default value is wanbridge, optional values include wanbridge or quix, obtain supported Bridges through API `https://xflows.wanchain.org/api/v3/supported/bridges`                                                       |
| dex              | Optional, specify a particular DEX to use, e.g., "wanchain" or "rubic", automatically selected by default, obtain supported Dex through API `https://xflows.wanchain.org/api/v3/supported/dexes`                                                                       |

5. **OpenAPI Specification**

The full OpenAPI specification is available at:

* Swagger UI：[https://xflows-open-api.wanscan.org](https://xflows-open-api.wanscan.org/)
* OpenAPI JSON：<https://xflows-open-api.wanscan.org/openapi.json> Use it to auto-generate types, clients, or import into tools like Postman.

**XFlows API Usage Demo:** <https://github.com/wandevs/xflows-api-demo>

## 3. Getting Supported Information

### 3.1 Getting Supported Chains

Get the information of the chain that supports cross-chain exchange, and return the target chain that supports cross-in by request.

**Request address**

**GET** `https://xflows.wanchain.org/api/v3/supported/chains`

**Request Parameters**

| Parameter | type    | Required | Description                                                                                                                                                                                            |
| --------- | ------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| chainId   | String  | No       | The unique identifier of the chain. Passing null returns all supported chains by default. Pass the id of the specified chain to return the information of the corresponding chain. e.g. `1`: Ethereum. |
| id        | String  | No       | Random number to identify the order of the request.                                                                                                                                                    |
| quix      | Boolean | No       | default is false, if pass true, then only return the quix supported chains.                                                                                                                            |

**Response Parameter**

| Parameter        | Type of parameter | Descripción                                          |
| ---------------- | ----------------- | ---------------------------------------------------- |
| chainId          | String            | Unique identifier of the chain. (e.g. `1`: Ethereum) |
| chainName        | String            | The name of the chain (e.g. `Optimism` ).            |
| String chainName | String            | Logo icon of the chain                               |
| symbol           | String            | Native coin symbol of the chain (e.g. `ETH` ).       |
| decimals         | Number            | Native coin decimals of the chain (e.g. `18` )       |
| chainType        | String            | chainType Tag for Wan Bridge                         |

**Example Request.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/chains
```

**Example Response.**

```jsx
{
  "success": true,
  "data": [
    {
      "chainId": 1,
      "chainName": "Ethereum",
      "logo": "https://xflows.wanchain.org/Chain/Ethereum.png",
      "symbol": "ETH",
      "chainType": "ETH"
    },
    {
      "chainId": 10,
      "chainName": "Optimism",
      "logo": "https://xflows.wanchain.org/Chain/Optimism.png",
      "symbol": "ETH",
      "chainType": "OETH"
    },
    ...
  ]
}
```

### 3.2 Get list of Tokens

Get the list of Tokens supported by XFlows.

**Request address**

GET `https://xflows.wanchain.org/api/v3/supported/tokens`

**Request Parameters**

| Parameters | Type of request | Required | Descripción                                                                                    |
| ---------- | --------------- | -------- | ---------------------------------------------------------------------------------------------- |
| chainId    | String          | No       | (e.g. `1`: Ethereum), if not fill this value, it will return all supported chain’s token list. |
| quix       | Boolean         | No       | default is false, if pass true, then only return the quix supported chains.                    |

**Response Parameters**

| Parameters           | Type   | Description                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| chainId              | Number | The ID of the chain used for the API request.                                           |
| decimals             | String | Currency precision (e.g.: `18` )                                                        |
| tokenContractAddress | String | The address of the token contract (e.g.: `0x382bb369d343125bfb2117af9c149795c6c65c50` ) |
| tokenLogoUrl         | String | Coin Logo (e.g. <https://xxxx/xxx.png>)                                                 |
| tokenName            | String | Full name of the token (e.g.: `Tether` )                                                |
| tokenSymbol          | String | Short name of the currency (e.g. `USDT` )                                               |
| asciiTokenAddress    | String | Only used for non-EVM address friendly display, no API input needed.                    |
| wanBridgeOnly        | Bool   | default: undefined; true: Only support cross-chain, not cross-chain Swap.               |

**Example Request #1.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/tokens?chainId=10
```

**Example Response #1.**

```jsx
{
  "success": true,
  "data": [
    {
      "decimals": "6",
      "tokenContractAddress": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
      "tokenLogoUrl": "https://xflows.wanchain.org/Token/USDT.png",
      "tokenName": "Tether USD",
      "tokenSymbol": "USDT",
      "asciiTokenAddress": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"
    },
    {
      "decimals": "6",
      "tokenContractAddress": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
      "tokenLogoUrl": "https://xflows.wanchain.org/Token/USDC.png",
      "tokenName": "usdc",
      "tokenSymbol": "USDC",
      "asciiTokenAddress": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"
    },
    {
      "decimals": "18",
      "tokenContractAddress": "0x0000000000000000000000000000000000000000",
      "tokenLogoUrl": "https://xflows.wanchain.org/Token/ETH.png",
      "tokenName": "ETH",
      "tokenSymbol": "ETH",
      "asciiTokenAddress": "0x0000000000000000000000000000000000000000"
    },
    {
      "decimals": "8",
      "tokenContractAddress": "0x68f180fcCe6836688e9084f035309E29Bf0A2095",
      "tokenLogoUrl": "https://xflows.wanchain.org/Token/WBTC.png",
      "tokenName": "Wrapped BTC",
      "tokenSymbol": "WBTC",
      "asciiTokenAddress": "0x68f180fcCe6836688e9084f035309E29Bf0A2095"
    }
  ]
}
```

**Example Request #2.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/tokens
```

**Example Response #2.**

```jsx
{
  "success": true,
  "data": [
    {
      "chainId": 1,
      "tokens": [
        {
          "decimals": "6",
          "tokenContractAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
          "tokenLogoUrl": "https://xflows.wanchain.org/Token/USDT.png",
          "tokenName": "Tether",
          "tokenSymbol": "USDT",
          "asciiTokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7"
        },
        {
          "decimals": "6",
          "tokenContractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
          "tokenLogoUrl": "https://xflows.wanchain.org/Token/USDC.png",
          "tokenName": "USDC",
          "tokenSymbol": "USDC",
          "asciiTokenAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        },
        ...
```

### 3.3 **Get a list of pairs that are only bridged via wan bridge**

Get a list of pairs that support cross-chaining (no swapping) directly via XFlows only.

**The request address is**

**GET** `https://xflows.wanchain.org/api/v3/supported/pairs`

**Request Parameters**

| Parameters  | Type   | Required | Description                   |
| ----------- | ------ | -------- | ----------------------------- |
| fromChainId | String | Yes      | Chain ID (e.g. `1`: Ethereum) |
| toChainId   | String | No       | Chain ID (e.g. `56`: BSC)     |

**Response Parameters**

| Parameters       | type        | Descripción                                                                                 |
| ---------------- | ----------- | ------------------------------------------------------------------------------------------- |
| fromChainId      | String      | Source chain ID (e.g. `1`: Ethereum, more can be obtained using the API)                    |
| toChainId        | String      | Destination chain ID (e.g. `1`: Ethereum, more can be obtained using API)                   |
| fromTokenAddress | String      | Address of the cryptocurrency contract (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` ) |
| toTokenAddress   | String      | Target currency contract address (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` )       |
| fromTokenSymbol  | String      | Short name of the source token (e.g. `USDC` )                                               |
| toTokenSymbol    | String      | Short name of the target token (e.g. `USDC` )                                               |
| tokenPairId      | tokenPairId | Token Pair ID of the WanBridge cross-chain.                                                 |
| symbol           | String      | Generic Symbol, Ancestor Coin Symbol                                                        |

**Example Request.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/pairs?fromChainId=56
```

**Example Response.**

```jsx
{
  "success": true,
  "data": [
    {
      "fromChainId": "56",
      "toChainId": "888",
      "fromTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
      "toTokenAddress": "0x11e77e27af5539872efed10abaa0b408cfd9fbbd",
      "fromTokenSymbol": "USDT",
      "toTokenSymbol": "wanUSDT",
      "tokenPairId": "184",
      "symbol": "USDT"
    },
    {
      "fromChainId": "56",
      "toChainId": "1",
      "fromTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
      "toTokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
      "fromTokenSymbol": "USDT",
      "toTokenSymbol": "USDT",
      "tokenPairId": "189",
      "symbol": "USDT"
    },
    {
      "fromChainId": "56",
      "toChainId": "137",
      "fromTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
      "toTokenAddress": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
      "fromTokenSymbol": "USDT",
      "toTokenSymbol": "USDT0",
      "tokenPairId": "200",
      "symbol": "USDT"
    },
    ...
  ]
}
```

### 3.4 Supported Bridges

Get the list of bridges supported by the XFlows API to perform cross-chain transactions.

**Request Address**

**GET** `https://xflows.wanchain.org/api/v3/supported/bridges`

**Request Parameters**

None.

**Response Parameters**

| Parameter | type   | Description |
| --------- | ------ | ----------- |
| key       | String | bridge key  |
| String    | String | bridge name |

**Example Request.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/bridges
```

**Example Response.**

```jsx
{
  "success": true,
  "data": [
    {
      "key": "wanbridge",
      "name": "WanBridge"
    },
    {
      "key": "quix",
      "name": "QUiX"
    }
  ]
}
```

### 3.5 Supported DEX

Get the list of supported DEXs for the current XFlows API execution transaction.

**Request Address**

**GET** `https://xflows.wanchain.org/api/v3/supported/dexes`

**Request Parameters**

None.

**Response Parameters**

| Parameter | type   | Description |
| --------- | ------ | ----------- |
| key       | String | dex key     |
| dex name  | name   | dex name    |

**Example Request.**

```jsx
GET https://xflows.wanchain.org/api/v3/supported/dexes
```

**Example Response.**

```jsx
{
  "success": true,
  "data": [
    {
      "key": "wanchain",
      "name": "Wanchain L1 Swap"
    },
    {
      "key": "rubic",
      "name": "Rubic"
    }
  ]
}
```

## 4. Query the best quote

Get the quote and fee information for a specified route.

### 4.1 Interface

**Request Address**

POST `https://xflows.wanchain.org/api/v3/quote`

**Request Parameters**

| Parameters       | Type   | Required | Description                                                                                          |
| ---------------- | ------ | -------- | ---------------------------------------------------------------------------------------------------- |
| id               | String | No       | Random number to be returned with the return value to identify the order of the request.             |
| fromChainId      | Number | Yes      | ID of the source chain (e.g. `1`: Ethereum, more can be retrieved using the API).                    |
| toChainId        | Number | Yes      | Destination Chain ID (e.g. `56`: BNB Smart Chain, more can be obtained using API)                    |
| fromTokenAddress | String | Yes      | The address of the requesting currency contract (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` ) |
| toTokenAddress   | String | Yes      | Target currency contract address (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` )                |
| fromAddress      | String | Yes      | Source chain wallet address                                                                          |
| toAddress        | String | Yes      | Destination chain wallet address                                                                     |
| fromAmount       | String | Yes      | fromAmount, e.g., "123.45"                                                                           |
| bridge           | String | No       | Optional, specify a bridge to use, e.g. "wanbridge" or "quix".                                       |
| dex              | No     | No       | Optional, specify a DEX to be used, e.g. "wanchain" or "rubic".                                      |
| slippage         | Number | No       | Optional, the maximum slippage allowed, default value is 0.01 (represents 1%)                        |

**Response Parameter**

| Parameter       | type   | Required | Descripción                                                                                                                                           |
| --------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| id              | String | No       | Random number, same as input, used to identify the order of request.                                                                                  |
| amountOut       | String | Yes      | The estimated number of tokens to be received. For example, "122.45".                                                                                 |
| amountOutRaw    | String | Yes      | The estimated amount of toToken received. The amount should include precision, e.g. 0.001 DAI returns: "1000000000000000".                            |
| slippage        | Number | Yes      | Same as the input value.                                                                                                                              |
| amountOutMin    | String | Yes      | The minimum amount of money that can be received after a slippage. For example, "120.45"                                                              |
| amountOutMinRaw | String | Yes      | The minimum amount of money that can be received after a slippage. The amount needs to include precision, e.g. 0.001 DAI returns: "1000000000000000". |
| priceImpact     | Number | Yes      | priceImpact, as a percentage, returns -1.3 for -1.3%                                                                                                  |
| approvalAddress | String | No       | The source chain needs to perform approval authorization for this address, if it is empty, no approval is needed.                                     |
| workMode        | Number | Yes      | Return Value:                                                                                                                                         |

1. directly cross the chain, go to wan-bridge;
2. directly cross the chain, go to quix;
3. cross the chain first, then do Swap on the target chain (e.g. cross to Wanchain);
4. cross the chain to Wanchain first, do Swap on Wanchain, then cross the chain to the target chain;
5. Swap only, e.g. do Swap on Wanchain. Swap only, e.g. Swap on Wanchain, or Swap on other chains based on Rubic (not supported by OKX or 1inch for now);
6. Swap first and then cross chain, e.g. Swap from Wanchain and cross out to other chains; (not supported by OKX or 1inch for now) | | bridge | String | No | Optional, specify the use of a certain Bridge, for example: "wanbridge" or "quix", if not fill in the default is wanbridge. | | dex | String | No | Use dex: wanchain, rubic | | error | String | No | If an error is returned, this field returns the error message. | | nativeFees | \[] | No | Stores information about the fees charged in Native Coin. | | nativeFeeAmount | String | No | The total amount of Native Coin Fees that need to be paid in the source chain, e.g. networkFee for Wan Bridge, message fee for XPort etc. The amount should include precision, e.g. 0.001 ETH returns: "1000000000000000". | | nativeFeeSymbol | String | No | Example: ETH | | nativeFeeDecimals | Number | No | Example: 18 | | tokenFees | \[] | No | Stores information about the fees charged in token. | | tokenFeeAmount | String | No | e.g. Quantity needs to include precision, e.g. 0.001 DAI returns: "1000000000000000". | | tokenFeeDecimals | Number | No | e.g. 18 | | tokenFeeContract | String | No | Example: `0xc02aaaa39b223fe8d0a0e5c4f27ead9083c756cc2` | | tokenFeeSymbol | String | No | e.g. USDT | | extraData | {} | No | Additional details. | | |- directPair | {} | No | If workMode is 1: cross-chain tokenPair information. | | |- quotaAndFee | {} | No | If workMode is 1: information about the remaining available cross-chain credit and common cross-chain fee rules for the current direction. | | |- minQuota | String | No | If workMode is 1: the minimum amount of cross-chain money. The amount should include precision, e.g. 0.001 ETH Return: "1000000000000000". | | |- maxQuota | String | No | If workMode is 1: the current maximum available cross-chain amount. Quantity needs to include precision, e.g. 0.001 USDT returns: "1000". | | |- networkFee | {} | No | extra info about native fee. | | |- serviceFee | {} | No | extra info about token fee. | | |- quix | {} | No | If workMode is 2: additional reference information for quix. | | |- dex | No {} | No | Additional reference information for dex. | | |- priceImpact | Number | No | The price impact of the dex. | | |- path | \[No] | No | The swap path and fee of the dex. |

### 4.2 Request Examples

#### **1) Example Request: (WorkMode 1)**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 43114,
  "toChainId": 56,
  "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
  "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "10"
}
```

**Example Response: (WorkMode 1)**

```jsx
{
  "success": true,
  "data": {
    "amountOut": "9.8",
    "amountOutRaw": "9800000000000000000",
    "slippage": 0.01,
    "amountOutMin": "9.8",
    "amountOutMinRaw": "9800000000000000000",
    "approvalAddress": "0x88888dd82A91f0406ED42BF750bAF881e64894F6",
    "priceImpact": 0,
    "workMode": 1,
    "bridge": "wanbridge",
    "nativeFees": [
      {
        "nativeFeeAmount": "6500000000000000",
        "nativeFeeSymbol": "AVAX",
        "nativeFeeDecimals": 18
      }
    ],
    "tokenFees": [
      {
        "tokenFeeAmount": "200000",
        "tokenFeeSymbol": "USDT",
        "tokenFeeDecimals": 18,
        "tokenFeeContract": "0x55d398326f99059ff775485246999027b3197955"
      }
    ],
    "extraData": {
      "directPair": {
        "fromChainId": "43114",
        "toChainId": "56",
        "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
        "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
        "fromTokenSymbol": "USDt",
        "toTokenSymbol": "USDT",
        "tokenPairId": "235",
        "symbol": "USDT"
      },
      "quotaAndFee": {
        "symbol": "USDT",
        "minQuota": "400000",
        "maxQuota": "61318064549",
        "networkFee": {
          "value": "6500000000000000",
          "isPercent": false
        },
        "operationFee": {
          "value": "0.002",
          "isPercent": true,
          "minFeeLimit": "200000",
          "maxFeeLimit": "100000000"
        }
      }
    }
  }
}
```

#### **2) Example Request: (WorkMode 2)**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 10,
  "toChainId": 56,
  "fromTokenAddress": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
  "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "10",
  "bridge": "quix"
}
```

**Example Response: (WorkMode 2)**

```jsx
{
  "success": true,
  "data": {
    "amountOut": "8",
    "amountOutRaw": "8000000000000000000",
    "slippage": 0.01,
    "amountOutMin": "8",
    "amountOutMinRaw": "8000000000000000000",
    "approvalAddress": "0x4bBcA1e55E99fF75a5F35152BAFE110F15123EA3",
    "priceImpact": 0,
    "workMode": 2,
    "bridge": "quix",
    "nativeFees": [
      {
        "nativeFeeAmount": "64000000000000",
        "nativeFeeSymbol": "ETH",
        "nativeFeeDecimals": 18
      }
    ],
    "tokenFees": [
      {
        "tokenFeeAmount": "2000000000000000000",
        "tokenFeeSymbol": "USDT",
        "tokenFeeDecimals": 18,
        "tokenFeeContract": "0x55d398326f99059ff775485246999027b3197955"
      }
    ],
    "extraData": {
      "quix": {
        "outAmount": "8",
        "fee": "2",
        "networkFee": "0.000064",
        "operationFee": "0.2",
        "walletChainId": 10,
        "intentInfo": {
          "intentType": 0,
          "nonce": "0",
          "fromChainId": "2147484262",
          "toChainId": "2147484362",
          "from": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "to": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "fromToken": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
          "fromAmount": "10000000",
          "toToken": "0x55d398326f99059ff775485246999027b3197955",
          "toAmount": "8000000000000000000",
          "relayer": "0x25309635Fd36CF2A85712B5be4f38Fa887e002CC",
          "deadline": "1756978402",
          "extraData": "0x000000000000000000000000000000000000000000000041726965735f303537000000000000000000000000000000000000000000000000000000000000017300000000000000000000000000000000000000000000000088009813ced40000"
        },
        "intentId": "0xf173c471c3ece5cbd8b925fe85fc39b8ee9623b74e59cea464f6dc27305714c2",
        "signature": "0x4da7b7e862169d100739dd047732b4c8f83cc9aabe0981e77ab38d6c4c6da80f2cb895262fd04f77471659174990f3ccbc05bffbd74887a029c1aea26af89f021b",
        "needApprove": true,
        "transactions": [
          {
            "to": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
            "data": "0x095ea7b30000000000000000000000004bbca1e55e99ff75a5f35152bafe110f15123ea30000000000000000000000000000000000000000000000000000000000989680"
          },
          {
            "to": "0x4bBcA1e55E99fF75a5F35152BAFE110F15123EA3",
            "data": "0x4f2ecca60000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000026000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000026600000000000000000000000000000000000000000000000000000000800002ca0000000000000000000000002fb4d46372ea1748ec3c29bd2c7b536019df52000000000000000000000000002fb4d46372ea1748ec3c29bd2c7b536019df520000000000000000000000000094b008aa00579c1307b0ef2c499ad98a8ce58e58000000000000000000000000000000000000000000000000000000000098968000000000000000000000000055d398326f99059ff775485246999027b31979550000000000000000000000000000000000000000000000006f05b59d3b20000000000000000000000000000025309635fd36cf2a85712b5be4f38fa887e002cc0000000000000000000000000000000000000000000000000000000068b95ce200000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000041726965735f303537000000000000000000000000000000000000000000000000000000000000017300000000000000000000000000000000000000000000000088009813ced4000000000000000000000000000000000000000000000000000000000000000000414da7b7e862169d100739dd047732b4c8f83cc9aabe0981e77ab38d6c4c6da80f2cb895262fd04f77471659174990f3ccbc05bffbd74887a029c1aea26af89f021b00000000000000000000000000000000000000000000000000000000000000",
            "value": "64000000000000"
          }
        ]
      }
    }
  }
}
```

#### **3) Example Request: (WorkMode 3) #1 Cross Swap to Wanchain**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 43114,
  "toChainId": 888,
  "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
  "toTokenAddress": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.001
}
```

**Example Request: (WorkMode 3) #1 Cross Swap to Wanchain**

```jsx
{
  "success": true,
  "data": {
    "amountOut": 990.745427,
    "amountOutRaw": "990745427",
    "slippage": 0.001,
    "amountOutMin": 989.754681573,
    "amountOutMinRaw": "989754682",
    "priceImpact": -0.6572,
    "approvalAddress": "0xAeCbF30602caF42467e7120C04271EDcC843f3c7",
    "workMode": 3,
    "bridge": "wanbridge",
    "dex": "wanchain",
    "nativeFees": [],
    "tokenFees": [],
    "extraData": {
      "dex": {
        "path": [
          [
            "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
            "0xdabD997aE5E4799BE47d6E69D9431615CBa28f48",
            "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b"
          ],
          [
            500,
            500
          ]
        ],
        "amountOut": "990745427",
        "priceImpact": 0.6572,
        "mode": "CrossSwapToWan",
        "params": {
          "fromChain": "0x80002328",
          "toChain": "0x8057414e",
          "fromToken": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
          "refundAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "fromAmount": "1000000000",
          "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "amountOutMin": "989754682",
          "wrappedFromToken": "0x11e77e27af5539872efed10abaa0b408cfd9fbbd",
          "wrappedToToken": "0x52a9cea01c4cbdd669883e41758b8eb8e8e2b34b",
          "smgID": "0x000000000000000000000000000000000000000000000041726965735f303537",
          "tokenPairID0": "233",
          "networkFee0": "0",
          "serviceFee0": "0",
          "crossType0": 0,
          "tokenPairID1": "80",
          "crossType1": 1,
          "messageFee": "13460135000000",
          "gasStation": 0,
          "swapFee0": 500,
          "swapFee1": 500
        },
        "fees": {
          "networkFee": "0",
          "serviceFee": "0",
          "discount": "1000000000000000000"
        }
      }
    }
  }
}
```

#### 4) **Example Request: (WorkMode 4)**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 43114,
  "toChainId": 10,
  "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
  "toTokenAddress": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.001
}
```

**Example Request: (WorkMode 4)**

```jsx
{
  "success": true,
  "data": {
    "amountOut": 986.728488,
    "amountOutRaw": "986728488",
    "slippage": 0.001,
    "amountOutMin": 985.7417595119999,
    "amountOutMinRaw": "985741760",
    "priceImpact": -0.6593,
    "approvalAddress": "0xAeCbF30602caF42467e7120C04271EDcC843f3c7",
    "workMode": 4,
    "bridge": "wanbridge",
    "dex": "wanchain",
    "nativeFees": [
      {
        "nativeFeeAmount": "13460135000000",
        "nativeFeeSymbol": "AVAX",
        "nativeFeeDecimals": 18
      },
      {
        "nativeFeeAmount": "290000000000000000",
        "nativeFeeSymbol": "WAN",
        "nativeFeeDecimals": 18
      }
    ],
    "tokenFees": [
      {
        "tokenFeeAmount": "3962765",
        "tokenFeeSymbol": "USDC",
        "tokenFeeDecimals": "6",
        "tokenFeeContract": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"
      }
    ],
    "extraData": {
      "dex": {
        "path": [
          [
            "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
            "0xdabD997aE5E4799BE47d6E69D9431615CBa28f48",
            "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b"
          ],
          [
            500,
            500
          ]
        ],
        "amountOut": "990691253",
        "priceImpact": 0.6593,
        "mode": "CrossSwap",
        "params": {
          "fromChain": "0x80002328",
          "toChain": "0x80000266",
          "fromToken": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
          "refundAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "fromAmount": "1000000000",
          "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "amountOutMin": "985741760",
          "wrappedFromToken": "0x11e77e27af5539872efed10abaa0b408cfd9fbbd",
          "wrappedToToken": "0x52a9cea01c4cbdd669883e41758b8eb8e8e2b34b",
          "smgID": "0x000000000000000000000000000000000000000000000041726965735f303537",
          "tokenPairID0": "233",
          "networkFee0": "0",
          "serviceFee0": "0",
          "crossType0": 0,
          "tokenPairID1": "557",
          "crossType1": 1,
          "messageFee": "13460135000000",
          "gasStation": 0,
          "swapFee0": 500,
          "swapFee1": 500
        },
        "fees": {
          "networkFee0": "0",
          "networkFee1": "290000000000000000",
          "serviceFee0": "0",
          "serviceFee1": "3962765",
          "discount": "1000000000000000000"
        }
      }
    }
  }
}
```

#### **5) Example Request: (WorkMode 5) #1 on Wanchain**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 888,
  "toChainId": 888,
  "fromTokenAddress": "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
  "toTokenAddress": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.02
}
```

**Example Response: (WorkMode 5) #1 on Wanchain**

```jsx
{
  "success": true,
  "data": {
    "amountOut": "991.933388",
    "amountOutRaw": "991933388",
    "slippage": 0.02,
    "amountOutMin": "972.09472",
    "amountOutMinRaw": "972094720",
    "priceImpact": -0.6476,
    "approvalAddress": "0xBc2e48073CE79553C4C8125878EeB7f8845975aa",
    "workMode": 5,
    "dex": "wanchain",
    "nativeFees": [],
    "tokenFees": [],
    "extraData": {
      "dex": {
        "path": [
          [
            "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
            "0xdabD997aE5E4799BE47d6E69D9431615CBa28f48",
            "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b"
          ],
          [
            500,
            500
          ]
        ],
        "amountOut": "991933388",
        "priceImpact": 0.6476
      }
    }
  }
}
```

**Example Request: (WorkMode 5) #2 on other EVM chains by Rubic**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 43114,
  "toChainId": 43114,
  "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
  "toTokenAddress": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.001
}
```

**Example Response: (WorkMode 5) #2**

```jsx
{
  "success": true,
  "data": {
    "amountOut": "999.642648",
    "amountOutRaw": "999642648",
    "slippage": 0.001,
    "amountOutMin": "998.643005",
    "amountOutMinRaw": "998643005",
    "priceImpact": -0.05,
    "approvalAddress": "0x3335733c454805df6a77f825f266e136FB4a3333",
    "workMode": 5,
    "dex": "rubic",
    "rubicId": "e63e6368-db2e-473e-ab33-1182d27d35d8",
    "nativeFees": [],
    "tokenFees": [],
    "extraData": {
      "dex": {
        "estimate": {
          "destinationTokenAmount": "999.642648",
          "destinationTokenMinAmount": "998.643005",
          "destinationUsdAmount": 999.49,
          "destinationUsdMinAmount": 998.5,
          "destinationWeiAmount": "999642648",
          "destinationWeiMinAmount": "998643005",
          "durationInMinutes": 5,
          "priceImpact": null,
          "slippage": 0.001
        },
        "fees": {
          "gasTokenFees": {
            "gas": {
              "baseFee": "809959425",
              "gasLimit": "1658354",
              "gasPrice": null,
              "maxFeePerGas": "1788282159",
              "maxPriorityFeePerGas": "168363309",
              "totalUsdAmount": 0.08,
              "totalWeiAmount": "2965605586819150"
            },
            "nativeToken": {
              "address": "0x0000000000000000000000000000000000000000",
              "blockchain": "AVALANCHE",
              "blockchainId": 43114,
              "decimals": 18,
              "name": "AVAX",
              "price": 24.11,
              "symbol": "AVAX"
            },
            "protocol": {
              "fixedAmount": "0",
              "fixedUsdAmount": 0,
              "fixedWeiAmount": "0"
            },
            "provider": {
              "fixedAmount": "0",
              "fixedUsdAmount": 0,
              "fixedWeiAmount": "0"
            }
          },
          "percentFees": {
            "percent": 0.05,
            "token": {
              "address": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
              "blockchain": "AVALANCHE",
              "blockchainId": 43114,
              "decimals": 6,
              "name": "TetherToken",
              "price": 1,
              "symbol": "USDt"
            }
          }
        },
        "providerType": "ONE_INCH",
        "routing": [
          {
            "path": [
              {
                "address": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
                "amount": "999.5",
                "blockchain": "AVALANCHE",
                "blockchainId": 43114,
                "decimals": 6,
                "name": "TetherToken",
                "symbol": "USDt",
                "price": 1
              },
              {
                "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
                "amount": "999.642648",
                "blockchain": "AVALANCHE",
                "blockchainId": 43114,
                "decimals": 6,
                "name": "USD Coin",
                "symbol": "USDC",
                "price": 1
              }
            ],
            "provider": "ONE_INCH",
            "type": "on-chain"
          }
        ],
        "swapType": "on-chain",
        "tokens": {
          "from": {
            "address": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
            "amount": "999.5",
            "blockchain": "AVALANCHE",
            "blockchainId": 43114,
            "decimals": 6,
            "name": "TetherToken",
            "price": 1,
            "symbol": "USDt"
          },
          "to": {
            "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
            "blockchain": "AVALANCHE",
            "blockchainId": 43114,
            "decimals": 6,
            "name": "USD Coin",
            "price": 1,
            "symbol": "USDC"
          }
        },
        "transaction": {
          "approvalAddress": "0x3335733c454805df6a77f825f266e136FB4a3333"
        },
        "useRubicContract": true,
        "warnings": [],
        "id": "e63e6368-db2e-473e-ab33-1182d27d35d8",
        "requestParams": {
          "dstTokenAddress": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
          "dstTokenBlockchain": "AVALANCHE",
          "referrer": "xflows.wanchain.org",
          "srcTokenAddress": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
          "srcTokenAmount": "1000",
          "srcTokenBlockchain": "AVALANCHE",
          "nativeBlacklist": [
            "lifi",
            "symbiosis",
            "xy",
            "squidrouter",
            "celer_bridge",
            "rango",
            "dln",
            "bridgers",
            "changenow",
            "orbiter_bridge",
            "meson",
            "owl_to_bridge",
            "arbitrum",
            "stargate_v2",
            "archon_bridge",
            "pulsechain_bridge",
            "router",
            "across",
            "retro_bridge",
            "unizen",
            "simple_swap",
            "changelly",
            "tele_swap",
            "xflows",
            "relay",
            "orbiter_bridge_v2",
            "wormhole",
            "exolix"
          ],
          "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "slippage": 0.001,
          "receiver": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "integratorAddress": "0x82bf94d159b15a587c45c9d70e0fab7fd87889eb"
        }
      }
    }
  }
}
```

#### **6) Example Request: (WorkMode 6)**

```jsx
POST https://xflows.wanchain.org/api/v3/quote
BODY
{
  "fromChainId": 888,
  "toChainId": 10,
  "fromTokenAddress": "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
  "toTokenAddress": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.001
}
```

**Example Response: (WorkMode 6)**

```jsx
{
  "success": true,
  "data": {
    "amountOut": "986.736558",
    "amountOutRaw": "986736558",
    "slippage": 0.001,
    "amountOutMin": 985.749821442,
    "amountOutMinRaw": "985749821",
    "priceImpact": -0.6518,
    "approvalAddress": "0x2d0217c700843Ba0CA44998d8C70e16b2a03B28f",
    "workMode": 6,
    "bridge": "wanbridge",
    "dex": "wanchain",
    "nativeFees": [],
    "tokenFees": [],
    "extraData": {
      "dex": {
        "path": [
          [
            "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
            "0xdabD997aE5E4799BE47d6E69D9431615CBa28f48",
            "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b"
          ],
          [
            500,
            500
          ]
        ],
        "amountOut": "990699355",
        "priceImpact": 0.6518,
        "mode": "CrossSwapFromWan",
        "params": {
          "fromChain": "0x8057414e",
          "toChain": "0x80000266",
          "fromToken": "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
          "refundAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "fromAmount": "1000000000",
          "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
          "amountOutMin": "985749821",
          "wrappedFromToken": "0x11e77e27af5539872efed10abaa0b408cfd9fbbd",
          "wrappedToToken": "0x52a9cea01c4cbdd669883e41758b8eb8e8e2b34b",
          "smgID": "0x000000000000000000000000000000000000000000000041726965735f303537",
          "tokenPairID0": "81",
          "networkFee0": 0,
          "serviceFee0": 0,
          "crossType0": 0,
          "tokenPairID1": "557",
          "crossType1": 1,
          "messageFee": 0,
          "gasStation": 0,
          "swapFee0": 500,
          "swapFee1": 500
        },
        "fees": {
          "networkFee": "290000000000000000",
          "serviceFee": "3962797",
          "discount": "1000000000000000000"
        }
      }
    }
  }
}
```

## 5. Creating Transactions

Create a cross-chain Swap transaction in the specified direction for the user's wallet signature and cross-chain completion. For EVM chain approve transaction, we need to check the allowance and create ERC20 approve transaction data by ourselves. This API only builds cross-chain Swap transaction, before execution, please make sure you have done approve operation and the allowance value is enough.

The request parameters are exactly the same as the `api/v3/quote` interface, so you can reuse the request data directly.

### 5.1 Interface Description

**Request address**

POST `https://xflows.wanchain.org/api/v3/buildTx`

**Request Parameters**

| Parameters       | Type   | Required | Description of the request                                                                             |
| ---------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------ |
| id               | String | No       | Random number to be returned with the return value to identify the order of the request.               |
| fromChainId      | Number | Yes      | ID of the source chain (e.g. `1`: Ethereum, more can be retrieved using the API).                      |
| toChainId        | Number | Yes      | Destination Chain ID (e.g. `56`: BNB Smart Chain, more can be obtained using API)                      |
| fromTokenAddress | String | Yes      | The address of the requesting currency contract (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` )   |
| toTokenAddress   | String | Yes      | Target currency contract address (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` )                  |
| fromAddress      | String | Yes      | Source chain wallet address                                                                            |
| toAddress        | String | Yes      | Destination chain wallet address                                                                       |
| fromAmount       | String | Yes      | fromAmount, e.g., "123.45"                                                                             |
| bridge           | String | No       | Optional, specify a bridge to be used, e.g. "wanbridge" or "quix", default is wanbridge if not filled. |
| dex              | String | No       | Optional, specify a DEX to be used, e.g. "wanchain" or "rubic".                                        |
| slippage         | Number | No       | Optional, the maximum slippage allowed, default value is 0.01 (represents 1%)                          |
| partner          | String | No       | Optional, the label of the partner.                                                                    |

**Response Parameters**

| Parameters | type                                       | Required | Descripción                                                      |
| ---------- | ------------------------------------------ | -------- | ---------------------------------------------------------------- |
| id         | String                                     | No       | Random number, same as input, to identify the order of requests. |
| chainId    | chainId                                    | Yes      | The chainId of the sending transaction                           |
| tx         | {}                                         | Yes      | Constructed transaction data                                     |
|            | - value                                    | String   | No                                                               |
|            | - to                                       | String   | No                                                               |
|            | - data                                     | String   | No                                                               |
|            | - approvalAddress                          | String   | No                                                               |
|            | - memo                                     | String   | No                                                               |
|            | - serializedTx                             | String   | No                                                               |
|            | - abi / params / functionSelector / params | {}       | No                                                               |

### 5.2 Request Examples

#### **1) Example Request: (from EVM chains)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 43114,
  "toChainId": 888,
  "fromTokenAddress": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
  "toTokenAddress": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "slippage": 0.001
}
```

**Example Response: (from EVM chains)**

```jsx
{
  "success": true,
  "data": {
    "chainId": 43114,
    "tx": {
      "value": "13460135000000",
      "to": "0xAeCbF30602caF42467e7120C04271EDcC843f3c7",
      "data": "0x4bcb403a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000080002328000000000000000000000000000000000000000000000000000000008057414e0000000000000000000000009702230a8ea53601f5cd2dc00fdbc13d4df4a8c70000000000000000000000002fb4d46372ea1748ec3c29bd2c7b536019df5200000000000000000000000000000000000000000000000000000000003b9aca000000000000000000000000000000000000000000000000000000000000000280000000000000000000000000000000000000000000000000000000003b1a88ff00000000000000000000000011e77e27af5539872efed10abaa0b408cfd9fbbd00000000000000000000000052a9cea01c4cbdd669883e41758b8eb8e8e2b34b000000000000000000000000000000000000000000000041726965735f30353700000000000000000000000000000000000000000000000000000000000000e90000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000c3dee90b7c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001f400000000000000000000000000000000000000000000000000000000000001f400000000000000000000000000000000000000000000000000000000000000142fb4d46372ea1748ec3c29bd2c7b536019df5200000000000000000000000000"
    }
  }
}
```

#### **2) Example Request: (from Bitcoin)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 2147483648,
  "toChainId": 888,
  "fromTokenAddress": "0x0000000000000000000000000000000000000000",
  "toTokenAddress": "0x50c439b6d602297252505a6799d84ea5928bcfb6",
  "fromAddress": "bc1qugvdunxxzqvy80hysz9y77nx50240n7ghhz3rd",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "0.002",
  "partner": "xflows"
}
```

**Example Response: (from EVM chains)**

```jsx
{
  "success": true,
  "data": {
    "tx": {
      "to": "bc1p64ekpgpmfzu7qag4eze8h775hwgc5fzzvt2g6w2wv4rdmmgk44dqny9plg",
      "value": 200000,
      "memo": "07000f000078666c6f77732fb4d46372ea1748ec3c29bd2c7b536019df5200"
    }
  }
}
```

#### **3) Example Request: (from Cardano)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 2147485463,
  "toChainId": 42161,
  "fromTokenAddress": "0x32356335646535663562323836303733633539336564666437376234386162633761343865356134663364346364396434323866663933352e3535353334343534",
  "toTokenAddress": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
  "fromAddress": "addr1q80p2p4a08kmd4fn5p6er8unu25n6302x3wrzajnl46as0nx3yflzt76nqydq2x6603wt96cvtuuj7ealj6j5r7qepmskkhetk",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "5",
  "partner": "xflows"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "tx": {
      "serializedTx": "84ab00828258204bdf1401cf3ce3279ee243a042c9d03601254674b6f3013f1b4c7bcb2d80b24a008258204dc625598a7f98a1911edfdf30c5a11f71cd4d966747c0ed170bf225227251e2000182825839010c05ca78b1d2f4104486ace091ada7c789733a5a0e9567e0bc3544a49e58f02147d458cce4a31e132cc30cd81d43f11d73033401e7dcf2941a001e848082583901de1506bd79edb6d533a075919f93e2a93d45ea345c317653fd75d83e668913f12fda9808d028dad3e2e5975862f9c97b3dfcb52a0fc0c877821a007a45c5a1581c25c5de5f5b286073c593edfd77b48abc7a48e5a4f3d4cd9d428ff935a244555344431a04c4b40044555344541a1c9c3800021a00054c8c031a09dc286a07582060bb27af0ed7ba5c7f715e876007127afad9c28965d0199d7b92768ebf389fd109a1581c25c5de5f5b286073c593edfd77b48abc7a48e5a4f3d4cd9d428ff935a144555344543a1dcd64ff0b5820d58636216b8b0d5b03f816c97dfd289631bee10a965ddff42806db51e2bdfff90d828258204bdf1401cf3ce3279ee243a042c9d03601254674b6f3013f1b4c7bcb2d80b24a008258204dc625598a7f98a1911edfdf30c5a11f71cd4d966747c0ed170bf225227251e2001082583901de1506bd79edb6d533a075919f93e2a93d45ea345c317653fd75d83e668913f12fda9808d028dad3e2e5975862f9c97b3dfcb52a0fc0c877821a0093e9a9a1581c25c5de5f5b286073c593edfd77b48abc7a48e5a4f3d4cd9d428ff935a244555344431a04c4b40044555344541a3a699d00111a000a2d281281825820fffb1b66bd78837ea0136587c354ee6a0991b6d0a2954e48d46a476b3ce683df00a10581840100d87980821a001626e41a12bca33cf5a101a66b66726f6d4163636f756e748278406164647231713830703270346130386b6d6434666e357036657238756e7532356e36333032783377727a616a6e6c34366173306e783379666c7a7437366e7179782764713278363630337774393663767475756a3765616c6a366a3572377165706d736b6b6865746b67706172746e65726678666c6f777365736d6749445820000000000000000000000000000000000000000000000041726965735f30353769746f4163636f756e74542fb4d46372ea1748ec3c29bd2c7b536019df52006b746f6b656e5061697249441901f1647479706508"
    }
  }
}
```

#### **4) Example Request: (from Solana)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 501,
  "toChainId": 888,
  "fromTokenAddress": "0x45506a465764643541756671535371654d32714e31787a7962617043384734774547476b5a77795444743176",
  "toTokenAddress": "0x52a9cea01c4cbdd669883e41758b8eb8e8e2b34b",
  "fromAddress": "2SFMj2XNzFCTzeQE8rEk82MxBq3A4u4J6uQvEnpmcqyh",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "5",
  "partner": "xflows"
}
```

**Example Response: (from Solana)**

```jsx
{
  "success": true,
  "data": {
    "tx": {
      "serializedTx": "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAkQFVNw5ypthVgz8lFRPNfRPMe/ufQ6BixH/73YR4GegvAhp6wFY40Ym+DdCl+oPDp4Vnoe257XWFLaQOYgcHCjyTzNc87IXADsuI2Qy8ak0jE9M0IRAhqD5DGJjETI9jAkRVafPC5c97vWwprgSq0wN+0wjwtmsREyFIRIifa2M6mKeERWu6W9qbwhs6Lj4UyvyY5gpgI2wMnkW2WMJTeyAateyLLYnsVsZR+X9XlGkyFBcMkY6NiYMvziKxqjgpG7xvp6877brTo9ZfNqq8l0MbG75MLS9uDkfKYCA0UvXWEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACSwg0+FVMmk6FXkLPjnIEQ+TzLKfJflaFCjyd8PEuNaZAvJ3zPF3TuKHxCJuoD0D12vyiNb33Pn7X9aQQr1uVh3YW5fcGFydG5lcjp4Zmxvd3MAAAAAAAAAAAAAAAAAAIKuHjxKyDYGsUdRHhJStJ+ig4GshjU9tRes6hpJ9C5mjJclj04kifG7PRApFI4NgwtaE5na/xCEBI572Nvp+FkDBkZv5SEXMv/srbpyw5vnvIzlu8X3EmssQ5s6QAAAAMHZ0b/TXl3f9PqMZ5KMpkjVm5YHFgVTF3+dEkEumuJMBt324ddloZPZy+FGzut5rBy0he1fWzeROoz1hX7/AKlWl3S6oS4QNSl1zKlvSB9sLUm16WT9HCJwqj8pZwtgvQIODgAEAgEGBQkLAwgPDAcKYkIR1n7rhVJyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBcmllc18wNTc9AwAAQEtMAAAAAAAqAAAAMHgyZmI0RDQ2MzcyRWExNzQ4ZWMzYzI5QmQyQzdCNTM2MDE5REY1MjAwDQAFAkBCDwA="
    }
  }
}
```

#### **5) Example Request: (from SUI)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 2147484432,
  "toChainId": 8453,
  "fromTokenAddress": "0x3078646261333436373265333063623036356231663933653361623535333138373638666436666566363663313539343263396637636238343665326639303065373a3a757364633a3a55534443",
  "toTokenAddress": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
  "fromAddress": "0x09212c719c1c62cd75a33a1cd70f34468b6096a26179f9e943621953168adbfc",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "5",
  "partner": "xflows"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "tx": {
      "serializedTx": "{\n  \"version\": 2,\n  \"sender\": null,\n  \"expiration\": null,\n  \"gasData\": {\n    \"budget\": null,\n    \"price\": null,\n    \"owner\": null,\n    \"payment\": [\n      {\n        \"objectId\": \"0xfab1f6005a5746ab02d882a0a63bc5ac740f80c2d28157ba20a238dffd3b0372\",\n        \"version\": \"590132835\",\n        \"digest\": \"9DEQ7Y4DvypHFMBrjTWpVciRSx5RzyvmFdwnNAvPcAVP\"\n      }\n    ]\n  },\n  \"inputs\": [\n    {\n      \"Pure\": {\n        \"bytes\": \"AGOfAgAAAAA=\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0x29a4f741448020f36301feffefbee6d4367d25f054147960a0713a3002e9d1f1\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"QEtMAAAAAAA=\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0x1706cef6192f49db4d5650eb93a912ae81694d0f8b90f591e6f489959829b987\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0xc22e2bf69d38889a92559f45fd8769838d98dfc85f9e42925c0cb34bd7da06c7\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0x8a47c0bcca85466f679a0f5b1e1e1ca0bed02a1ea33dad829fa22e8bfa97bf54\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0xfd6f639b37679637d77389038bcfad8e7a128122c18a9b0706d101670af21505\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0xbb93514a7e8774a4f9aca575793f766e3a21d0a936785129be4f99c0263e1d0f\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0x30e1529ff5b1bcaac4dcdc9095ea5a3562c6a26607e6b26b0dfd296ed230c2d1\"\n      }\n    },\n    {\n      \"UnresolvedObject\": {\n        \"objectId\": \"0x0000000000000000000000000000000000000000000000000000000000000006\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQXJpZXNfMDU3\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"+AMAAAAAAAA=\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"KjB4MmZiNEQ0NjM3MkVhMTc0OGVjM2MyOUJkMkM3QjUzNjAxOURGNTIwMA==\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"BnhmbG93cw==\"\n      }\n    },\n    {\n      \"Pure\": {\n        \"bytes\": \"CSEscZwcYs11ozoc1w80RotglqJhefnpQ2IZUxaK2/w=\"\n      }\n    }\n  ],\n  \"commands\": [\n    {\n      \"SplitCoins\": {\n        \"coin\": {\n          \"GasCoin\": true\n        },\n        \"amounts\": [\n          {\n            \"Input\": 0\n          }\n        ]\n      }\n    },\n    {\n      \"SplitCoins\": {\n        \"coin\": {\n          \"Input\": 1\n        },\n        \"amounts\": [\n          {\n            \"Input\": 2\n          }\n        ]\n      }\n    },\n    {\n      \"MoveCall\": {\n        \"package\": \"0x1c8b984b5d896a916b356171ee7c48eb5b62d8685ffe8da6f5ac30cc1def8c6a\",\n        \"module\": \"cross\",\n        \"function\": \"user_lock\",\n        \"typeArguments\": [\n          \"0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC\"\n        ],\n        \"arguments\": [\n          {\n            \"Input\": 3\n          },\n          {\n            \"Input\": 4\n          },\n          {\n            \"Input\": 5\n          },\n          {\n            \"Input\": 6\n          },\n          {\n            \"Input\": 7\n          },\n          {\n            \"Input\": 8\n          },\n          {\n            \"Input\": 9\n          },\n          {\n            \"Input\": 10\n          },\n          {\n            \"Input\": 11\n          },\n          {\n            \"Input\": 12\n          },\n          {\n            \"NestedResult\": [\n              1,\n              0\n            ]\n          },\n          {\n            \"NestedResult\": [\n              0,\n              0\n            ]\n          },\n          {\n            \"Input\": 13\n          }\n        ]\n      }\n    },\n    {\n      \"TransferObjects\": {\n        \"objects\": [\n          {\n            \"NestedResult\": [\n              0,\n              0\n            ]\n          }\n        ],\n        \"address\": {\n          \"Input\": 14\n        }\n      }\n    }\n  ]\n}"
    }
  }
}
```

#### **6) Example Request: (from Tron)**

```jsx
POST https://xflows.wanchain.org/api/v3/buildTx
BODY
{
  "fromChainId": 195,
  "toChainId": 1,
  "fromTokenAddress": "0xa614f803b6fd780986a42c78ec9c7f77e6ded13c",
  "toTokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fromAddress": "TEKTPLcABzoq8nthP6yV55kE94irztW2dW",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "5",
  "partner": "xflows"
}
```

**Example Response: (from Tron) Example Response: (from Tron)**

```jsx
{
  "success": true,
  "data": {
    "tx": {
      "to": "41fe464ebd5bb5d95731f90aa7b9e39df920a61c97",
      "abi": [
        {
          "inputs": [
            {
              "internalType": "bytes32",
              "name": "smgID",
              "type": "bytes32"
            },
            {
              "internalType": "uint256",
              "name": "tokenPairID",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "value",
              "type": "uint256"
            },
            {
              "internalType": "bytes",
              "name": "userAccount",
              "type": "bytes"
            }
          ],
          "name": "userLock",
          "outputs": [],
          "stateMutability": "payable",
          "type": "function"
        }
      ],
      "functionSelector": "userLock(bytes32,uint256,uint256,bytes)",
      "rawParameter": "0x000000000000000000000000000000000000000000000041726965735f303537000000000000000000000000000000000000000000000000000000000000011100000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000142fb4d46372ea1748ec3c29bd2c7b536019df5200000000000000000000000000",
      "params": [
        "0x000000000000000000000000000000000000000000000041726965735f303537",
        "273",
        "5000000",
        "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200"
      ],
      "value": "0x4a62f80"
    }
  }
}
```

## 6. Status Query

Get the status of XFlows transaction execution.

### 6.1 Interface Description

The input parameters of the interface are the same as those of the quote interface, except that the slippage is replaced by a hash value, which refers to the hash of the transaction sent by the source chain.

**Request address**

POST `https://xflows.wanchain.org/api/v3/status`

**Request Parameters**

| Parameters       | Type   | Mandatory | Description of the request                                                                           |
| ---------------- | ------ | --------- | ---------------------------------------------------------------------------------------------------- |
| id               | String | No        | Random number to be returned with the return value to identify the order of the request.             |
| fromChainId      | Number | Yes       | ID of the source chain (e.g. `1`: Ethereum, more can be retrieved using the API).                    |
| toChainId        | Number | Yes       | Destination Chain ID (e.g. `56`: BNB Smart Chain, more can be obtained using API)                    |
| fromTokenAddress | String | Yes       | The address of the requesting currency contract (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` ) |
| toTokenAddress   | String | Yes       | Target currency contract address (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` )                |
| fromAddress      | String | Yes       | Source chain wallet address                                                                          |
| toAddress        | String | Yes       | Destination chain wallet address                                                                     |
| fromAmount       | String | Yes       | fromAmount, e.g., "123.45"                                                                           |
| bridge           | String | No        | Optional, specify a bridge to use, e.g. "wanbridge" or "quix".                                       |
| dex              | String | No        | Optional, specify a DEX to be used, e.g. "wanchain" or "rubic".                                      |
| hash             | Number | Yes       | The transaction hash of the source chain.                                                            |

**Response Parameters**

| Parameters | type   | Required | Description                                                          |
| ---------- | ------ | -------- | -------------------------------------------------------------------- |
| id         | String | No       | Random number, same as input, used to identify the order of request. |
| statusCode | Number | Yes      | Current status code of the transaction:                              |

* **1**: `Success`
* **2**: `Failed`
* **3**: `Processing`
* **4/5**: `Refunded`
* 6: `Trusteeship`
* **7**: `Risk transaction`

Among them, the Trusteeship status indicates that there may be issues with the 'to' address filled in by the user, and the cross-chain process enters a manual intervention process. Users need to contact <techsupport@wanchain.org> for manual processing. Refunded status indicates that the transaction has been refunded, possibly due to slippage not being met, causing intermediate process failure and triggering a refund. There are two types of refund situations: 4 represents refund to the source chain, and 5 represents refund to the user's address on Wanchain. Risk transaction indicates that the user's address has AML risk, the transaction cannot continue, and has been refunded. | | statusMsg | String | Yes | Status message: Success, Processing, Failed, Refunded, Risk transaction | | receiveAmount | String | No | The number of toTokens actually received. For example, "122.45". (This value is not returned when the toToken is a native coin) | | receiveAmountRaw | String | No | The number of toTokens actually received. Amount should include precision, e.g. 0.001 DAI return: "1000000000000000". (This value is not returned when the toToken is a native coin.) | | workMode | Number | Yes | Return Value: 1. directly cross-chain, go to wan-bridge; 2. directly cross-chain, go to quix; 3. cross-chain first, then do Swap in target chain (e.g. cross to Wanchain); 4. cross-chain to Wanchain first, do Swap on Wanchain, then cross-chain to target chain; 5. only Swap, e.g. on Wanchain, Swap. Swap only, e.g. Swap on Wanchain, or Swap on other chains based on Rubic (not supported by OKX or 1inch for now); 6. Swap first and then cross chain, e.g. Swap from Wanchain and cross out to other chains; (not supported by OKX or 1inch for now) | | error | String | No | If an error is returned, this field returns the error message | | sourceHash | String | No | Source chain hash | | destinationHash | String | No | destinationHash | | swapHash | String | No | Swap hash | | refundHash | String | No | Refund hash in case of a refund | | String Start time in seconds. timestamp | Number | No | Start time in seconds. | | extraData | {} | No | Other relevant auxiliary information |

### 5.2 Request Examples

#### **1) Example Request: (workMode1)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 10,
  "toChainId": 42161,
  "fromTokenAddress": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
  "toTokenAddress": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "4.5015",
  "hash": "0x969eb35d16435b8bdd261804c74201454c7d95b348a8033b297278b55fae4590"
}
```

**Example Response: (workMode1)**

```jsx
{
  "success": true,
  "data": {
    "statusCode": 1,
    "statusMsg": "Success",
    "receiveAmount": "4.3015",
    "receiveAmountRaw": "4301500",
    "workMode": 1,
    "sourceHash": "0x969eb35d16435b8bdd261804c74201454c7d95b348a8033b297278b55fae4590",
    "destinationHash": "0xc29d7f9abcff581ccd776a4ea88d4417cbe3ec7485dbcf01dd56c7f3087644e8",
    "timestamp": 1757045459,
    "extraData": {
      "timestamp": 1757045459,
      "tokenPair": "373",
      "lockHash": "0x969eb35d16435b8bdd261804c74201454c7d95b348a8033b297278b55fae4590",
      "redeemHash": "0xc29d7f9abcff581ccd776a4ea88d4417cbe3ec7485dbcf01dd56c7f3087644e8",
      "status": "Success",
      "sendAmount": "4501500",
      "receiveAmount": "4301500"
    }
  }
}
```

#### **2) Example Request: (workMode2)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 56,
  "toChainId": 888,
  "fromTokenAddress": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
  "toTokenAddress": "0x52a9cea01c4cbdd669883e41758b8eb8e8e2b34b",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "10",
  "bridge": "quix",
  "hash": "0x670d61f9be47ab83f359835c017468524eeeb6cc0d6a50d258a4c896727c12e7"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "statusCode": 1,
    "statusMsg": "Success",
    "receiveAmount": "3.789",
    "receiveAmountRaw": "3789000",
    "workMode": 2,
    "sourceHash": "0x670d61f9be47ab83f359835c017468524eeeb6cc0d6a50d258a4c896727c12e7",
    "destinationHash": "0xeb550bef1cb343fac5f57b06199080729d805215ce78fd98dd5d03bb96ea3ff5",
    "timestamp": 1750130177,
    "extraData": {
      "_id": "6850de01da4efa011aa928fc",
      "intentId": "0xf779a3bf64aca2bff8dd3982160ceb0548ffdc3be1093d7f9f47c1269882fd0d",
      "chain": "Wanchain",
      "chainId": 888,
      "txHash": "0xeb550bef1cb343fac5f57b06199080729d805215ce78fd98dd5d03bb96ea3ff5",
      "status": "executed",
      "claimed": true,
      "intentInfo": {
        "intentType": 0,
        "nonce": "2",
        "fromChainId": "2147484362",
        "toChainId": "2153201998",
        "from": "0x4Cf0A877E906DEaD748A41aE7DA8c220E4247D9e",
        "to": "0x4Cf0A877E906DEaD748A41aE7DA8c220E4247D9e",
        "fromToken": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "fromAmount": "5789000000000000000",
        "toToken": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
        "toAmount": "3789000",
        "relayer": "0x25309635Fd36CF2A85712B5be4f38Fa887e002CC",
        "deadline": "1750389342",
        "extraData": "0x000000000000000000000000000000000000000000000041726965735f30353500000000000000000000000000000000000000000000000000000000000000f60000000000000000000000000000000000000000000000000000000000585548"
      },
      "createdAt": "2025-06-17T03:16:17.262Z",
      "__v": 0,
      "claimTxHash": "0x333f0f4e8c42b84a390a0be3ab43857a81e25047113799b91ea75a0d5830685a"
    }
  }
}
```

#### **3) Example Request: (workMode3)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 42161,
  "toChainId": 888,
  "fromTokenAddress": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
  "toTokenAddress": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "hash": "0x679883ca0c353a8888651dc436092fa2e61443016492607ded9d59904d75585c"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "workMode": 3,
    "statusCode": 1,
    "statusMsg": "Success",
    "receiveAmount": "3.784275",
    "receiveAmountRaw": "3784275",
    "sourceHash": "0x679883ca0c353a8888651dc436092fa2e61443016492607ded9d59904d75585c",
    "destinationHash": "0x480a4497145a0eac531f79c32308034efb27d6fdd3d8e642fe2959931b1d3ba3",
    "swapHash": "0x480a4497145a0eac531f79c32308034efb27d6fdd3d8e642fe2959931b1d3ba3",
    "extraData": {
      "_id": "68be7811660c0261a65b00f0",
      "messageId": "0x221e041d36548c1bb872dde4ae7a1ac73026c7ce982ae2be70d44e1ef70d8868",
      "lockHash": "0x679883ca0c353a8888651dc436092fa2e61443016492607ded9d59904d75585c",
      "timestamp": "2025-09-08T06:30:41.144Z",
      "status": 1,
      "details": [
        1073741826,
        2153201998,
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
        3786353,
        "0x2fb4d46372ea1748ec3c29bd2c7b536019df5200",
        3746523,
        "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
        "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
        "0x000000000000000000000000000000000000000000000041726965735f303537",
        186,
        0,
        0,
        0,
        80,
        1,
        111086000000,
        0,
        500,
        500
      ],
      "__v": 0,
      "processTxHash": "0x480a4497145a0eac531f79c32308034efb27d6fdd3d8e642fe2959931b1d3ba3"
    }
  }
}
```

#### **4) Example Request: (workMode4)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 42161,
  "toChainId": 10,
  "fromTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
  "toTokenAddress": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "hash": "0x32cb5524d67fd43c4a5e1170e54319fadaef4094f13fa8e5e3ac6db5ea14cab9"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "workMode": 4,
    "sourceHash": "0x32cb5524d67fd43c4a5e1170e54319fadaef4094f13fa8e5e3ac6db5ea14cab9",
    "timestamp": 1757321487,
    "swapHash": "0x8bbea570e673f6f950c438c9d0fa9f2328c20f52e0dc5c681ff10970f264f9ed",
    "statusCode": 1,
    "statusMsg": "Success",
    "receiveAmount": "6.76251",
    "receiveAmountRaw": "6762510",
    "destinationHash": "0x5c22efce1e8d8583e2712cfa2a960227bc2be3e28bf4ba36ee5d4ca5f8b6a39f",
    "extraData": {
      "timestamp": 1757321595,
      "tokenPair": "370",
      "lockHash": "0x8bbea570e673f6f950c438c9d0fa9f2328c20f52e0dc5c681ff10970f264f9ed",
      "redeemHash": "0x5c22efce1e8d8583e2712cfa2a960227bc2be3e28bf4ba36ee5d4ca5f8b6a39f",
      "status": "Success",
      "sendAmount": "6762510",
      "receiveAmount": "6762510"
    }
  }
}
```

#### **5) Example Request: (workMode5#1)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 888,
  "toChainId": 888,
  "fromTokenAddress": "0x0000000000000000000000000000000000000000",
  "toTokenAddress": "0x11e77E27Af5539872efEd10abaA0b408cfd9fBBD",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "hash": "0xbe8202b461739e91244e7b905565e83d3eb4482185472bd8a94a181fa2fb528f"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "workMode": 5,
    "swapHash": "0xbe8202b461739e91244e7b905565e83d3eb4482185472bd8a94a181fa2fb528f",
    "receiveAmount": "0.720547",
    "receiveAmountRaw": "720547",
    "statusCode": 1,
    "statusMsg": "Success",
    "extraData": {
      "dex": "wanchain"
    }
  }
}
```

#### **6) Example Request: (workMode5#2)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 42161,
  "toChainId": 42161,
  "fromTokenAddress": "0x0000000000000000000000000000000000000000",
  "toTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "hash": "0x54971b0566abea9c77a4d71672287f07ec9625ba8557191690265d5fb58616d5"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "workMode": 5,
    "swapHash": "0x54971b0566abea9c77a4d71672287f07ec9625ba8557191690265d5fb58616d5",
    "receiveAmount": "4.376184",
    "receiveAmountRaw": "4376184",
    "statusCode": 1,
    "statusMsg": "Success"
  }
}
```

#### **7) Example Request: (workMode6)**

```jsx
POST https://xflows.wanchain.org/api/v3/status
BODY
{
  "fromChainId": 888,
  "toChainId": 42161,
  "fromTokenAddress": "0x52A9CEA01c4CBDd669883e41758B8eB8e8E2B34b",
  "toTokenAddress": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
  "fromAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "toAddress": "0x2fb4D46372Ea1748ec3c29Bd2C7B536019DF5200",
  "fromAmount": "1000",
  "hash": "0xf9a4cfec864570c5d831c7684e77c6bed7f00826da2c369f0ffcf9d43a0e4342"
}
```

**Example Response.**

```jsx
{
  "success": true,
  "data": {
    "workMode": 6,
    "statusCode": 1,
    "statusMsg": "Success",
    "receiveAmount": "5.791341",
    "receiveAmountRaw": "5791341",
    "sourceHash": "0xf9a4cfec864570c5d831c7684e77c6bed7f00826da2c369f0ffcf9d43a0e4342",
    "destinationHash": "0x0ec4d403cf9585eb0ab70a0d689e482cdd052a1ece49bf5c36fbe6ad00f95368",
    "swapHash": "0xf9a4cfec864570c5d831c7684e77c6bed7f00826da2c369f0ffcf9d43a0e4342",
    "timestamp": 1757314260,
    "extraData": {
      "timestamp": 1757314260,
      "tokenPair": "186",
      "lockHash": "0xf9a4cfec864570c5d831c7684e77c6bed7f00826da2c369f0ffcf9d43a0e4342",
      "redeemHash": "0x0ec4d403cf9585eb0ab70a0d689e482cdd052a1ece49bf5c36fbe6ad00f95368",
      "status": "Success",
      "sendAmount": "5991341",
      "receiveAmount": "5791341"
    }
  }
}
```
