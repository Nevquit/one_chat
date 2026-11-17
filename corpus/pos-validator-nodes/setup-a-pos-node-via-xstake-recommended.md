
# Setup a PoS Node via XStake (Recommended)

## 0. Node Overview & Requirements

Before becoming a Wanchain PoS Validator (Galaxy Consensus Node), please ensure your environment meets the hardware and staking requirements below.

**Hardware Requirements**

| Item             | Requirement (Minimum)  |
| ---------------- | ---------------------- |
| CPUX             | 4 cores                |
| RAM              | 8 GB                   |
| Disk Space       | 200 GB                 |
| Operating System | Ubuntu 22.04 and above |

**Staking Requirements**

* **Minimum Stake:**
  * **Delegating Validator:** 50,000 WAN
  * **Non-delegating Validator:** 10,000 WAN
* **Staking Period:** You may freely choose any period between 7–90 days.
* **Node Exit:** After you initiate exit and your staking period has expired, you may withdraw your staked WAN at any time.
* **Registration Window:** There is no fixed registration window. You may register a Wanchain PoS node at any time.

**XStake Portal:** [https://xstake.wanchain.org](https://xstake.wanchain.org/)

## 1. Node Deployment

This section uses a Docker-based quickstart script. Running this process requires `sudo` privileges.

### 1.1 Execute Quickstart Script

Log in to your server via SSH and run the following command to initialize the deployment:

```
wget https://raw.githubusercontent.com/wanchain/scripts/main/pos/mainnet/deployMainnetValidator.sh && chmod +x deployMainnetValidator.sh && ./deployMainnetValidator.sh
```

**Interactive Prompts:**

1. **Validator Name:** Enter a display name (this will appear on [wanstats.io](https://wanstats.io)).
2. **Password:** Enter a secure password for the validator account. *Note: For security, characters will not appear on the screen as you type.*
3. **Confirm Password:** Re-enter the password.

> ⚠️ CRITICAL: Back up your password securely. If this password is lost, your funds and node access cannot be recovered.

#### 1.2 Save and Secure Your Credentials

Once the script completes, it will display vital information. **Copy and store these details in a secure location:**

* **Validator Address:** Used for node operations (not for staking funds).
* **Public Key 1 & Public Key 2:** Required for on-chain registration.
* **Keystore JSON:** Necessary for node recovery.

**Note:** Please remember to back up your password properly. If this password is lost, there is no way to recover it. Do not use your Validator Address as your Registration Address. Your Registration Address is the wallet address containing your staking funds (e.g., your MetaMask or Ledger address).

**The information together with your password is used to restore your node in case of corruption or loss of data, so it is vital that you store it safely.**

### 1.3 Verify Node Status

To monitor the node's progress and ensure it is synchronizing with the blockchain, use:

```
sudo docker logs -f gwan
```

**Stop log view by pressing Ctrl+C**

If you see the words Validator Start Success, the node has started successfully and chain synchronization is ongoing.

You can view the node information on the [<mark style="color:blue;">WanStats</mark>](https://wanstats.io/).

### **1.4**  Synchronizing in Archive Mode (Optional)

By default, the deployment script synchronizes the node in **Full Mode**. If you require **Archive Mode** to maintain a complete history of the blockchain, please execute the following command:

```
export GCMODEENV=archive
wget https://raw.githubusercontent.com/wanchain/scripts/main/pos/mainnet/deployMainnetValidator.sh && chmod +x deployMainnetValidator.sh && ./deployMainnetValidator.sh
```

Note: Archive Mode requires a minimum of **600 GB** of available disk space.

## 2. Register Your Node

1. Access XStake [https://xstake.wanchain.org](https://xstake.wanchain.org/)
2. Navigate to **Validator Node > Setup PoS Node**
3. Fill Registration Details on the Register page:

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FbyWVMQJB6DT0aeKVggTS%2F869c4cfa-8156-4249-ab21-6e05eb521d06.png?alt=media&amp;token=c899722a-7d4b-4ebf-8193-2e097c487c58" alt=""><figcaption></figcaption></figure>

* **Public Keys:** Input Public Key 1 and Public Key 2 generated in Step 1.2.
* **Lock Period:** Select 7–90 days. *Note: Rewards increase linearly with the lock duration; a 90-day lock yields 1.5x the rewards of a 7-day lock.*
* **Accept Delegation:** Yes: Requires an initial stake of 50,000 WAN; No: Requires an initial stake of 10,000 WAN.
* **Max Fee:** The Max Fee represents the absolute upper limit for the Delegation Fee that a validator node can set. Note: Once the Max Fee is set, it is immutable and cannot be modified.
* **Delegation Fee:** The current commission rate taken from daily delegating rewards. Note: Increases are limited to a maximum of 1% per day and cannot exceed the Max Fee. Decreases are unrestricted.
* **Stake Amount:** Enter the total WAN you wish to stake from your connected wallet.

## 3. Post-Registration Maintenance

### 3.1 Fund Your Validator Address (Gas Fees)

Your Validator Address (Work Address) requires a small balance (e.g., 20 WAN) to pay for PoS-related transaction fees. Please fund your work address immediately.

### 3.2 Update Display Profile

To customize how your node appears on [wanscan.org](https://wanscan.org) (adding a logo, website, or description), please [fill out this official form](https://forms.office.com/pages/responsepage.aspx?id=VPnN3XSIEEqLYwFUDjqIlk-ycC0AzHBFlOYMrVpv55NUQUNRV1o5SDk3TTQwWlNYSkszWDFVVllNNS4u\&route=shorturl).

### 3.3 Monitoring Tools

* Network Health: Use [wanstats.io](https://wanstats.io) for global validator status.
* Explorer: Use [wanscan.org](https://wanscan.org) to view your node in the validator list.
