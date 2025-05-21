# SustainableFoodChain: A Blockchain-based Food Supply Chain DApps

## Table of Contents

- [Introduction](#introduction)
    - [Overview](#overview)
    - [Key Features](#key-features)
    - [Technologies Used to Develop](#technologies-used-to-develop)
- [Installation](#installation)
    - [Requirements](#requirements)
    - [Setup in UNIX-like OS's](#setup-in-unix-like-oss)
    - [Setup in Windows](#setup-in-windows)
- [How to use it](#how-to-use-it)
    - [First look](#first-look)
    - [Bonus track: Scripts](#bonus-track-scripts)
- [Contributors](#contributors)

## Introduction

Welcome to **SustainableFoodChain**, a decentralized DApp that traces products from agriculture to the final seller while tracking CO₂ emissions. By integrating carbon accounting and credit mechanisms, it promotes transparency and sustainability across the entire food supply chain.

### Overview
SustainableFoodChain is a blockchain-based platform designed to enhance transparency and sustainability across the entire food supply chain. By leveraging Ethereum for secure and immutable data recording, combined with Python for off-chain operations, the platform enables all participants—from farmers to sellers—to track products and monitor their environmental impact effectively. SustainableFoodChain aims to foster trust and accountability by providing a reliable and transparent system that supports sustainable practices throughout the supply chain.

### Key Features

The platform offers a comprehensive set of features designed to ensure transparency, sustainability, and security throughout the food supply chain:

- **Product Traceability**: Enables tracking of food products across all supply chain stages, ensuring transparency and authenticity.

- **Carbon Footprint Monitoring**: Records CO₂ emissions at every phase, supporting measurement and reduction initiatives.

- **Decentralized and Secure**: Uses blockchain technology to guarantee tamper-proof records and trustworthy verification.

- **Carbon Credit Integration**: Rewards sustainable practices through a system of carbon credits to incentivize eco-friendly behavior.

- **Multi-role Access**: Supports different supply chain participants (farmers, carriers, processors, sellers) with tailored permissions.

- **Modular Architecture**: Utilizes Docker containerization to isolate backend services and blockchain simulation for robust and easy deployment.

- **Role-based Security**: Ensures data privacy and controlled access through defined user roles.

- **User-friendly Interface**: Designed for intuitive use by all participants, regardless of technical background.

### Technologies Used to Develop

- [Python](https://www.python.org/) -> Main programming language
- [Sqlite3](https://www.sqlite.org/) -> Database used
- [Ganache](https://archive.trufflesuite.com/ganache/) -> Personal blockchain as Ethereum simulator
- [Web3](https://web3py.readthedocs.io/en/stable/) -> Python library for interacting with Ethereum
- [Docker](https://www.docker.com/) and [Docker-compose](https://docs.docker.com/compose/) -> Containerization
- [Solidity](https://soliditylang.org/) -> Smart contract development
- [Py-solc-x](https://solcx.readthedocs.io/en/latest/) -> Solidity compiler
- [Unittest](https://docs.python.org/3/library/unittest.html) -> Unit testing framework

### Installation

To run the SustainableFoodChain application, please follow the steps below.

### Requirements

Before getting started, ensure that Docker is installed on your machine. Docker provides an isolated environment by running the application components in containers, which guarantees portability and security. You can download Docker from [here](https://www.docker.com/).

Also, make sure `git` is installed on your system. In **Windows** systems, you could download [here](https://git-scm.com/download/win) the latest version of **Git for Windows**. On **UNIX-like systems, you can install Git by running**

```bash
sudo apt install git
```

### Setup on UNIX-like OSs

First, clone the repository by opening your terminal and running the following command:
```bash
git clone https://github.com/luigi9548/SustainableFoodSupplyChain
```
Then, move into the project directory:
```bash
cd SustainableFoodChain
```
If you wish to rebuild the Docker images from scratch (without using cached layers), run:
```bash
docker-compose build --no-cache
```
Once ready, you can start all required Docker containers (including the local Ethereum blockchain via Ganache and the backend services) by executing:
```bash
docker-compose up -d
```
You can verify if the services were started correctly by inspecting the logs: `docker-compose logs`.
Make sure your user has the appropriate privileges to run Docker commands. If not, prepend each command with `sudo`.

### Setup on Windows
To run the application on Windows, open **Windows PowerShell** and execute the same commands listed above from within the project directory.

If Docker commands don’t work, ensure that Docker Desktop is running in the background — it is required to enable Docker on Windows systems.

### Setup on macOS
On macOS, the setup process is identical to the UNIX-like system instructions and can be followed via the Terminal.

In case `docker-compose` fails to execute due to platform architecture issues, you may need to set the Docker default platform explicitly. You can do so with:
```bash
sudo DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose run -it supplychain
```
After this step, the application should function correctly.

### How to Use It
Once the setup has been completed, you can launch the main application interface by running the following command:
```bash
docker-compose run -it supplychain
```

Be sure to include the `-it` flags: `-i` keeps the container's *STDIN* open, while `-t` allocates a *pseudo-TTY*, allowing you to interact with the CLI-based interface of the application directly from the terminal.

At this point, the program is ready to use. After the command is executed and all containers are properly deployed, you’ll be able to interact with the system via the terminal window that appears.

### First Look

During the first launch, the application performs a startup check to ensure the local Ethereum blockchain (Ganache) is active and listening. If everything is in place, SustainableFoodChain will load successfully and display the home screen.

You will now be able to *register* a new user as a Farmer, Carrier, Processor, or Seller — or *login* if you’re already registered — and begin exploring the platform’s features.

For testing purposes, sample credentials are included in the repository inside the `scripts/credentials.txt` file.
Enjoy the journey toward a more transparent and sustainable food supply chain!

> **NOTE**: To fully test the application, you will **need** both the *public key* and *private key* during registration. You can obtain these by either accessing Ganache directly or using the extract script provided (see below).
This script is intended for **educational purposes only** and should not be used in production environments for security reasons.

### Bonus Track: Scripts
To simplify user testing and registration, the following utility scripts are included in the `/scripts` directory:

1. `extract` -> Extracts Ganache logs (via Docker) to display both *public* and *private key*s used during contract deployment.
2. `gen_password` -> Generates a list of random passwords that comply with the platform's required Regex format.

You can execute these scripts by first navigating to the `/scripts` folder and making the scripts executable:

```bash
chmod +x ./SCRIPT_NAME.sh
```
Then run the desired script:

```bash
./SCRIPT_NAME.sh
```
Replace `SCRIPT_NAME` with the actual name of the script you want to execute (e.g., extract or gen_password).
Generated outputs such as passwords or credentials can be found in their respective .txt files (e.g., `passwords.txt`, `credentials.txt`) within the same directory.

## Contributors
Meet the team that made ADIChain possible:

| Contributor Name      | GitHub                                  |
|:----------------------|:----------------------------------------|
| ⭐ **Cirullo Luigi**    | [Click here](https://github.com/luigi9548) |
| ⭐ **Evangelisti Fabrizio**  | [Click here](https://github.com/fabreva) |
| ⭐ **Pagano Elena**  | [Click here](https://github.com/elena1812) |
| ⭐ **Percipalle Noemi**   | [Click here](https://github.com/Noemi1198) |