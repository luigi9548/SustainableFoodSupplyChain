require("@nomicfoundation/hardhat-toolbox");

module.exports = {
    solidity: "0.8.20",
    paths: {
        sources: "./on_chain/contracts",
        artifacts: "./on_chain/artifacts",
        cache: "./on_chain/cache"
    }
};
