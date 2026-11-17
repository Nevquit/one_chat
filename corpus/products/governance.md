
# Governance

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FkUzobO1zxDQXOOF463yI%2FWanchain%20Governance.png?alt=media&amp;token=3554ee70-3c63-4a0b-b152-1dc47f80383f" alt=""><figcaption></figcaption></figure>

## Platform Overview

The Wanchain Governance Platform is a governance tool that enables community members to submit and vote on proposals. Through the platform, the community can collectively decide how to:

* Allocate and spend funds from the Community Treasury.
* Adjust the Convert n’ Burn percentage split.
* Change the governance platform’s adjustable parameters.
* Improve the Wanchain ecosystem in other ways.

**Supported devices:** Desktop and mobile. Access the platform using a desktop browser with an EVM-compatible wallet such as MetaMask, or the built-in browser in a mobile wallet app.

**Platform URL:** <https://governance.wanchain.org/>

Community members can create two types of proposals: **Funding** proposals, which request funds from the Community Treasury, and **Technical** proposals, which do not request funding and may cover changes such as adjustments to system parameters.

## Funding Proposals

This section walks you through the complete lifecycle of a Funding proposal, from creation to settlement.

### Step 1 Create a Proposal

Open the platform and connect your wallet. Click **Submit Proposal** in the homepage banner to open the proposal creation page, then enter the required information:

* Select **Funding** from the **Category** dropdown.
* Enter the amount of WAN requested from the Community Treasury.
* Provide a detailed description of how the WAN will be used.

After submission, your proposal has **Pending** status, and the platform temporarily holds your pledge while the proposal awaits review.

![Creating a Funding proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FZaSUIQfiHSzOS70ZbPAR%2F1.jpg?alt=media\&token=37b43e92-f13e-4748-9183-791e01eaa6be)

#### Before You Submit

