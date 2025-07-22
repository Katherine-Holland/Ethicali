require("@nomicfoundation/hardhat-ethers");
require("dotenv").config();

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
      url: "https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_1",
      accounts: [`0x${process.env.PRIVATE_KEY}`],
    },
  },
};
