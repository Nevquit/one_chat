
# XPort Fee Center User Guide

## 1. Overview

**XPort** is the core messaging cross-chain mechanism within the Wanchain Cross-chain Bridge. In **XPort V1**, the bridge charges a certain amount of **native coin on the source chain** as a bridge fee, which is used to cover gas costs incurred when processing messages on the **destination chain**. Over the past year, XPort has seen significant growth and adoption across the blockchain community.

However, with increased usage, the V1 fee model has shown some limitations:

* The native coin charged on the source chain differs from the gas coin consumed on the destination chain;
* In volatile market conditions, the price gap between the collected and spent tokens can grow significantly, causing losses and reducing sustainability.

To address this, **XPort V2** introduces a more robust and flexible fee model:

* The **project pays in the same token** that the Agent uses to process the transaction on the destination chain;
* Projects can freely specify which token to charge end users on the source chain;
* This eliminates token price fluctuation risks and improves long-term sustainability.

## 2. Workflow

In XPort V2, when a user initiates a cross-chain message, the **cross-chain Agent** will **cover the gas fee on the destination chain**. The corresponding token amount will then be deducted from the **Fee Contract account on Wanchain**.

#### Example:

For a message from **Arbitrum to Avalanche**:

1. **Source Chain (Arbitrum)**: The user triggers the cross-chain message and pays the cross-chain fee to the project. The token used for the cross-chain fee is defined by the project.
2. **Destination Chain (Avalanche)**: The Agent pays the gas fee in AVAX, the native coin of the destination chain.
3. **Wanchain**: The equivalent AVAX amount (actual fee + platform service fee) is deducted from the Fee Contract account.

## 3. XPort Fee Center Platform

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F6Jbuhtc92fQp4wLhXvPP%2Fimage.png?alt=media&amp;token=84e593e1-40ba-4e40-9f23-41f189cb8271" alt=""><figcaption><p>Homepage</p></figcaption></figure>

To simplify fee management, Wanchain provides the **XPort Fee Center**, a unified portal for project teams to map their dapp contracts with spender, manage fee deposits, and check the fee spendings.

#### XPort Fee Center Access:

* **Mainnet**: [https://xport.wanchain.org](https://xport.wanchain.org/)
* **Testnet**: [https://xport-testnet.wanchain.org](https://xport-testnet.wanchain.org/)

> Please connect your wallet and ensure your network is set to **Wanchain** or **Wanchain Testnet**.

### 3.1 Asset Management

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FDvTnJbT0FKkx0rDwKVDu%2F1751006780746.png?alt=media&amp;token=ddbfdeeb-c000-4e8d-9b10-a2d6ac4fc2ba" alt=""><figcaption></figcaption></figure>

#### 3.1.1 Token Balances

This section displays the current token balance recorded in the Fee Contract for the connected wallet address.

It allows for:

* Depositing tokens;
* Withdrawing unused tokens;
* Transferring admin rights.

For example, to support cross-chain messages to Avalanche, the project team must deposit `wanAVAX` into the Fee Contract. `AVAX` is the native coin of Avalanche for gas. Other destination chains are similar, that is, **whichever token the target chain uses as gas, you should make sure the balance is enough for that minted token on Wanchain.**

#### 3.1.2 Bridge

Project teams can use WanBridge ([bridge.wanchain.org](https://bridge.wanchain.org/)) to transfer the required fee tokens to Wanchain.

#### 3.1.2 Deposit

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FUZiTuGUwPmNOPiBHBuzI%2F1751008835270.png?alt=media&amp;token=04147ffa-5f65-49b1-86bb-5b705e673e64" alt=""><figcaption></figcaption></figure>

After the required tokens are bridged to Wanchain via WanBridge, you can use the **Deposit** to fund the Fee Contract. In this way, you will be able to see the balance of the token.

**Note:** If the remaining balance in the Fee Contract is not enough to cover the user's cross-chain transaction, the transaction will remain in a pending state. Therefore, please make sure to replenish the balance in a timely manner when it is insufficient, ensuring that the Fee Contract account always has enough funds.

#### 3.1.3 Withdraw

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FxAg9rPFco7JGelyLg8va%2F1751008888975.png?alt=media&amp;token=d9debd9f-ce45-42e2-816e-3c5bdea3e519" alt=""><figcaption></figcaption></figure>

Use **Withdraw** to retrieve any unused fees from the Fee Contract if necessary.

#### 3.1.4 Transfer Admin

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FsznwuowoiKLq4BykFZvS%2F1751008984651.jpg?alt=media&amp;token=20642319-6d7f-430b-ab3b-f51d97f50177" alt=""><figcaption></figcaption></figure>

Use this function to transfer admin rights of the Fee Contract to another wallet address.

### 3.2 Spenders Management

#### 3.2.1 Add Spender

A **Spender** is a DApp smart contract address on the source chain that initiates cross-chain messages.

* You must associate the contract address with the correct source chain.
* Incorrect configuration will result in stuck or failed cross-chain messages.

For example, if your DApp supports message crosschain from Wanchain to Ethereum, add the contract address to the New Spender Address and select the **Wanchain** chain as source.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FDIONzGm7Y1b7Uf5exuKb%2F1751009141834.png?alt=media&amp;token=8dd3af82-e54e-4c07-90dd-690903acc6dd" alt=""><figcaption></figcaption></figure>

#### 3.2.2 Remove Spender

If a DApp is no longer active, you could remove its contract address from the spender list.

### 3.3 Transaction History

This section displays all relevant operations and historic data, including:

* **My Deposits**
* **My Withdrawals**
* **Fee Deductions Records**
* **Admin Transfers**

## 4. Developing Cross-chain Fee Charging From End Users

The XPort Fee Center provides a comprehensive platform for unified management of payments and prepayments between the XPort protocol and the project teams. However, as a project team, you still need to develop your own contracts or tools based on your praticial DApp, so that when an end user initiates a cross-chain message on the source chain, you can collect the required cross-chain fees from the user.

For any technical questions, feel free to contact **<techsupport@wanchain.org>**.
