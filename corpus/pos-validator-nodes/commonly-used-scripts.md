
# Commonly Used Scripts

## Testnet Validator Node Setup Script

```
```

## Testnet Validator Node Update Script

```
rm updateValidator.sh
wget https://raw.githubusercontent.com/wanchain/go-wanchain/develop/loadScript/updateValidator.sh && chmod +x updateValidator.sh && ./updateValidator.sh
```

## Mainnet Validator Node Setup Script

```
```

## Mainnet Validator Node Upgrade Script

```
rm updateMainnetValidator.sh
wget https://raw.githubusercontent.com/wanchain/scripts/main/pos/mainnet/updateMainnetValidator.sh && chmod +x updateMainnetValidator.sh && ./updateMainnetValidator.sh
```

## Node Restart Script

This script only works for non-deleted data restarts of docker nodes launched with the above startup and upgrade scripts.

```
rm updateMainnetValidator.sh
wget https://raw.githubusercontent.com/wanchain/scripts/main/pos/mainnet/updateMainnetValidator.sh && chmod +x updateMainnetValidator.sh && ./updateMainnetValidator.sh
```

## Delete Node Script

```
sudo pkill gwan
sudo docker rm gwan
```