Make sure you have enough WAN for your pledge and enough XP to cover the **Proposal Creation Cost** of **110,000 XP** per proposal. Learn more: [What is XP?](https://docs.wanchain.org/products/wanbridge/xp)

The requested amount must not exceed **10%** of the total Community Treasury balance.

Under **Collateral Configuration**, choose **Lock** or **Burn**. For proposers, Lock has a term of **6 months (6 × 30 days)** and allows a funding request of up to **10 times** the pledged amount. Burn allows a funding request of up to **50 times** the pledged amount. Choose carefully: once WAN is burned, it is permanently destroyed and cannot be recovered. The review process in Step 2 explains when the selected option takes effect.

**PoS staking and rewards:** If you choose Lock and the proposal passes the community vote, your pledged WAN will be staked with Wanchain PoS node and earn staking rewards. Your principal remains locked for the specified term. Once the term ends, click **Unstake**, wait **5 days**, then click **Claim** to withdraw your principal and rewards together. If the proposal does not pass, your locked WAN will be unlocked and available to claim in **My Proposals**, without rewards.

Enter at least **1 WAN** in **Your Pledge Amount**. The amount you pledge determines whether your proposal can become active immediately after approval.

**Min. required to activate proposal** shows the activation threshold. The proposal meets this threshold when the pledge amount multiplied by the applicable collateral multiplier is at least equal to the requested funding amount. If your pledge falls short, you can still create a **Prospective Proposal** and seek additional pledges from community sponsors to reach the threshold, as illustrated below.

Provide your contact details so the team can get in touch if needed.

![A pledge that meets the activation threshold](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FOpkdCOHrRGzce08SH3KZ%2F2.jpg?alt=media\&token=56f11aa9-fd5e-4241-abf6-1a7e91bc97c4)

![A pledge that requires additional community sponsorship](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FmDG5zZ2m2oFFCZkJhHI6%2F3.jpg?alt=media\&token=4f65ae9d-a83b-47e6-a5c3-6b5a30894b0d)

### Step 2 Await Team Review

The Wanchain team reviews your proposal after you submit it.

**If you cancel before review:** Open **My Proposals**, select the proposal, and click **Cancel**. Your XP and WAN are automatically returned to your account, regardless of whether you selected Lock or Burn. The proposal is closed.

**If the team rejects the proposal:** Your XP and WAN are automatically returned to your account, regardless of whether you selected Lock or Burn. The proposal is closed.

**If the team approves the proposal:** It is published and can no longer be canceled. Your WAN pledge is then locked or burned according to the option you selected when creating the proposal.

If your pledge meets the activation threshold, the proposal becomes an **Active Proposal** and moves directly to voting. Continue to **Step 4**.

![An Active Funding proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FK6ZXCisAMDgAzqFPZ2pL%2F4.png?alt=media\&token=ae9ef4f9-ac58-4b16-9d93-f5e97b399615)

If your pledge does not meet the activation threshold, the proposal becomes a **Prospective Proposal** and enters the sponsorship phase described in **Step 3**.

![A Prospective Funding proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F9APzvhjvNtCPn4PD78aq%2F5.png?alt=media\&token=cd4a3032-0eab-4ff3-95b5-63d08689d5d9)

### Step 3 Secure Community Sponsorship

An approved proposal that has not yet reached the activation threshold has **30 days** to secure additional pledges from community members.

The **Prospective** tab on the homepage lists proposals seeking sponsorship and shows their progress toward activation. Any user can choose a proposal to sponsor. **Each address can sponsor a given proposal only once.**

Under **Sponsorship Type**, choose **Lock** or **Burn**. For sponsors, Lock has a term of **6 months (6 × 30 days)**, and each WAN pledged counts as **10 WAN** toward the requested funding amount. With Burn, each WAN pledged counts as **50 WAN** toward that amount. Choose carefully: WAN committed through Burn is destroyed immediately and cannot be recovered.

**PoS staking and rewards:** If you sponsor a proposal using Lock and it passes the community vote, your pledged WAN will be staked with Wanchain PoS nodes and earn staking rewards. Your principal remains locked for the specified term. Once the term ends, click **Unstake**, wait **5 days**, then click **Claim** to withdraw your principal and rewards together. If the proposal does not pass, your locked WAN will be unlocked and available to claim in **My Sponsorships**, without rewards.

![Sponsoring a Prospective Proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2Fn8d5Bzij4WurEupEqL1i%2F6.jpg?alt=media\&token=6b2d8189-d3b8-4198-a223-b6fd3f9a7aaa)

**If the sponsorship target is reached:** The proposal becomes **Active** and moves to the voting phase in **Step 4**. WAN pledged through Lock by the proposer and all sponsors remains locked.

**If the deadline passes before the target is reached:** The proposal receives **Failed** status and is closed. WAN pledged through Lock by the proposer and sponsors is unlocked. Proposers can click **Claim** in **My Proposals**; sponsors can click **Claim** in **My Sponsorships**.

### Step 4 Vote on the Active Proposal

The voting period lasts **14 days**.

The **Active** tab on the homepage lists proposals open for voting and shows their current voting progress. Any user can choose a proposal to vote on. **Each address can vote on a given proposal only once.**

![A Funding proposal open for voting](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2Fvjp2fjCwoCVGJ2zhfc9i%2F7.png?alt=media\&token=d612023b-1156-4a46-9f46-963d1c2dce9c)

*A Funding proposal open for voting*

Select **Yes** or **No**, then choose **Lock** or **Burn** under **Voting Mechanism**. Your voting weight depends on the option you select:

* Lock for **6 months (6 × 30 days)**: **1 WAN = 10 votes**.
* Lock for **3 months (3 × 30 days)**: **1 WAN = 5 votes**.
* No lock-up: **1 WAN = 1 vote**.
* Burn: **1 WAN = 25 votes**.

**PoS staking and rewards:** If you select a **90-day or 180-day lock-up** and the proposal passes, your WAN will be staked with Wanchain PoS nodes and earn staking rewards. Your principal remains locked for the selected term. Once the term ends, click **Unstake**, wait **5 days**, then click **Claim** to withdraw your principal and rewards together. If the proposal does not pass, your locked WAN will be unlocked and available to claim in **My Votes**, without rewards.

Your WAN is locked or burned according to your selection. Choose carefully: WAN committed through Burn is destroyed immediately and cannot be recovered.

![Selecting a voting option for a Funding proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FcmneWSNEnTpDPAz6ala0%2F8.jpg?alt=media\&token=0b5822a3-9459-491f-bf2c-2a2ef036d533)

A Funding proposal passes only if **both** conditions are met:

* At least **75%** of the votes are **Yes**.
* The total number of votes is at least **3 times** the amount of WAN requested from the Community Treasury.

Open the proposal details to view the current voting totals.

### Step 5 Settle After Voting Ends

**If the proposal passes:** You are eligible to receive the requested funding. The team will contact you and transfer the funds to the relevant address.

![A Funding proposal that has passed](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FBQXfA2AoPkOHvPjYBbv6%2F9.png?alt=media\&token=af3c75b4-2e21-4e19-b14c-35ce12fb95ed)

Settlement applies to **proposers, sponsors, and voters**:

**Burn:** All WAN committed through Burn is permanently destroyed.

**Lock:** Your WAN remains locked for the agreed term. Locked WAN is staked with Wanchain proof-of-stake (PoS) nodes and earns rewards at the corresponding PoS node rate. When the lock-up term ends, you can click **Unstake**. After **5 days**, you can click **Claim** to withdraw all your principal and rewards.

**If the proposal does not pass:** The requested funding is not awarded.

Settlement applies to **proposers, sponsors, and voters**:

**Lock:** Your WAN is unlocked. Click **Claim** in **My Proposals**, **My Sponsorships**, or **My Votes**, as applicable, to withdraw your principal. **No rewards are earned.**

**Burn:** All WAN committed through Burn is permanently destroyed.

**PoS staking and rewards:** If you select a **90-day or 180-day lock-up** and the proposal passes, your WAN will be staked with Wanchain PoS nodes and earn staking rewards. Your principal remains locked for the selected term. Once the term ends, click **Unstake**, wait **3 days**, then click **Claim** to withdraw your principal and rewards together. If the proposal does not pass, your locked WAN will be unlocked and available to claim in **My Votes**, without rewards.

## Technical Proposals

This section walks you through the complete lifecycle of a Technical proposal, from creation to settlement.

### Step 1 Create a Proposal

Open the platform and connect your wallet. Click **Submit Proposal** in the homepage banner to open the proposal creation page, then enter the required information:

* Select **Technical** from the **Category** dropdown.
* Provide a detailed description of the division of responsibilities, including whether you need support from the Wanchain team.

After submission, your proposal has **Pending** status.

![Creating a Technical proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F0Hll2ZxjmCiP6AFP3X0u%2F10.png?alt=media\&token=1587a665-0948-4cf2-8449-1dd8a88da227)

#### Before You Submit

Make sure you have enough XP to cover the **Proposal Creation Cost** of **110,000 XP** per proposal.

### Step 2 Await Team Review

The Wanchain team reviews your proposal after you submit it.

**If you cancel before review:** Open **My Proposals**, select the proposal, and click **Cancel**. Your XP is automatically returned to your account, and the proposal is closed.

**If the team rejects the proposal:** Your XP is automatically returned to your account, and the proposal is closed.

**If the team approves the proposal:** It is published and can no longer be canceled. Your XP is burned.

The proposal moves directly to the voting phase.

### Step 3 Vote on the Approved Proposal

The voting period lasts **14 days**.

The **Active** tab on the homepage lists proposals open for voting and shows their current voting progress. Any user can choose a proposal to vote on. **Each address can vote on a given proposal only once.**

![A Technical proposal open for voting](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F1dTo3fKaQWUZQBXSNR2y%2F11.png?alt=media\&token=3bf7bb74-8f9b-46dd-b00f-778910164b2d)

*A Technical proposal open for voting*

Select **Yes** or **No**, then choose **Lock** or **Burn** under **Voting Mechanism**. Your voting weight depends on the option you select:

* Lock for **6 months (6 × 30 days)**: **1 WAN = 10 votes**.
* Lock for **3 months (3 × 30 days)**: **1 WAN = 5 votes**.
* No lock-up: **1 WAN = 1 vote**.
* Burn: **1 WAN = 25 votes**.

Your WAN is locked or burned according to your selection. Choose carefully: WAN committed through Burn is destroyed immediately and cannot be recovered.

![Selecting a voting option for a Technical proposal](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FuSWvztWrjKF2qScpZcPW%2F12.jpg?alt=media\&token=ee8e402c-37e5-4508-9f73-aac7c2b6b857)

A Technical proposal passes only if **both** conditions are met:

* At least **75%** of the votes are **Yes**.
* The total number of votes is at least **0.5% of the total WAN supply**, equivalent to **1,050,000 votes**.

Open the proposal details to view the current voting totals.

### Step 4 Settle After Voting Ends

**If the proposal passes:** The team will implement the proposed technical changes.

![A Technical proposal that has passed](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FzjXiGybJE1ZDgePZWpyz%2F13.png?alt=media\&token=c2c2d31b-ba48-47bf-8858-77870b67f504)

Settlement applies to **voters only**:

**Burn:** All WAN committed through Burn is permanently destroyed.

**Lock:** Your WAN remains locked for the agreed term. Locked WAN is staked with Wanchain proof-of-stake (PoS) nodes and earns rewards at the corresponding PoS node rate. When the lock-up term ends, you can click **Unstake**. After **3 days**, you can click **Claim** to withdraw all your principal and rewards.

**If the proposal does not pass:** The team will not proceed with the proposed technical changes at this time.

Settlement applies to **voters only**:

**Lock:** Your WAN is unlocked. Click **Claim** in **My Votes** to withdraw your principal. **No rewards are earned.**

**Burn:** All WAN committed through Burn is permanently destroyed.
