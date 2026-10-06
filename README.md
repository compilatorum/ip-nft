# IP-NFT × ValueCurator: Verifiable Intellectual Property & Authorization on Solana

> **Colosseum Crypto World's Fair 2026 Hackathon**  
> *Project Submission & Technical Architecture for Tokenized Intellectual Property & Autonomous Agent Authorization.*

---

## 🏛️ Executive Summary

**IP-NFT × ValueCurator** creates an evidence-gated authorization and tokenization infrastructure for intellectual property (patents, scientific datasets, AI models, and bio-algorithms) on Solana.

Instead of issuing speculative tokens or relying on high-friction offshore legal wrappers during the hackathon, the project establishes:
1. **Master IP-NFTs (Metaplex Core)**: Single-account, gas-efficient on-chain containers recording cryptographic SHA-256 digests of legal licenses, datasets, and author credentials.
2. **Deterministic Licensing & Access (Token-2022 Extensions)**: Programmatic transfer hooks and metadata extensions controlling usage rights, data decryption access, and royalty distribution without regulatory securities exposure.
3. **Evidence-Gated Policy Gatekeeper (ValueCurator Engine)**: On-chain PDA program on Solana Devnet preventing autonomous AI agents from accessing or transacting IP assets unless deterministic validation rules (proof of provenance, price impact, oracle verification) are satisfied.

---

## 🔬 Tokenization Analysis: Why Token-2022 + Metaplex Core over MetaDAO STAMP

| Metric / Dimension | MetaDAO STAMP (Futarchy) | Molecule / EVM IP-NFT | Solana Token-2022 + Metaplex Core (Selected) |
| :--- | :--- | :--- | :--- |
| **Legal / Regulatory Friction** | **High**: Requires Cayman foundation, bylaws, and securities compliance | **Medium**: Relies on Swiss law wrappers & sublicensing pacts | **Low**: Structured purely as programmatic utility licenses and verifiable provenance |
| **Execution Feasibility (6 Days)**| **Unviable**: Needs market makers and twin prediction markets | **Risky**: Fractures existing Anchor Devnet codebase | **High**: Native Solana standards directly compatible with Anchor & PDAs |
| **Hackathon Track Alignment** | N/A | Ethereum L1 ($25k prize track) | **Solana Track ($100k prize pool + $250k SF Accelerator)** |
| **Composability** | Confined to futarchy engine | EVM only | Fully composable with Phantom, Squads, Jupiter, and Metaplex |

---

## 📐 Architecture & Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Creator / Researcher                    │
│   (Uploads Research / Dataset / Model -> Generates SHA-256) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Master IP-NFT (Metaplex Core L1)                │
│   • Content Digest: SHA-256 hash of legal agreement + IP    │
│   • Royalties & Governance Plugin                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          Licensing & Fraction Layer (Token-2022)            │
│   • Transfer Hook: Verifies license validity on transfer    │
│   • Metadata Pointer: Dynamic licensing terms               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            ValueCurator Evidence Gatekeeper (Anchor)        │
│   • PDA Vault: Custody of licensing revenues & escrow       │
│   • Policy Engine: AI agents cannot sign unless conditions  │
│     (oracle price freshness, mandate adherence) are met    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

* **Blockchain**: Solana (Devnet & Mainnet-ready)
* **Smart Contracts**: Anchor Framework (Rust), Token-2022 (SPL Extensions), Metaplex Core
* **Evidence & Oracles**: Pyth Pro, Jupiter DEX API, SHA-256 Content Attestation
* **Client & Frontend**: TypeScript, `@solana/web3.js`, `@solana/wallet-adapter-react`, Next.js 15, Tailwind CSS
* **Agent Integration**: `withValueCuratorGuard` middleware for autonomous agents

---

## 📅 6-Day Sprint Roadmap (D-6 → D0)

* **D-6 (Oct 06)**: Finalize tokenization strategy; setup repository; link Colosseum Copilot telemetry.
* **D-5 (Oct 07)**: Metaplex Core Master IP-NFT minting script with SHA-256 legal hash metadata.
* **D-4 (Oct 08)**: Token-2022 licensing extension integration with ValueCurator Devnet PDA vault.
* **D-3 (Oct 09)**: End-to-end interactive UI demonstrating:
  * Mint IP-NFT
  * Request Agent License
  * ValueCurator Guard verifying and approving/blocking on-chain.
* **D-2 (Oct 10)**: Record 3-minute pitch & demo video; test anonymous submission links.
* **D-1 (Oct 11)**: Review Colosseum rubric (Functionality, Novelty, UX, Open-Source); finalize portal text.
* **D-0 (Oct 12)**: Submit project to Colosseum Crypto World's Fair before 18:00 BRT.

---

## 📄 License

Apache License 2.0. Open-source public good for the Solana and DeSci ecosystem.
