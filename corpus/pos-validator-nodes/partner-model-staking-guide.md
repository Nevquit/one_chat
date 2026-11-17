
# Partner Model Staking Guide

Tutorial for validators’ registration in partner model

### 1) Partner model main rules

1. Partner model has two roles: leader and partners;
2. The validator node’s PoS reward in the partner model is sent only to the leader's wallet address, therefore the distribution of PoS reward is “off-chain”;
3. The first person (Wanchain address) who registered the validator node is the leader, and Wanchain addresses other than the leader staking additional funds after the creation of the node, using partner model, are partners;
4. When the validator node no longer participates in the PoS consensus, the staking amount is returned automatically to the leader and partners’ respective wallet addresses, so there is no risk for partners to lose their staking amounts;
5. When the leader registers the validator node, the first staking amount must be no less than 10,000 WAN;
6. When partners inject funds into validator node using partner model, the first staking amount for each partner must be no less than 10,000 WAN, there is no minimum funding threshold when partners continue to inject funds after the first transaction;
7. Maximum number of partners for one single validator node is limited to 5. So maximum number of addresses injecting funds is 6, one leader plus 5 partners;
8. When the total staking amount of the leader and partners combined is less than 50,000 WAN, and the commission fee ratio is set to less than 100%, the validator node can not participate in the operation of the PoS protocol, thus will not receive PoS rewards;
9. Summary of partner model’s conditions: A) The validator node’s initial staking amount must be greater than 10,000 WAN, B) For each partner, initial staking amount must be greater than 10,000 WAN, C) When the commission fee ratio is set to less than 100% (“feeRate” value is set to less than 10000), the total staking amount of the leader and partners combined must be equal or higher than 50,000 WAN, otherwise validator node will not receive PoS rewards since it cannot participate in the PoS consensus. D) When the commission fee ratio is set to 100% (“feeRate” value is set to 10000), the total staking amount of the leader and partners combined must be equal or higher than 10,000 WAN, but it is obvious that this requirement is always met since initial staking amount of leader must be greater than 10,000 WAN.

### 2) Partner model instructions for partners using Mywanwallet

a. Access [<mark style="color:blue;">https://mywanwallet.io/#contracts</mark>](https://mywanwallet.io/#contracts)

b. Verify that you are using the correct network (Mainnet, testnet)

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FjMYy4V6CythurkgMQkxU%2Fpartner1.png?alt=media\&token=688c2b5c-8c76-4313-81ea-ebad1bbaa01b)

c. Select “Staking” smart contract in the drop-down list

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FnLUsHZHL6eHc9jNP3Mgu%2Fpartner2.png?alt=media\&token=244e544e-e553-4076-9603-1359b53046af)

d. Click “Access” button

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FuSY7Nj0HhWakqMprHY8C%2Fpartner3.png?alt=media\&token=ecfebdbf-093b-475e-b1c6-8b989b09eee8)

e. Select “PartnerIn” function in the drop-down list

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FTfJOM9VL8YkXxwStHIaZ%2Fpartner4.png?alt=media\&token=580ee1d8-7721-43d1-b6ff-1c531a2130ec)

f. Enter validator node’s address, select whether to renew the staking period or not.

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2Fnq9SdCFnBpeqBhGqDDlz%2Fpartner5.png?alt=media\&token=e6c214c9-b6a2-4480-a34e-09a3b8665060)

If you choose “False” here in “renewal”, the staking amount will quit after the end of current lock period of the validator. For example, validator (leader) has set his “lockEpochs” value to be 30, which means the staking amount of leader will be locked for 30 epochs which equals roughly 30 days. And partner joined this node using partner model at day 10, and choose to not renew automatically, then this partner’s fund will be returned 20 days later (30 days – 10 days already passed).

g. Choose your wallet that will be used to inject funds accordingly

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FMRyhWTpwUeKLVurhAWUt%2Fpartner6.png?alt=media\&token=034e724b-9626-4245-87e9-8e831b2fa1a2)

Once Mywanwallet has gained access to your wallet, click “WRITE” to confirm the operation and inject funds into validator using partner model.
