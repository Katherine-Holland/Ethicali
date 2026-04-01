require("@nomicfoundation/hardhat-ethers");
require("dotenv").config();
require("hardhat-abi-exporter");

module.exports = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: "backend/blockchain/contracts",
    artifacts: "backend/blockchain/artifacts",
    cache: "backend/blockchain/cache",
    tests: "backend/blockchain/test",
  },
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [`0x${process.env.PRIVATE_KEY}`],
    },
  },
  abiExporter: {
    path: "./backend/blockchain/abi",
    runOnCompile: true,
    clear: true,
    flat: true,
    spacing: 2,
    pretty: true,
  },
};
