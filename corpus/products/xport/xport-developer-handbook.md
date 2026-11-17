
# XPort Developer Handbook

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FOgOPXa7vjjG3zw2f6GJ9%2FFrame%20680.png?alt=media&amp;token=8075c097-9c91-48fe-8f7e-761bf31ecab3" alt=""><figcaption></figcaption></figure>

## 0. Quick Start

To get started with the XPort EVM cross-chain token transfer demo, visit <https://github.com/wandevs/xport-evm-usage-demo> and follow the instructions provided.

## 1. Background

### 1.1. This Handbook

Welcome to the XPort Handbook! This handbook serves as a straightforward guide to help you understand and leverage XPort, Wanchain's Cross-Chain Data Transfer Protocol, to build decentralised cross-chain applications. Whether you're a seasoned cross-chain developer or someone taking their first steps into the world of blockchain technology, this handbook caters to all levels of expertise. We're excited to witness the innovative cross-chain applications you can envision and bring to life!

### 1.2. Cross-Chain Data Transfers

Cross-Chain Data Transfer Protocols enable data to be passed from one blockchain to another. Rather than only moving fungible and non-fungible tokens, which are a specific type of data structure, Cross-chain data transfer protocols can move any type of data. Importantly, Cross-Chain Data Transfer Protocols can feed data into 3rd party smart contracts to seamlessly execute on-chain logic and create novel cross-chain applications.

### 1.3. XPort: Wanchain's Cross-Chain Data Transfer Protocol

XPort, Wanchain's Cross-Chain Data Transfer Protocol, is composed of two basic elements: one robust off-chain relayer and a set of rudimentary on-chain smart contracts called Cross-Chain Gateways.

1. The off-chain relayer is the same Bridge Node Group that secures all cross-chain transactions executed using the WanBridge. These permissionless Bridge Nodes are rotated and re-elected monthly. They use Multiparty Computation and Shamir’s Secret Sharing cryptography to transfer messages and arbitrary data across chains.
2. A single smart contract, called a Cross-Chain Gateway, is deployed on each supported blockchain. These Cross-Chain Gateways have limited functionality – they can essentially only send and receive messages and arbitrary data. They serve as the point of contact for all 3rd party developers.

## 2. Getting Started

