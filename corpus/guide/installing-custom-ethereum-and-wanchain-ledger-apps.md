
# Installing Custom Ethereum and Wanchain Ledger Apps

### WARNING <a href="#precautions-and-recommendations" id="precautions-and-recommendations"></a>

**This is a workaround to install custom Ethereum and Wanchain apps on your Ledger device. This is not an official solution provided by Ledger. Before implementing this workaround, it is crucial that you first transfer all your assets, except those on the Wanchain L1 blockchain, to another secure address that you control. After regaining access to your Wanchain assets, you must then also move them to another secure address that you control. Should you choose to continue to store your assets using a Ledger device, you must generate a new address with a new seed phrase. Do not continue to use your previous Ledger wallet address.**

**It is not recommended to use this workaround unless absolutely necessary. This workaround is designed for users who need to urgently access their assets and are willing to accept any and all associated risks. If you do not need to urgently access your assets, you must wait for the official Ledger team to incorporate Wanchain's pull request into a future update of the official Ledger Ethereum app.**

**You must confirm if Ledger has already incorporated Wanchain's pull request into their official Ledger Ethereum app before proceeding. If Ledger has already incorporated Wanchain's pull request, you must not use this workaround. As of April 26, 2024, the Ledger team has yet to incorporate Wanchain's pull request into their official Ledger Ethereum app. Wanchain accepts no liability for any loss or damages that may occur as a result of using this workaround.**

### Solution Overview <a href="#solution-overview" id="solution-overview"></a>

This workaround involves creating a downgraded version (1.10.3) of the Ethereum app and a Wanchain app. These apps will then be installed directly onto your Ledger device. This method also ensures that the Ledger Wanchain app remains functional with the WanWallet Desktop.

Below, we outline two solutions: Solution 1 is more technical but offers higher security. Solution 2 is simpler and requires less technical expertise.

For maximum safety, we advise not to use this workaround and to wait for the official Ledger team to incorporate Wanchain's pull request into a future update of the official Ledger Ethereum app.

### Solution 1: For Developers <a href="#solution-1-for-developers" id="solution-1-for-developers"></a>

This method is only suitable for users with development experience. You will need to set up a development environment and manually compile and install the Ethereum and Wanchain apps on your Ledger.

