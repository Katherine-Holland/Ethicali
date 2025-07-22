const fs = require("fs");
const path = require("path");

async function main() {
    const { ethers } = require("hardhat");

    const EthicalAI = await ethers.getContractFactory("EthicalAI");

    console.log("🚀 Deploying EthicalAI contract...");

    const ethicalAI = await EthicalAI.deploy();
    await ethicalAI.waitForDeployment();

    const deploymentInfo = {
    address: ethicalAI.target,
    abi: EthicalAI.interface.format("json"),  // ✅ No JSON.parse here
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