This section establishes a solid foundation to get you using XPort, Wanchain's Cross-Chain Data Transfer Protocol, as quickly as possible. It will outline a few necessary preparations before demonstrating how to perform a few of XPort's basic operations. This handbook will use [<mark style="color:blue;">https://remix.ethereum.org/</mark>](https://remix.ethereum.org/), an online Solidity IDE, as the development environment.

### 2.1. Necessary Preparations

1. Open your browser and visit [<mark style="color:blue;">https://remix.ethereum.org/</mark>](https://remix.ethereum.org/).
2. Click the File Explorer icon in the left navigation bar of Remix.
3. Click the "+" icon to create a new workspace. Name your workspace anything you like.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FzzVbFnHe4dSplooc4zAU%2FUntitled.png?alt=media&amp;token=6d6f22e8-bd02-42be-bcd2-eab91725b4bf" alt=""><figcaption></figcaption></figure>

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FM0LQrFjkXCIDJjLoFrMJ%2FUntitled%201.png?alt=media&amp;token=6a0fd8e4-68a1-448d-93c2-50fda6c1d6a7" alt=""><figcaption></figcaption></figure>

4. Create a new .sol smart contract and name it something that's easy to remember like "MyContract.sol".

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F5qP4PXDrkLkATA7EyicJ%2FUntitled%202.png?alt=media&amp;token=5a5ca485-5d9b-452a-9a4f-f2b52fa059fa" alt=""><figcaption></figcaption></figure>

### 2.2. Basic Operations

1. In your new .sol smart contract, import WmbApp.sol. Use `is` to indicate that your contract inherits WmbApp. This allows your smart contract to access all public and protected members from WmbApp. For example, you can declare your contract as follows:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.18;

import "@wandevs/message@0.2.1/contracts/app/WmbApp.sol";

contract MyContract is WmbApp {
    // Your contract codes
}
```

2. Override the `_wmbReceive` function in your smart contract. `_wmbReceive` is a protected function provided by WmbApp. It will be called when your smart contract receives a cross-chain message. Customise the `_wmbReceive` function to meet your application's specific needs.  `_wmbReceive` defines how your contract will behave when it receives a cross-chain message.

```solidity
function _wmbReceive(
        bytes calldata data,
        bytes32 messageId,
        uint256 fromChainId,
        address fromSC
    ) internal override {
		// do something you want...
}
```

3. When initializing your smart contract contract, call the WmbApp `initialize` function. `initialize` takes two parameters: `admin` and `_wmbGateway`. Pass in the address of the administrator account as `admin` and the address of the WmbGateway as `_wmbGateway`. For example:

```solidity
constructor(address admin, address _wmbGateway) WmbApp() {
    initialize(admin, _wmbGateway);
    // Your initialization code
}
```

4. In your smart contract, you may need to send messages or contract calls to other chains. For this, call the `_dispatchMessage` function. `_dispatchMessage` is a protected function provided by WmbApp. It can send messages to any chain or contract you specify. `_dispatchMessage` takes four parameters:

   * `toChainId`: The ID of the chain that will receive the message.
   * `toAddress`: The address of the smart contract that will receive the message.
   * `msgData`: The message data you want to send.
   * `feeAmount`: The fee you want to pay.

   For example, you can call the `_dispatchMessage` function like this:

<pre class="language-solidity"><code class="lang-solidity"><strong>function sendMessage(
</strong>	uint256 toChainId, address toAddress, bytes memory msgData,
	uint feeAmount) public payable {
    _dispatchMessage(toChainId, toAddress, msgData, feeAmount);
}
</code></pre>

*Note: In this example, the `sendMessage` function takes the above parameters and simply calls the `_dispatchMessage` function. You can customise the function in your own smart contract and call the `_dispatchMessage` function in accordance with your needs. Before calling the `_dispatchMessage` function,  use the `estimateFee` function to estimate the fee.*

5. `estimateFee` is a public function provided by WmbApp. It can help you calculate the fee required to send a cross-chain message. `estimateFee` takes two parameters:

   * `toChain`: The BIP44 ChainId of the chain that will receive the message.
   * `gasLimit`: The gas limit required to execute the contract call on the receiving chain.

   Use the fee value returned by the `estimateFee` function as the `feeAmount` parameter of the `_dispatchMessage` function. You can use `msg.value` to pass in the native token of your chain as the fee, or use the balance of your smart contract as the fee.

   For example, you can call the `_dispatchMessage` function like this:

<pre class="language-solidity" data-full-width="false"><code class="lang-solidity"><strong>function sendMessage(
</strong>	uint256 toChainId, address toAddress,
	bytes memory msgData, uint256 gasLimit) public payable {
    uint256 fee = estimateFee(toChainId, gasLimit);
    require(msg.value >= fee, "Insufficient fee");
    _dispatchMessage(toChainId, toAddress, msgData, msg.value);
}
</code></pre>

*Note: In this example, the `sendMessage` function adds the `gasLimit` parameter and calls the `estimateFee` function to calculate the fee inside the function. Then, the smart contract checks whether `msg.value` is greater than or equal to the calculated fee. If it is not enough, an exception is thrown. Finally, the `_dispatchMessage` function is called and uses `msg.value` as the fee.*&#x20;

### 2.3. Additional Operations

1. WmbApp provides a function called `_dispatchMessageBatch`. It can be used to send transactions in batches to different contract addresses on the target chain. `_dispatchMessageBatch` can also be used to interact with multiple different contracts or to ensure the sequential execution of multiple operations. `_dispatchMessageBatch` takes three parameters:

   * `toChainId`: the ID of the chain that will receive the message.
   * `messages`: an array containing multiple Message structures. Each Message structure contains a target address and a message data.
   * `fee`: The fee you want to pay.

   For example, you can call the `_dispatchMessageBatch` function like this:

```solidity
function sendMessageBatch(
	uint256 toChainId, Message[] memory messages, uint256 gasLimit)
	public payable {
    uint256 fee = estimateFee(toChainId, gasLimit);
    require(msg.value >= fee, "Insufficient fee");
    _dispatchMessageBatch(toChainId, messages, msg.value);
}
```

*Note: In this example, the `sendMessageBatch` function calculates the fee using the `estimateFee` function. It then checks if `msg.value` is greater than or equal to the calculated fee. If it is not, an exception is thrown. Finally, the `_dispatchMessageBatch` function is called using `msg.value` as the fee.*

2. After your smart contract is deployed and initialized, the administrator needs to call the `setTrustedRemotes` function to explicitly specify which chains and contracts have permission to send cross-chain messages to your contract. This is an important step to ensure the security of your contract. The `setTrustedRemotes` function accepts three parameters:
   * `fromChainIds`: an array containing multiple chain IDs, each of which is a uint type.
   * `froms`: an array containing multiple contract addresses, each of which is an address type. Each address corresponds to the chain ID at the same position in the `fromChainIds` array.
   * `trusted`: an array containing multiple Boolean values, each of which represents whether the corresponding chain and contract is trusted and can send cross-chain messages to your contract.

### 2.4 Before Moving On

After completing the above operations, your smart contract is ready to receive and send cross-chain messages. Please note that it is your responsibility to ensure the security of your smart contract. You can compile and deploy your smart contract to a blockchain using Remix and MetaMask.

Now that you have an understanding of the basics of XPort, Wanchain's Cross-Chain Data Transfer Protocol, you can customise your smart contracts to receive and send cross-chain messages to serve the unique needs of your application or use case.&#x20;

## 3. Supported Blockchains

Note: While this handbook strives to be comprehensive, please refer to <https://github.com/wanchain/message-bridge-contracts> for an up-to-date list of supported networks.

### 3.1 Mainnets

| Index | Network           | Address                                    | Bip44 chainId |
| ----- | ----------------- | ------------------------------------------ | ------------- |
| 1     | Polygon           | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147484614    |
| 2     | BSC               | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147484362    |
| 3     | Wanchain          | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2153201998    |
| 4     | Avalanche         | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147492648    |
| 5     | Optimism          | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147484262    |
| 6     | Arbitrum          | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741826    |
| 7     | Energi            | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147493445    |
| 8     | Bitrock           | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2154655314    |
| 9     | Ethereum          | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147483708    |
| 10    | Meld (deprecated) | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741847    |
| 11    | Plyr              | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741849    |
| 11    | Base              | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741841    |
| 12    | Waterfall         | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741851    |
| 13    | DIONE Mainnet     | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741848    |
| 14    | 5ire              | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741853    |
| 15    | Polygon zkEVM     | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741838    |
| 16    | Linea             | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741842    |
| 17    | X Layer           | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741835    |
| 18    | Celo              | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 2147536400    |
| 19    | edeXa             | 0x7280E3b8c686c68207aCb1A4D656b2FC8079c033 | 1073741850    |

### 3.2 Testnets

**Testnet**

| Index | Chain Name               | Gateway                                    | Chain ID   |
| ----- | ------------------------ | ------------------------------------------ | ---------- |
| 1     | Avalanche Fuji Testnet   | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147492648 |
| 2     | Wanchain Testnet         | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2153201998 |
| 3     | XDC Apothem Testnet      | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147484198 |
| 4     | Ethereum Sepolia Testnet | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147483708 |
| 5     | Arbitrum Sepolia         | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741826 |
| 6     | Optimism Sepolia         | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147484262 |
| 7     | polygon amoy             | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147484614 |
| 8     | energi                   | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147493445 |
| 9     | bitrock                  | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2154655314 |
| 10    | BSC Testnet              | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 2147484362 |
| 11    | DIONE Odyssey Testnet    | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741848 |
| 12    | PLYR TAU Testnet         | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741849 |
| 13    | edeXa Testnet            | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741850 |
| 14    | Base Sepolia Testnet     | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741841 |
| 15    | Waterfall Testnet 9      | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741851 |
| 16    | 5ire Testnet             | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741853 |
| 17    | Lummio Testnet           | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741854 |
| 18    | Linea                    | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741842 |
| 19    | Polygon zkEVM            | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741838 |
| 20    | Immutable zkEVM          | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741855 |
| 21    | Shido                    | 0xDDddd58428706FEdD013b3A761c6E40723a7911d | 1073741856 |
| 22    | Vechain                  | 0xa1Dd5cBF77e1E78C307ecbD7c6AEea90FC71499e | 2147484466 |

*Note: When writing smart contracts and performing cross-chain operations, ensure that you use the correct ChainId value.*

## 4. Appendix: XPort, Wanchain's Cross-Chain Data Transfer Protocol Composition

### 4.1 Basic Elements

True to its legacy, XPort, Wanchain’s Cross-Chain Data Transfer Protocol is deceptively simple. It simply detects data on the source chain then repeats it on the destination chain in the correct format.

XPort is composed of two basic elements: one robust off-chain relayer and a set of rudimentary on-chain smart contracts called Cross-Chain Gateways.

1. The off-chain relayer is the exact same Bridge Node Group that secures all cross-chain transactions executed using the WanBridge. These permissionless Bridge Nodes are rotated and re-elected monthly. They use Multiparty Computation and Shamir’s Secret Sharing cryptography to transfer messages and arbitrary data across chains.
2. A single smart contract, called a Cross-Chain Gateway, is deployed on each supported blockchain. These Cross-Chain Gateways have limited functionality – they can essentially only send and receive messages and arbitrary data. They serve as the point of contact for all 3rd party developers.

### 4.2 XPort Transaction Flow

The basic flow of XPort, Wanchain's Cross-Chain Data Transfer Protocol, is as follows:

1. &#x20;A message is sent – A 3rd party application sends a transaction to XPort's Cross-Chain Gateway on the source chain to initiate a cross-chain message request. In addition to the message itself, this request includes several bits of additional data including the destination chain ID, a target smart contract address on the destination chain, and more. XPort's Cross-Chain Gateway generates a unique messageID to differentiate each cross-chain message request and, after checking that all the required data is complete, records the request on the source chain as an Event.
2. A message in transit – The Wanchain Bridge Node Group detects this Event and verifies that all the required data is complete. Then, using Wanchain’s unique blend of Multiparty Computation and Shamir’s Secret Sharing cryptography, the Bridge Node Group signs the cross-chain message and sends a transaction to XPort's Cross-Chain Gateway on the destination chain.
3. A message arrives – XPort's Cross-Chain Gateway on the destination chain verifies that the signature is valid and confirms that all the required data is complete. It then forwards the cross-chain message to the target smart contract address on the destination chain. The smart contract can then execute customised on-chain logic using the received message.

### **4.3 Cross-Chain Gateway Smart Contract Design**

#### **4.3.1 EIP-5164**

XPort, Wanchain's Cross-Chain Data Transfer Protocol, follows the specifications laid out in EIP-5164. EIP-5164 details a cross-chain execution interface for EVM-based blockchain. It defines two components: the `MessageDispatcher` and the `MessageExecutor`. The `MessageDispatcher` lives on the origin chain and dispatches messages to the `MessageExecutor` for execution. The `MessageExecutor` lives on the destination chain and executes dispatched messages. Using this interface, developers can create smart contracts on one chain that can call contracts on another chain by sending a cross-chain message.

The interface defines several methods, events, executions and errors types:

*MessageDispatcher Methods*

1. `dispatchMessage`: Used to send a single cross-chain message. Parameters include target chain ID, target contract address, and message data. Returns a unique messageId.
2. `dispatchMessageBatch`: Used to send a batch of cross-chain messages. Parameters include target chain ID and message array. Returns a unique messageId.

*MessageDispatcher Events*

1. `MessageDispatched`: Triggered when a cross-chain message is successfully sent with messageId, sender address, target chain ID, target contract address, and message data included.
2. `MessageBatchDispatched`: Triggered when a batch of cross-chain messages are successfully sent with messageId, sender address, target chain ID, and message array included.
3. `MessageIdExecuted`: Triggered when a cross-chain message is successfully executed with the source chain ID and messageId included.

*MessageExecutor Executions*

1. `MessageExecutor` must append the ABI-packed (`messageId`, `fromChainId`, `from`) to the calldata for each cross-chain message being executed.

*Error Types*

1. `MessageIdAlreadyExecuted`: An error triggered when attempting to execute an already executed messageId.
2. `MessageFailure`: An error triggered when a message execution fails. Contains the message ID and error data.
3. `MessageBatchFailure`: An error triggered when batch message execution fails. Contains the message ID, message index, and error data.

#### **4.3.2 Gateway Contract Interface**

The `IWmbGateway` file is the interface definition of the Wanchain's Cross-Chain Data Transfer Protocol Cross-Chain Gateway contract. The interface extends and expands the EIP-5164 interface and includes the following interfaces:

1. `dispatchMessage`: Used to a message to a specified address on a specified chain and attach the corresponding data. Parameters include toChainID, to and data. Returns a unique messageId.
   * `toChainId` (uint256): The chain ID of the target chain.
   * `to` (address): The address of the target contract on the target chain.
   * `data` (bytes): The data sent to the target contract.
   * `messageId` (bytes32): The unique identifier of the sent message.

```solidity
function dispatchMessage(
    uint256 toChainId,
    address to,
    bytes calldata data
) external payable returns (bytes32 messageId);
```

2. `dispatchMessageBatch`: Used to send a batch of messages to a specified chain. Returns a unique messageId.

* `toChainId` (uint256): The chain ID of the target chain.
* `messages` (Message\[]): An array containing the target addresses and data to be sent to each target contract.
* `messageId` (bytes32): The unique identifier of the sent message batch.

```solidity
function dispatchMessageBatch(
    uint256 toChainId,
    Message[] calldata messages
) external payable returns (bytes32 messageId);
```

3. `receiveMessage`: Used to receive a message from another link and verify the sender's signature.
   * `messageId` (bytes32): The unique identifier of the message to prevent replay attacks.
   * `sourceChainId` (uint256): The chain ID of the source chain.
   * `sourceContract` (address): The address of the source contract on the source chain.
   * `targetContract` (address): The address of the target contract on the target chain.
   * `messageData` (bytes): The data sent in the message.
   * `gasLimit` (uint256): The maximum gas consumption for the message call.
   * `smgID` (bytes32): Wanchain Storeman Group ID that signed the message.
   * `r` (bytes): R component of the SMG MPC signature.
   * `s` (bytes32): S component of the SMG MPC signature.

```solidity
function receiveMessage(
    bytes32 messageId,
    uint256 sourceChainId,
    address sourceContract,
    address targetContract,
    bytes calldata messageData,
    uint256 gasLimit,
    bytes32 smgID,
    bytes calldata r,
    bytes32 s
) external;
```

4. `receiveBatchMessage`: Used to receive a batch of messages from another link and verify the sender's signature.
   * `messageId` (bytes32): The unique identifier of the message to prevent replay attacks.
   * `sourceChainId` (uint256): The chain ID of the source chain.
   * `sourceContract` (address): The address of the source contract on the source chain.
   * `messages` (Message\[]): An array of messages containing the target addresses and data to be sent to each target contract.
   * `gasLimit` (uint256): The maximum gas consumption for the message call.
   * `smgID` (bytes32): Wanchain Storeman Group ID that signed the message.
   * `r` (bytes): R component of the SMG MPC signature.
   * `s` (bytes32): S component of the SMG MPC signature.

```solidity
function receiveBatchMessage(
    bytes32 messageId,
    uint256 sourceChainId,
    address sourceContract,
    Message[] calldata messages,
    uint256 gasLimit,
    bytes32 smgID,
    bytes calldata r,
    bytes32 s
) external;
```

5. `estimateFee`: Used to estimate the fee required to send a message to the target chain. Parameters include targetChainId and gasLimit. Returns a fee.

* `targetChainId` (uint256): The chain ID of the target chain.
* `gasLimit` (uint256): The maximum gas consumption for the message call when calling a third-party DApp contract during cross-chain message transmission.
* `fee` (uint256): The estimated fee required for cross-chain message transmission.

```solidity
function estimateFee(
    uint256 targetChainId,
    uint256 gasLimit
) external view returns (uint256 fee);
```

Other public read-only interfaces are shown in the following table:

| Variable name           | Meaning                                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| chainId                 | The slip-0044 standard chainId of the local chain                                                                              |
| maxGasLimit             | The maximum global gas limit for messages                                                                                      |
| minGasLimit             | The minimum global gas limit for messages                                                                                      |
| defaultGasLimit         | The default gas limit for messages                                                                                             |
| maxMessageLength        | The maximum message length                                                                                                     |
| signatureVerifier       | The address of the signature verification contract                                                                             |
| wanchainStoremanAdminSC | The address of the Wanchain Storeman Admin contract                                                                            |
| messageExecuted         | The mapping of message ID to execution status                                                                                  |
| baseFees                | The mapping of target chain ID to basic fees for obtaining the target chain's fee benchmark                                    |
| messageGasLimit         | The mapping of message ID to gas limit, storing the gas limit value set for each message                                       |
| nonces                  | The mapping of source chain ID -> target chain ID -> source contract -> target contract -> nonce for preventing replay attacks |
| supportedDstChains      | The mapping of target chain ID to support status                                                                               |

#### **4.3.3 Gas Limit and Fee Estimation**

Cross-chain transactions require a fee. The calculation of fees needs to consider the gas limit value of the target chain. When estimating fees, it is necessary to consider the gas limit value of the target chain and the size of the transaction data. Fees need to be independently configured to account for different target chains.

The formula for calculating fees is as follows:

```
estimatedFee = gasLimit * baseFee
```

gasLimit is the target smart contract call gasLimit passed when calling the send interface. baseFee is the unit price. When setting baseFee, three points should be considered:

1. The price difference between the source chain and the target chain: The value of different native coins on different chains may differ greatly. When calculating fees, it is necessary to adjust according to the actual coin price.
2. The default gasPrice of the target chain: The gas price of each chain is different, and the transaction fee needs to consider the gasPrice of the target chain to calculate the cross-chain transaction fee more accurately.
3. The profit margin: In order to ensure sustainable, long-term operations, fees should result in a desired profit margin. When configuring baseFee, developers should ensure that they are not consistently operating at a loss.

*Note: In cases where the gasLimit is set but the target chain's gasLimit is insufficient, third-party DApps can retry failed transactions. When retrying failed transactions, DApps are not limited by the gas limit, which can avoid transaction failures due to insufficient gas limit.*

#### **4.3.4 Error Handling**

When calling the target chain smart contract, the try-catch interface can be used to handle transaction failures. When a transaction fails, according to EIP-5164, an Error containing the MessageId and error information will be directly reverted. If the reason for the failure is insufficient gas, the DApp can resubmit the transaction with a higher gasLimit. If a developer does not want the failed transaction to be re-executed, they need to capture errors and actively restrict them in the DApp contract.

#### **4.3.5 App Contract Inheritance Template**

Third-party DApps can inherit and develop their own cross-chain applications from the APP template, and all interactions with the Gateway are encapsulated in the APP template. The APP template is divided into two types: 1) WmbApp simple template; 2) WmbRetryableApp App template that can retry errors.

1. The simple template directly forwards the message without any error caching. Failed transactions cannot be retried within the contract.
2. The retryable template caches error transactions and can retry or read the messageId information that occurred in the error within the contract.

#### **4.3.6 Guaranteed Message Execution Order**

For messages with strict execution order requirements, the `dispatchMessageBatch` interface can be used to send batch messages. The execution order in this interface can be strictly guaranteed. If any one message fails, the entire transaction will be rolled back. The ordinary dispatchMessage interface does not guarantee strict sequential execution. If the third party wants to guarantee the order, it can customize the contract code in its DApp.

#### **4.3.7 Basic Smart Contract Security Considerations**

1. Prevent reentrancy attacks: Use the nonReentrant function to restrict reentrancy for the interfaces that involve sending messages, because these interfaces contain refund callback sender operations.
2. Prevent replay attacks: Use a globally unique messageId recorded in the contract to prevent possible replay attacks.
3. Administrator permissions: Use the AccessControl library to restrict function access.

## 5. Advanced Usage

A few simple example smart contracts designed to work with XPort, Wanchain's Cross-Chain Data Transfer Protocol, can be found here: [<mark style="color:blue;">https://github.com/wanchain/message-bridge-contracts/tree/main/contracts/examples</mark>](https://github.com/wanchain/message-bridge-contracts/tree/main/contracts/examples)

### 5.1 Cross-Chain Applications with On-Chain Recording and Retry

Inherit from the RetryableApp contract to implement a cross-chain application that can record error messages on-chain and customise retry rules.

See: `examples/CCPoolV2.sol`

## 6. Practical Examples

A few simple example smart contracts designed to work with XPort, Wanchain's Cross-Chain Data Transfer Protocol, can be found here: [<mark style="color:blue;">https://github.com/wanchain/message-bridge-contracts/tree/main/contracts/examples</mark>](https://github.com/wanchain/message-bridge-contracts/tree/main/contracts/examples)

### 6.1 Cross-Chain Token Issuance

Based on cross-chain burn-and-mint mechanism, developers can issue a new token on multiple blockchains and perform unrestricted cross-chain transfers without wrapping or liquidity pools.

See an example: `examples/mcToken.sol`

### 6.2 Permissionless Cross-Chain Transfers

Developers can enable perform permissionless cross-chain transfers for existing tokens by leveraging XPort, Wanchain's Cross-Chain Data Transfer Protocol.

See an example: `examples/ccPoolV1.sol`

### 6.3 Refundable Token Cross-Chain

When the cross-chain fails due to insufficient balance in the pool, developers can choose to refund the assets to the user's wallet on the source chain.

See an example: `examples/ccPoolV2.sol`

## 7. FAQ

**Q1:** What happens if across-chain transaction fails on the target chain?

A: Third-party DApp smart contracts need to consider possible failure scenarios in advance during the design phase, including whether failed transactions need to be retried, whether failed transactions need to be recorded on-chain, and whether feedback messages need to be sent to the original chain. XPort's default off-chain relayer, the Wanchain Bridge Node Group, will not automatically retry failed transactions. DApps need to handle failure scenarios according to its needs.

**Q2:** Is there a way to make end users pay the cross-chain transaction fee themselves?

A: Yes. Simply send the transaction fee as a payable value along with the transaction when building it.

**Q3:** Is there a way to make cross-chain transactions free for end users? to make users use message cross-chain for free and let the project bear the cross-chain transaction fee?

A: Yes. A developer can subsidise cross-chain fees by depositing sufficient native coins in the DApp smart contract. This balance can be used to pay transaction fees.
