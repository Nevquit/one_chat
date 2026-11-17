
# NFT Crosschain from OpenSea

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FzsMOpalnpQirSjJMSRKa%2FPoster-03.png?alt=media&amp;token=65bb4835-91b2-4286-ac3f-5cee3de3916b" alt=""><figcaption></figcaption></figure>

If a user creates an NFT through the OpenSea platform, but does not initiate any transaction, then the NFT is not actually on the chain, which is called Lazy Minting in the OpenSea mechanism. Only when the user makes a successful sending/transaction, can the NFT be actually minted on the chain.

Therefore, for users who create NFTs on OpenSea for the first time, WanBridge cannot successfully get NFTs in this state.

The Wanchain team provides the following two methods to help users turn the created NFT into the Minted state, so that it can be recognized by WanBridge, and then be able to cross-chain the NFT to other chains.&#x20;

## Use OpenSea's in-built "Transfer"

As we know, currently, your NFT is at pre-minted status, so you can use Transfer function in OpenSea to transfer your NFT to another address. By then, WanBridge can get your NFT data.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FX6mgvh2qKdwRoG6Tbirb%2F1673270652696.png?alt=media&amp;token=9418a514-4cd7-439b-8eec-9bf8cfc0cda7" alt=""><figcaption></figcaption></figure>

After your target address receives your NFT, the status of the NFT turns to the Minted status. In this case, when you choose collection OpenSea, set the From chain Ethereum and the To chain in WanBridge, the bridge can access this NFT.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FCuux78vkcmKu67yYbSxi%2F1673271007360.png?alt=media&amp;token=2f7fcf0c-1007-41aa-83f4-d8f848e64c1c" alt=""><figcaption></figcaption></figure>

If your NFT is ERC1155 and has more than one items, WanBridge also supports you to crosschain NFT items in batch by entering the number.

## Ues Aries Wallet to Transfer

Most of the cases, you don't like to turn your NFT status to minted by transferring the NFT to another address. Instead, you would like to transfer the NFT to the same address. However, the OpenSea's in-built transfer doesn't support the same addresses between the sending address and the recepient address.

In this case, we offer you a convenient & customized tool Aries Wallet to achieve it. Actually, other wallets like MyEtherWallet also supports this transfer. You can choose your favorate one.

Let's take Aries Wallet as an example.

Go to [<mark style="color:blue;">https://arieswallet.xyz</mark>](https://arieswallet.xyz), and click Add

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F0ofaoge4v7IMvDQ2NMYX%2F1673271993753.png?alt=media&amp;token=d168bba3-2c11-40e4-9973-ab7713e4ac8e" alt=""><figcaption></figcaption></figure>

Type the Contract Name **ERC1155**, Contract Address **0x495f947276749ce646f68ac8c248420045cb7b5e**, and ABI below. Click **OK**.

```
[
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "account",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "ApprovalForAll",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256[]",
				"name": "ids",
				"type": "uint256[]"
			},
			{
				"indexed": false,
				"internalType": "uint256[]",
				"name": "values",
				"type": "uint256[]"
			}
		],
		"name": "TransferBatch",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "TransferSingle",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "value",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "URI",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address[]",
				"name": "accounts",
				"type": "address[]"
			},
			{
				"internalType": "uint256[]",
				"name": "ids",
				"type": "uint256[]"
			}
		],
		"name": "balanceOfBatch",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "isApprovedForAll",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256[]",
				"name": "ids",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[]",
				"name": "amounts",
				"type": "uint256[]"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeBatchTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "setApprovalForAll",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes4",
				"name": "interfaceId",
				"type": "bytes4"
			}
		],
		"name": "supportsInterface",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "uri",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
```

Click **Access** and then **Write Contract**

Choose the item 2 funtion **safeTransferFrom**

Type the from address, the to address (same to from address), the ID (NFT token ID can be found in OpenSea under the details of NFT), the amount (how many items you want to transfer), and the data (by default, we put 0x here)

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FxdpsT7vguCfnf6iySun1%2F1673272595726.png?alt=media&amp;token=eb1d2bb9-daf5-4989-9f4b-edee9c1b19b6" alt=""><figcaption></figcaption></figure>

Click **Write**

Wait for a while, your address will receive those NFT(s) and the status changed to Minted. By then, the NFT(s) can be accessed by WanBridge and be crosschained to other chains through it.

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F8vaT42RciMIgmaMZhN4n%2F1673272765155.png?alt=media&amp;token=167bb96d-a23f-4dc0-8aee-c89136bee64a" alt=""><figcaption></figcaption></figure>
