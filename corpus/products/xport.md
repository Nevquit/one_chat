
# XPort

<figure><img src="https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F5fxLZoGlrVCyejJkh1Lg%2FXPort%20Top%20Banner.png?alt=media&amp;token=eda7c658-3a86-4bff-b2e6-71d2f9f055fa" alt=""><figcaption></figcaption></figure>

XPort is Wanchain’s cross-chain data transfer protocol. It enables arbitrary data to be passed from one blockchain to another. It is composed of two basic elements: a robust off-chain relayer and a set of rudimentary on-chain smart contracts called Cross-Chain Gateways that send and receive data.&#x20;

The off-chain relayer is the same Bridge Node Group that secures all cross-chain transactions executed using the Wanchain Bridge. These permissionless Bridge Nodes are rotated and re-elected monthly. They use Multiparty Computation and Shamir’s Secret Sharing cryptography to transfer messages and arbitrary data across chains.

The Cross-Chain Gateways are a set of smart contracts deployed on each supported blockchain. These have limited functionality — they can essentially only send and receive data. They serve as the point of contact for all 3rd party developers.

Importantly, XPort is designed to be compliant with the [Enterprise Ethereum Alliance’s Distributed Ledger Technology Interoperability Specification](https://entethalliance.org/specs/dlt-interop/), co-authored by Wanchain’s VP on Engineering Dr. Weijia Zhang.
