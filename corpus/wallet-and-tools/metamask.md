
# MetaMask

![](https://camo.githubusercontent.com/370ad8625d81ff0e001ae6fd272aa4bebcbfbc842b513b47b2cb94325033a6ed/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536363239323238302d32303332376664372d333263612d343037662d383966352d6561656136333565643764652e706e6723636c69656e7449643d7533393232366430622d383135622d342666726f6d3d75692669643d756c6a4e48266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d393030266f726967696e57696474683d31363030266f726967696e616c547970653d62696e6172792673697a653d32303437383139267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7565353661613936632d323333632d343931632d623365662d6136316634316437653636)

On April 15, 2021, Wanchain completed a major upgrade to the Jupiter version. So far, Wanchain has achieved full compatibility with the EVM. Therefore, MetaMask, the most popular browser plug-in wallet on Ethereum, can also connect to Wanchain (including the support of Ledger and Trezor hardware wallets).

For MetaMask to connect to Wanchain, we provide two configuration methods.

## Method 1: Quick configuration

Using the functions provided by the [<mark style="color:blue;">chainlist.org</mark>](https://chainlist.org) website，you can quickly add the Wanchain network to the MetaMask browser plug-in wallet.

First, open [<mark style="color:blue;">https://chainlist.org</mark>](https://chainlist.org) in Chrome.

Enter **Wanchain** in the search box above

![](https://camo.githubusercontent.com/e04cf78dd44d39cdf54aa2078d770c1c28fc5ee3adb41cabdf795760492d13fc/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536333834393438322d33623865313935632d333937642d343765622d613931372d3336613762653261633663642e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3236382669643d753736333462346366266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d333439266f726967696e57696474683d383837266f726967696e616c547970653d62696e6172792673697a653d3737313839267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7565366532626537632d656633392d343062382d613236302d30656233333335613261342677696474683d3638302e35)

Then click the **Connect Wallet** button below to connect to MetaMask.

Then click the **Add To Metamask** button to complete the add the Wanchain network.

![](https://camo.githubusercontent.com/b859118108ce7835c2e772f3c8d13de567763f352e6334ce381708237046ed9f/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536333836393539322d35373638333531332d313232642d343436622d623037392d6663373730653039616136352e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3232312669643d756430303335663662266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d323332266f726967696e57696474683d343332266f726967696e616c547970653d62696e6172792673697a653d3334333339267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7536376661343130392d656134362d346330362d616366352d62333435636438333162662677696474683d343131)

After completing the adding, you can select MetaMask wallet in Wanchain's Dapps.

## Method 2: Manual configuration

### Connect to Wanchain mainnet

Click the network menu at the top of the MetaMask page, and select the **Custom RPC** at the bottom of the pop-up menu.

![](https://camo.githubusercontent.com/68ab38888622c6bb49d3bb7e533cd5edc1f080e53eafc1760b44ae602dbee172/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536343032363430382d36303837343131312d313638372d343934362d383864622d3966653633333461366430362e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3736392669643d756338373963383262266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d373639266f726967696e57696474683d333737266f726967696e616c547970653d62696e6172792673697a653d313036353234267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7565363066373133372d396561362d343837612d396232342d63656439386263333730662677696474683d333737)

Then fill in the RPC information as shown in the figure below, and click the **Save** button:

![](https://camo.githubusercontent.com/995b172ec15fd801ea327ac34e5f52198b3ceb0d7080f6c2bbc4ad00076d2140/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536343139343937332d62316433663334322d646564372d343764332d626564362d3533303837663939656234372e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3535322669643d753262623034396134266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d353938266f726967696e57696474683d343239266f726967696e616c547970653d62696e6172792673697a653d3431333230267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7530363666346232362d306666612d343931302d393061372d34363232613831356637302677696474683d333936)

```
Network Name: Wanchain
New RPC URL: https://gwan-ssl.wandevs.org:56891
Chain ID:888
Currency Symbol: WAN
Block Explorer URL: https://www.wanscan.org
```

After adding, you can use MetaMask to connect to the Wanchain mainnet to send transactions.

### Connect to Wanchain test network

Click the network menu at the top of the MetaMask page, and select the **Custom RPC** at the bottom of the pop-up menu.

![](https://camo.githubusercontent.com/7ce7090a4ffec9906c7062f6db47a1a8f51729068100693ea36735f63a39d187/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536343337323231382d36343338353930362d376337312d346333352d393332652d3237303736356565323166312e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3732372669643d753366623663376631266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d373639266f726967696e57696474683d333737266f726967696e616c547970653d62696e6172792673697a653d313036353234267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7530333937636434652d306632312d343038642d396632312d61373166323735626130392677696474683d3335362e35)

Then fill in the RPC information as shown in the figure below, and click the **Save** button:

![](https://camo.githubusercontent.com/20244312f8df211097bb15a445a4e2cde37bccef75d35918945429f8bf472d63/68747470733a2f2f63646e2e6e6c61726b2e636f6d2f79757175652f302f323032312f706e672f323330383938382f313631383536343430373435362d65353965343834392d623265332d343362392d383064362d3833316364613235656131652e706e6723636c69656e7449643d7535336265323061392d346361352d342666726f6d3d7061737465266865696768743d3537342669643d753834653262336234266d617267696e3d2535426f626a6563742532304f626a656374253544266f726967696e4865696768743d353734266f726967696e57696474683d333835266f726967696e616c547970653d62696e6172792673697a653d3432373033267374617475733d646f6e65267374796c653d6e6f6e65267461736b49643d7565646235623661302d363332342d346132632d623935302d38393062623063363266312677696474683d333835)

```
Network Name: Wanchain
New RPC URL: https://gwan-ssl.wandevs.org:46891
Chain ID: 999
Currency Symbol: WAN
Block Explorer URL: https://testnet.wanscan.org
```

After adding, you can use MetaMask to connect to the Wanchain testnet to send transactions.

## How to crosschain your assets using WanBridge Web <a href="#id-469f" id="id-469f"></a>

**Step 0: Make sure you have the appropriate wallets.**

Before completing decentralised crosschain transactions using WanBridge Web, you need to ensure you have access to the correct wallet(s). You must have wallets for each network involved in the crosschain transaction. In other words, if you are moving $BTC from Bitcoin to Ethereum, you need to use Bitcoin and Ethereum wallets. Similarly, if you are moving $LTC from Wanchain to Moonriver, you need Wanchain- and Moonriver-compatible wallets.

This guide demonstrates a crosschain transaction moving $ETH from Ethereum to Wanchain and uses [<mark style="color:blue;">Metamask</mark>](https://metamask.io/). [<mark style="color:blue;">Metamask</mark>](https://metamask.io/) is a fantastic wallet that grants you access to any EVM-compatible blockchain network.

[<mark style="color:blue;">Download Metamask here</mark>](https://metamask.io/).

**Step 1: Visit** [<mark style="color:blue;">**https://bridge.wanchain.org/**</mark>](https://bridge.wanchain.org/#/)

**Step 2:** Click “**Select asset please**” on the left side of the terminal.

![](https://miro.medium.com/max/1400/1*Gttxz9PbTObnf2rSYU5xrg.png)

**Step 3:** Select the asset you want to move crosschain from one blockchain network to another.

In this example, we select $ETH because we are moving $ETH.

![](https://miro.medium.com/max/1400/1*yq1uy0Ukn3KKQb49PhOtDA.png)

**Step 4:** Click “**Select From Chain**” and select the origin chain.

In this example, the origin chain is Ethereum because the $ETH is currently on Ethereum.

![](https://miro.medium.com/max/1400/1*1faZOo1MJnrTFMDfJ3szKw.png)

**Step 5:** Click “**Select To Chain**” and select the destination chain.

In this example, we are moving $ETH to Wanchain. So, Wanchain is the destination chain.

![](https://miro.medium.com/max/1400/1*FORXIPCI3sHGCLQ5w8UKfA.png)

**Step 6.** Click “**Connect to Wallet**” in the top right corner of the window.

**Step 7:** Select the appropriate wallet.

In this example, we are using [<mark style="color:blue;">MetaMask</mark>](https://metamask.io/) connected to the Ethereum network.

![](https://miro.medium.com/max/1400/1*R_o7iNUo_cZ6tY5hJmZYdw.png)

When connecting [<mark style="color:blue;">Metamask</mark>](https://metamask.io/) for the first time, you will need to click **connect** in the [<mark style="color:blue;">Metamask</mark>](https://metamask.io/) pop-up window. Your Ethereum wallet address will now be connected to [<mark style="color:blue;">WanBridge Web</mark>](https://bridge.wanchain.org/#/). Your ETH balance should also be visible.

![](https://miro.medium.com/max/1400/1*JtWSj9QAJCCb1UpW7ZkT9w.png)

**Step 8:** Enter your recipient address. This is the address that you want to send your assets to on the destination chain.

In this example, as we are moving $ETH to Wanchain, the **Recipient** address is a Wanchain address.

**Step 9:** Enter the amount you wish to convert and then click “**Next**”.

![](https://miro.medium.com/max/1400/1*jBuLC80x0BreBFEHsCtusQ.png)

**Step 10:** On the next page, review all the information relating to your crosschain transaction and click “**Confirm**”.

![](https://miro.medium.com/max/1400/1*xycN966drj4eNKVnW1onFw.png)

Be sure to double check your **To** address and the **Amount** you are sending crosschain. When using Metamask, you will also need to confirm the transaction in the MetaMask pop-up window. Make sure to use an appropriate gas fee to ensure your ETH transaction doesn’t get delayed.

**Step 11:** Wait.

![](https://miro.medium.com/max/1400/1*T7404OYI1AVJZEhzR3UP9A.png)

Your crosschain transaction is now being processed. It will appear as **Processing**. The amount of time a crosschain transaction takes is entirely depending on the speed of the blockchain networks involved. For example, an $XRP transaction from XRP Ledger to Avalanche might only take a few minutes while a $BTC transaction from Bitcoin to Binance Smart Chain could take an hour.

**Step 12:** Confirm the receipt of your funds.

![](https://miro.medium.com/max/1400/1*9R5kslJBNbKfEqu8yEIqYg.png)

Once your crosschain transaction status changes to **Complete**, you can confirm receipt of funds in your **Recipient** address. In this example, the **Recipient** Wanchain address now has $wanETH.

Congratulations! You have completed a crosschain transaction using Wanbridge Web!

*Note: Crosschain assets use different nomenclature depending on the destination chain. Assets moved to Wanchain use the ‘wan’ prefix (ie. ETH becomes wanETH, XRP becomes wanXRP, etc.). Crosschain assets on different blockchain networks may use a slightly different naming scheme. For instance, crosschain assets on Avalanche use the ‘.a’ suffix (ie. BTC becomes BTC.a, WAN becomes WAN.a).*