**The official Ledger GitHub repository provides a comprehensive guide to the** [<mark style="color:blue;">**Ledger Application Builder**</mark>](https://github.com/LedgerHQ/ledger-app-builder/) **and** [<mark style="color:blue;">**Ledger Boilerplate Application**</mark>](https://github.com/LedgerHQ/app-boilerplate?tab=readme-ov-file)**, which are invaluable resources for developers.** This user guide draws extensively from that documentation to offer you practical and detailed instructions on setting up your development environment, building apps, and installing apps.

#### **Development Environment & Building Apps**

Here is the build environment we have implemented for your reference:

Operating Systems:

* Ubuntu 20.04;&#x20;
* macOS 14.3.1;&#x20;

Docker Version:

* Docker 24.0.2

1. **Clone the Ethereum App Repository from the official Ledger GitHub channel:**

```
git clone -b 1.10.3 https://github.com/LedgerHQ/app-ethereum.git app-ethereum-1.10.3
```

2. **Prepare the Ledger Application Builder using the official scripts provided by Ledger:**

```
docker pull ghcr.io/ledgerhq/ledger-app-builder/ledger-app-builder:latest
```

```
docker run --rm -ti -v /your_path:/app --user 0 ghcr.io/ledgerhq/ledger-app-builder/ledger-app-builder:latest
```

Replace `/your_path` with the actual path to your local `app-ethereum-1.10.3` directory.

The compilation instructions in this section specifically target the Ledger Nano S device. Please note that the scripts for other Ledger models—Nano X, Nano S+, Stax, and Flex—differ slightly. If you are working with any of these models, refer to the "[<mark style="color:blue;">Compile your app in the container</mark>](https://github.com/LedgerHQ/ledger-app-builder/?tab=readme-ov-file#compile-your-app-in-the-container)" section of the [<mark style="color:blue;">Ledger Application Builder</mark>](https://github.com/LedgerHQ/ledger-app-builder/) documentation for the appropriate scripts. This ensures that you are using the correct procedures for your specific device model.

3. **Compile the Ethereum App using the official scripts provided by Ledger:**

```
BOLOS_SDK=$NANOS_SDK make clean
```

```
BOLOS_SDK=$NANOS_SDK make
```

After compilation, rename the `bin` folder to `ethereum`.

4. **Compile the Wanchain App using the official scripts specifically designed for this purpose:**

```
BOLOS_SDK=$NANOS_SDK make clean
```

```
BOLOS_SDK=$NANOS_SDK make CHAIN=wanchain
```

After compilation, rename the `bin` folder to `wanchain`.

#### **Preparing for Installation**

For your reference, our implementation utilises Python 3.10.4.

5. **Install Python and Set Up the Environment using the official scripts provided by Ledger:**

Download Python from [<mark style="color:blue;">https://www.python.org/downloads/</mark>](https://www.python.org/downloads/) and **ensure you check "Add Python to environment variables"** during installation.

```
python -m pip install virtualenv
```

```
python -m virtualenv ledger
```

6. **Activate the Virtual Environment:**

* macOS: `source ledger/bin/activate`
* Linux: `source ledger/bin/activate`

7. **Install the Ledgerblue Tool using the official scripts provided by Ledger:**

```
python -m pip install ledgerblue
```

#### **Installing Apps Using Scripts**

For your reference, the operating systems used in our installation environment are:

* Ubuntu 20.04;&#x20;
* macOS 14.3.1

8. **Exit or Uninstall Existing Apps:**

Before starting the installation process, it is important to either exit or uninstall any existing Ethereum and Wanchain apps from your Ledger device. This step ensures that there are no conflicts or issues during the installation of the new applications.

9. **Install the Ethereum App using the official scripts provided by Ledger:**

```
python -m ledgerblue.runScript --scp --fileName your_path/ethereum/app.apdu --elfFile your_path/ethereum/app.elf
```

Replace `your_path` with the actual path where you extracted the zip file. Note: After running the scripts, confirm any prompts on your Ledger device to allow the installation of the Ethereum app.

10. **Install the Wanchain App using the official scripts provided by Ledger**:

```
python -m ledgerblue.runScript --scp --fileName your_path/wanchain/app.apdu --elfFile your_path/wanchain/app.elf
```

Replace `your_path` with the actual path where you compiled and stored  the files in your local machine. Note: After running the scripts, confirm any prompts on your Ledger device to allow the installation of the Wanchain app.

### Solution 2: For General Users <a href="#solution-2-for-general-users" id="solution-2-for-general-users"></a>

If you have limited development experience, you can install the custom Ethereum and Wanchain apps using Python scripts by following these steps. Below are the technical specifications for your reference:

Operating Systems:

* Ubuntu20.04
* macOS 14.3.1
* Win 10

Python Version:

* Python 3.10.4

1. **Install Python:**&#x20;

Download the latest version from [<mark style="color:blue;">https://www.python.org/downloads/</mark>](https://www.python.org/downloads/) and **ensure you check "Add Python to environment variables"** during installation.

2. **Set Up Your Environment using the official scripts provided by Ledger:**

```
python -m pip install virtualenv
```

```
python -m virtualenv ledger
```

3. **Activate the Virtual Environment:**

* macOS: `source ledger/bin/activate`
* Windows: `.\ledger\Scripts\Activate`
* Linux: `source ledger/bin/activate`

4. **Install the Ledgerblue Tool using the official scripts provided by Ledger:**

```
python -m pip install ledgerblue
```

5. **Download and Prepare the App Files:**&#x20;

Download the `Ledger Ethereum & Wanchain apps version 1.10.3` from the Wanchain GitHub repository at [<mark style="color:blue;">https://github.com/wanchain/ledger-app-ethereum/releases/tag/eth-app-v1.10.3</mark>](https://github.com/wanchain/ledger-app-ethereum/releases/tag/eth-app-v1.10.3). Select the zip file that corresponds to your Ledger model, then extract it to a specified directory. To ensure the integrity of the downloaded file, verify the SHA256 hash and confirm that it matches the provided security checksum. This step is crucial to ensure that the file has not been tampered with or compromised.

6. **Exit or Uninstall Existing Apps:**

Before starting the installation process, it is important to either exit or uninstall any existing Ethereum and Wanchain apps from your Ledger device. This step ensures that there are no conflicts or issues during the installation of the new applications.

7. **Install the Ethereum App Using Scripts using the official scripts provided by Ledger:**

```
python -m ledgerblue.runScript --scp --fileName your_path/ethereum/app.apdu --elfFile your_path/ethereum/app.elf
```

Replace `your_path` with the actual path where you extracted the zip file. Note: After running the scripts, confirm any prompts on your Ledger device to allow the installation of the Ethereum app.

8. **Install the Wanchain App Using Scripts using the official scripts provided by Ledger**:

```
python -m ledgerblue.runScript --scp --fileName your_path/wanchain/app.apdu --elfFile your_path/wanchain/app.elf
```

Replace `your_path` with the actual path where you extracted the zip file. Note: After running the scripts, confirm any prompts on your Ledger device to allow the installation of the Wanchain app.

### **About Ledger Device Confirmation**

After running the installation scripts for the Ethereum and Wanchain apps, your Ledger device will display several security prompts that you need to manually approve. These prompts are critical as they involve permissions for installing custom software. Here are the prompts you will likely encounter and need to confirm:

1. **"Allow Unsafe Manager":** This prompt asks for your permission to bypass standard security protocols. Confirming this allows the installation of non-official apps.
2. **"Enter your Ledger PIN":** This final confirmation ensures that you are ready to proceed with the installation after all safety checks.

Be sure to review each message carefully before approval. By understanding and confirming these prompts, you ensure the intended custom apps are securely installed on your Ledger device.

### Completion and Usage

Following these steps correctly will equip your Ledger device with the necessary capabilities to perform transactions using the Wanchain app, including via the WanWallet Desktop.
