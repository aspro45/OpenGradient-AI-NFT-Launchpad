# OpenGradient AI NFT Launchpad Documentation

## Overview
The OpenGradient AI NFT Launchpad is an intelligent platform that lets you buy, create, or sell NFTs through simple chat conversations. Powered by an AI assistant, it handles the complex parts of blockchain technology for you. You type what you want to do, and the AI manages price checks, payment verifications, and new collection creations directly on the blockchain.

## The Problem It Solves
Traditional NFT platforms are often complicated for everyday users. They require you to figure out the right digital wallet, manually copy long contract addresses, calculate exact Ethereum amounts, and hope you avoid costly mistakes. This project replaces that stressful process with a simple conversation.

## Core Features

### 1. Mint an NFT
Tell the AI you want to mint an NFT. The AI will tell you the exact amount of ETH needed and the payment address. After you make the payment and provide the transaction ID, the AI verifies it on the blockchain and sends the NFT directly to your wallet.

### 2. Deploy Your Own Collection
Tell the AI you want to launch a new NFT collection. Provide the collection name, symbol, supply, price, and a short description. After paying a small 0.01 ETH deployment fee, the AI verifies the payment and deploys a real smart contract on the blockchain.

### 3. Browse Collections
Ask the AI questions about the platform. You can find out what collections are available on the launchpad, check minting prices, or ask if a specific collection is free to mint.

## How It Works
The AI agent acts as a very smart, 24/7 NFT shop assistant.
* **Listens:** You type your request in the chat.
* **Thinks:** The AI figures out the necessary action on OpenGradient's secure network.
* **Checks:** It looks up collections, verifies your payment transaction, or deploys a contract automatically.
* **Replies:** The AI explains the results to you in plain, real-time language.

## The Technology Behind It

| User Experience | Backend Action |
| :--- | :--- |
| The chat box | A website streams the AI's reply live, word by word. |
| The AI thinking | GPT-4o processes the request inside OpenGradient's secure network. |
| Processing payment message | A Python script reads the Base Sepolia blockchain to verify the transaction. |
| Minting success message | A real smart contract function is called to create a token on-chain. |
| Receiving a contract address | A brand new ERC-721 smart contract is compiled and deployed to the blockchain. |

## What Makes OpenGradient Special?
* **Self-Paying AI:** Unlike standard AI apps that use a password-like API key, this AI agent has its own crypto wallet. Every time it thinks, it pays a tiny fee directly on-chain using the x402 micropayment protocol. There are no middlemen or monthly subscriptions.
* **Secure Environment:** The AI runs inside a Trusted Execution Environment (TEE). This secure chip guarantees that no one, not even the server hosts, can tamper with the AI's thinking process.
* **Continuous Memory:** The AI remembers your entire conversation. If you discuss minting an NFT and later confirm your payment, it knows exactly what you mean without you having to repeat yourself.

## Example: Deploying a Collection
**User:** I want to launch my own NFT collection called MoonCats.
**AI:** Great! I need a few details: Ticker symbol, Mint price, Total supply, and a short description.
**User:** MOON, free mint, 500 NFTs, cute mooncat PFPs.
**AI:** Perfect! To deploy, please send 0.01 ETH to [Payment Address]. Then share the transaction ID with me.
**User:** Here's my tx: 0xabc123...
**AI:** ✅ Payment confirmed! 🚀 MoonCats (MOON) is now live on Base Sepolia! Contract address: [Real Address]. View on BaseScan: [BaseScan Link].

## Project Credits

| Role | Details |
| :--- | :--- |
| Developer | @ASPRO_22 |
| AI Network | OpenGradient |
| Blockchain | Base Sepolia (Ethereum L2) |
| AI Model | GPT-4o via OpenGradient TEE |
| Hosting | Vercel |
