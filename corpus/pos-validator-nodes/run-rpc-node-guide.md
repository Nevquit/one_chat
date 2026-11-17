
# Run RPC Node Guide

Running your own node is the most direct way to connect to and interact with the **Wanchain network**.\
This guide explains how to set up and run an RPC node step by step.

***

## System Requirements

| Hardware           | Requirement |
| ------------------ | ----------- |
| **CPU**            | 2 cores     |
| **Memory**         | 8 GB        |
| **Disk (archive)** | 600 GB      |
| **Disk (full)**    | 200 GB      |

***

## Supported Operating Systems

The following operating systems are supported:

* Linux (x64)
* Linux (ARM)
* Windows (x64)
* macOS (x64)

***

## Required Ports

A Wanchain node requires the following open ports:

* **17717** – for P2P communication
* **8545** – for RPC access

Please make sure these ports are open in your firewall.\
You can also configure the port numbers via CLI parameters.

***

## Running a Mainnet RPC Node (Binary)

{% stepper %}
{% step %}

### Download the latest binary

```bash
wget https://github.com/wanchain/go-wanchain/releases/download/v3.0.2/gwan-linux-amd64.tgz
```

{% endstep %}

{% step %}

### Extract and rename

```bash
tar zxf gwan-linux-amd64.tgz
mv gwan-linux-amd64 gwan
```

{% endstep %}

{% step %}

### Run the node (archive mode)

```bash
./gwan --http --http.addr 0.0.0.0 --http.port 8545
```

Or, to save disk space, run in full mode:

```bash
./gwan --gcmode=full --http --http.addr 0.0.0.0 --http.port 8545
```

{% endstep %}
{% endstepper %}

{% hint style="info" %}
The command-line interface is similar to Ethereum’s Geth client. Use `./gwan --help` to view additional parameters.
{% endhint %}

***

## Running a Testnet RPC Node (Binary)

To run a testnet node, add the `--testnet` flag.

{% stepper %}
{% step %}

### Download and extract the binary

Download and extract the binary as shown in the Mainnet Binary steps above.
{% endstep %}

{% step %}

### Start the testnet node

Archive mode:

```bash
./gwan --testnet --http --http.addr 0.0.0.0 --http.port 8545
```

Full mode (less disk usage):

```bash
./gwan --testnet --gcmode=full --http --http.addr 0.0.0.0 --http.port 8545
```

{% endstep %}
{% endstepper %}

***

## Running a Mainnet RPC Node (Docker)

```bash
sudo docker run -d --name wanchain-node     -v /home/ubuntu/wanchain:/root     -p 8545:8545 -p 17717:17717     wanchain/client-go:3.0.2 gwan     --gcmode=full --http --http.addr 0.0.0.0 --http.port 8545
```

***

## Running a Testnet RPC Node (Docker)

```bash
sudo docker run -d --name wanchain-node     -v /home/ubuntu/wanchain:/root     -p 8545:8545 -p 17717:17717     wanchain/client-go:3.0.2 gwan     --testnet --gcmode=full --http --http.addr 0.0.0.0 --http.port 8545
```
