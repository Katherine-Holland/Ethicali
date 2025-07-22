const fs = require("fs");
const path = require("path");

async function main() {
    const { ethers } = require("hardhat");

    const EthicalAI = await ethers.getContractFactory("EthicalAI");

    console.log("🚀 Deploying EthicalAI contract...");

    const ethicalAI = await EthicalAI.deploy();
    await ethicalAI.waitForDeployment();

    // Load ABI directly from artifacts (recommended and most reliable)
    const artifactPath = path.join(__dirname, "../../blockchain/artifacts/backend/blockchain/contracts/EthicalAI.sol/EthicalAI.json");
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

    const deploymentInfo = {
        address: ethicalAI.target,
        abi: artifact.abi,
    };

    const outputPath = path.join(__dirname, "../../blockchain/abi/contract_abi.json");
    fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));

    console.log("✅ Contract deployed!");
    console.log("📍 Address:", ethicalAI.target);
    console.log("💾 ABI saved to:", outputPath);
}

main().catch((error) => {
    console.error("❌ Error deploying contract:", error);
    process.exitCode = 1;
});

