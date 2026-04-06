# **Forensic Analysis of the Anthropic Claude Code (v2.1.88) Intellectual Property Exposure and GitHub Propagation Dynamics**

The inadvertent disclosure of the Anthropic Claude Code (v2.1.88) source code on March 31, 2026, represents a transformative event within the domains of artificial intelligence development, open-source compliance, and corporate intellectual property management. This incident, originating from a failure in the release engineering pipeline, resulted in the global dissemination of a comprehensive blueprint for what is widely considered the industry's most advanced agentic coding harness. By accidentally including a 59.8 MB JavaScript source map file within a public distribution on the npm registry, Anthropic provided the developer community with the ability to reconstruct over 512,000 lines of original TypeScript across 1,906 proprietary files. The following report performs a multidimensional analysis of this exposure, the specific systems revealed, and the five most significant GitHub repositories that emerged as centers of propagation and innovation in the wake of the leak.

## **Technical Genesis and the Failure of Release Engineering**

The exposure occurred at approximately 04:00 UTC on March 31, 2026, when Anthropic pushed version 2.1.88 of the @anthropic-ai/claude-code package to the public npm registry.1 While the package itself was minified, it contained a critical debugging artifact: cli.js.map.3 In modern software development, source maps are essential tools that map minified, production-ready code back to its original human-readable source code, including comments, internal logic, and file structures.3 By including this file, Anthropic effectively provided a key that unlocked the entirety of its client-side agentic harness to anyone with access to the npm registry.3

The discovery was first publicized by security researcher Chaofan Shou, whose post on social media platform X accumulated over 28 million views within hours, triggering a viral wave of downloads and mirrors.1 The technical root cause was identified as a multi-layered failure in the build pipeline. Primary among these was the omission of a exclusion rule for .map files in the .npmignore configuration.1 Furthermore, the incident coincided with a known bug in the Bun JavaScript runtime—a toolchain Anthropic had recently acquired—where source maps were occasionally served in production builds despite explicit documentation stating they would be excluded.2 This confluence of human error and toolchain instability resulted in the exposure of an estimated $2.5 billion in annualized recurring revenue (ARR) value, as the leaked code revealed the foundational logic of a tool used by over 100,000 developers.3

| Release Metric | Value / Status |
| :---- | :---- |
| Affected Version | @anthropic-ai/claude-code@2.1.88 |
| Release Timestamp | March 31, 2026, \~04:00 UTC |
| Artifact Type | JavaScript Source Map (.map) |
| Exposed Lines of Code | 512,000+ TypeScript Lines |
| Total Source Files | 1,906 Files |
| Exposed Logic Layers | UI, Commands, Agent Orchestration, Tool Registry |

1

## **Dimensional Analysis of Exposed Proprietary Systems**

The disclosure of the Claude Code source revealed that the application was far more complex than a simple command-line interface wrapper for the Anthropic API. It was, in fact, a full multi-agent production system that had been in active development since mid-2024.3 Several "stealth" features and unreleased modes were identified within the source tree, providing unprecedented insight into Anthropic's long-term product roadmap and defensive strategies.

### **KAIROS and the Persistent Agent Paradigm**

One of the most significant discoveries was the "KAIROS" system, mentioned over 150 times throughout the codebase.1 KAIROS is an unreleased, autonomous background daemon mode designed to transform Claude Code from a reactive tool into a persistent agent.1 This system operates as a background process that watches file system events, logs developer behavior, and performs proactive actions without explicit user invocation.1 The architecture suggests an evolution toward "always-on" AI assistants that maintain context throughout the entire development lifecycle rather than just during active chat sessions.6

### **Memory Consolidation and the Dream System**

The internal logic for memory management was found to be handled by a sophisticated "Dream" system, located in the autoDream process.2 This system implements a form of nightly reflection and memory pruning. While the user is inactive, a forked subagent merges disparate observations from the day's sessions, removes logical contradictions, and converts vague insights into verified facts stored in a long-term index.1 This process addresses the critical LLM challenge of context bloat by employing "Strict Write Discipline," where the agent only updates its memory index after a confirmed successful file operation, preventing the pollution of long-term memory with failed attempts or hallucinations.2

### **Undercover Mode and Anti-Distillation Mechanisms**

The presence of undercover.ts and the ANTI\_DISTILLATION\_CC flag revealed defensive capabilities previously unknown to the public.2 Undercover Mode is a stealth system that activates when Anthropic employees contribute to external or public repositories. It instructs the agent to strip all AI-related metadata, co-author attributions, and mentions of Anthropic from commit messages, effectively masking the use of AI in the development process.6 Simultaneously, the anti-distillation defense is designed to protect Anthropic’s competitive advantage. When triggered, it injects "decoy" tool call definitions into API traffic to poison the data that competitors might collect for model distillation, ensuring that any attempt to train a model on Claude Code's output results in corrupted training sets.1

| System Component | Technical Identifier | Functional Description |
| :---- | :---- | :---- |
| Daemon Mode | KAIROS | Persistent background agent for proactive task execution. |
| Memory Engine | autoDream | Nightly consolidation and pruning of session logs. |
| Stealth System | undercover.ts | Strips AI attribution from public repository commits. |
| Defense Module | ANTI\_DISTILLATION | Injects fake tool definitions to poison competitor training data. |
| Companion Pet | BUDDY | Tamagotchi-style UI element for user engagement. |

1

## **Multidimensional Analysis of Top 5 GitHub Repositories**

The propagation of the Claude Code source across GitHub occurred in waves, with different repositories representing distinct strategies for preservation, modification, or functional expansion. The following five repositories emerged as the most influential or representative artifacts of the incident.

### **1\. instructkr/claw-code (Sigrid Jin)**

The repository originally established as instructkr/claude-code and subsequently renamed to claw-code represents the most significant community response to the leak.6 Managed by Korean developer Sigrid Jin, this repository achieved 50,000 stars within two hours of creation and eventually exceeded 105,000 stars, making it one of the fastest-growing projects in GitHub's history.10

The distinguishing feature of this repository is its transition from a direct mirror to a "clean-room" rewrite.9 Following the initial backup of the TypeScript source, Jin utilized OpenAI Codex and Grok to translate the entire architectural logic of the agent harness into Python and Rust.10 This strategy, described as "shedding the golden cicada's shell," was intended to create a version of the tool that was functionally identical to Claude Code but legally distinct.10 By ensuring that "not a single line of original source code" remained, the creators aimed to bypass Anthropic's DMCA takedown claims, arguing that the resulting project was a new expression of the underlying ideas and algorithms.10

* **Objective**: To provide a legally resilient, open-source version of the Claude Code agent harness through automated cross-language translation.9  
* **Metric Dynamics**: 105,000+ stars, 95,000+ forks, and 5,000 Discord members joined within 24 hours.11  
* **Competitive Intelligence**: The project received Grok credits from xAI to assist in the porting process, highlighting how competitors utilized the leak to fuel their own development efforts.10

### **2\. Kuberwastaken/claurst (or Kuberwastaken/claude-code)**

The claurst repository is notable for its rigorous "behavioral specification" approach to reimplementation.15 Unlike direct mirrors, this project followed a two-phase process: an AI agent was first tasked with producing behavioral specifications, architectural designs, and tool contracts based on the leaked logic.15 Subsequently, a separate AI agent implemented those specifications in idiomatic Rust without referencing the original TypeScript source.15

This repository focuses on performance optimization and the removal of tracking mechanisms.15 It achieved 100% feature parity with the original source, including the implementation of the BUDDY companion system and the ULTRAPLAN mode.15 The project is representative of the "clean-room" methodology used to transform leaked proprietary information into usable open-source software while attempting to minimize copyright infringement risks.6

* **Objective**: High-performance Rust reimplementation of the Claude Code behavior with zero telemetry and unlocked experimental features.15  
* **Technical Content**: Includes full specifications for the "Dream" system and the "Ultraplan" multi-agent planning mode.15  
* **Metric Dynamics**: 8,400 stars and 7,600 forks.15

### **3\. antonoly/claude-code-anymodel**

The antonoly/claude-code-anymodel repository represents the functional evolution of the leak into a model-agnostic tool.16 While the original Claude Code was strictly locked to Anthropic’s API, this project integrates a local proxy system—including ollama-proxy.mjs and openrouter-proxy.mjs—allowing the client to work with over 200 different AI models.16

The codebase retains the sophisticated UI and terminal rendering logic of the original tool but modifies the QueryEngine.ts and bridge/ logic to support OpenAI-compatible endpoints.16 This repository is a key indicator of the community's desire to use Anthropic's industry-leading "agentic harness" with local or open-source models like Qwen or DeepSeek.16

* **Objective**: To decouple the Claude Code UI and orchestration logic from the Anthropic provider.16  
* **Engagement**: 68 stars, 105 forks, and 11 commits from lead author Anton Abyzov.16  
* **Architecture**: Modular structure including assistant/, coordinator/, and upstreamproxy/ directories.16

### **4\. claw-cli/claw-code-rust**

This repository, managed by the claw-cli organization, represents a systematic attempt to decompose Claude Code’s logic into a collection of reusable Rust crates.17 The project addresses the problem of the original codebase being "deeply intertwined," making it difficult to reuse specific components like the permission system or the message loop.17

The architecture is divided into specialized crates: claw-core (session state), claw-tools (execution orchestration), claw-permissions (authorization layer), and claw-compact (context trimming).17 This project treats the leak not as a final product to be mirrored, but as a technical blueprint for the next generation of modular agentic tools.17

* **Objective**: To rebuild a modular, clean-room version of the Claude Code runtime in Rust for use in other projects.17  
* **Status**: Active development with 45 commits and 3 primary contributors.17  
* **Architecture Hierarchy**: Three-layer design consisting of a thin CLI, a middle core runtime, and concrete implementation crates.17

### **5\. hangsman/claude-code-source**

The hangsman/claude-code-source repository was one of the first and most representative direct archival efforts of the incident.18 Unlike the rewrites or extensions, this repository sought to preserve the v2.1.88 source code exactly as it was leaked, providing a reference point for researchers studying real-world AI agent systems.18

It contains the complete TypeScript source tree, including the original package.json, bun.lock file, and the cli.js.map artifact that enabled the exposure.16 This repository served as the primary source for the technical analysis performed by security researchers in the first 48 hours of the event.18 Because it contained unmodified proprietary code, it was a central target of Anthropic's initial DMCA blitz.14

* **Objective**: Archival snapshot of the proprietary source for research and reference.18  
* **Metrics**: 731 stars and 1.7k forks.18  
* **Content**: Full repository including the buddy/ pet system and the unreleased tools/permissions/ security logic.7

## **Comparative Analysis of Repository Metrics and Strategy**

| Repository Identifier | Strategy Type | Engagement (Stars/Forks) | Primary Language | Legal Defense |
| :---- | :---- | :---- | :---- | :---- |
| instructkr/claw-code | Clean-Room Rewrite | 105k / 95k | Python | Functional Re-expression |
| Kuberwastaken/claurst | Behavioral Spec | 8.4k / 7.6k | Rust | Specification Independence |
| hangsman/claude-code-source | Direct Archival | 0.7k / 1.7k | TypeScript | Research / Mirroring |
| claw-cli/claw-code-rust | Modular Crates | 0.2k / 0.1k | Rust | Architectural Extraction |
| antonoly/claude-code-anymodel | Functional Extension | 0.1k / 0.1k | TypeScript | Decoupling / Interop |

11

## **Compliance and Legal Implications for Open Source Researchers**

The propagation of Claude Code across GitHub triggered a complex series of legal maneuvers and raised fundamental questions regarding the copyrightability of AI-generated software.

### **DMCA Enforcement and Overreach**

Anthropic's legal response was swift but broadly criticized for its lack of precision. The company issued DMCA takedown notices that initially removed approximately 8,100 repositories.14 This automated enforcement mechanism inadvertently targeted legitimate forks of Anthropic's own publicly released Claude Code repository—which contained only installation scripts and community resources—rather than just the leaked proprietary source.20 Following public backlash and acknowledgment of the error by Boris Cherny, Anthropic retracted the majority of these notices, eventually limiting enforcement to roughly 97 repositories that directly contained the leaked intellectual property.20

### **The Copyright Paradox of AI-Generated Code**

A central theme in the community's defense against takedowns was the origin of the code itself. Boris Cherny, the head of Claude Code, had publicly stated weeks prior to the leak that "100% of my contributions to Claude Code... were written by Claude Code itself".22 This admission placed the codebase within a legal grey area defined by the *Thaler v. Perlmutter* precedent, which suggests that work generated entirely by an AI system without human creative control is not eligible for copyright protection.22

Developers of clean-room rewrites like Sigrid Jin argued that if the original code lacked copyright due to its AI origin, then Anthropic's DMCA claims were potentially fraudulent.22 Furthermore, Section 512(f) of the DMCA makes false copyright claims punishable as perjury, creating a theoretical legal risk for Anthropic if it attempted to assert ownership over code it knew was generated by its own model.22 While this defense has not been tested in a final court ruling, it provided the rhetorical and legal foundation for the rapid proliferation of rewritten versions that remain active on GitHub today.10

## **Security Risks and the "Leaked Code" Malware Trap**

The curiosity surrounding the leak was weaponized by threat actors almost immediately. Researchers at Zscaler ThreatLabz identified several GitHub repositories disguised as mirrors of the Claude Code source that actually functioned as distribution points for malware.23 These repositories often featured a README claiming to offer "unlocked enterprise features" or "API key bypasses".24

The primary vector was a Rust-based dropper named ClaudeCode\_x64.exe bundled in a .7z archive.24 Upon execution, this dropper installed the Vidar infostealer and GhostSocks.23 This campaign targeted thousands of developers who were attempting to inspect the internal logic of the agent, highlighting the risks inherent in the unauthorized distribution of proprietary code.24

## **Strategic Findings from the Exposed Architectural Blueprint**

The 512,000 lines of exposed TypeScript provided a detailed look at the internal security and operational model of a high-tier agentic system.

### **The "Fucks" Chart and User Sentiment Tracking**

A notable find within the telemetry systems was a profanity-tracking dashboard, internally referred to by the team as the "fucks" chart.8 This system uses regex-based scanning of user inputs to detect developer frustration.8 The presence of this chart indicates that Anthropic uses emotional friction as a primary signal for assessing model performance, prioritizing user sentiment over technical accuracy in its product iteration cycle.8

### **Model Context Protocol (MCP) and Tool Sandboxing**

The source code confirmed that Claude Code’s architecture mirrors the primitives standardized in the Model Context Protocol (MCP).26 Every tool call within the agent harness is discretely permission-gated and schema-defined.26 The leak revealed a sophisticated classifyYoloAction() function, which is responsible for the auto-permissioning system.6 Interestingly, while the tool system is designed with safety in mind, the leaked binary contained environment variables—such as CLAUDE\_CODE\_ABLATION\_BASELINE and DISABLE\_COMMAND\_INJECTION\_CHECK—that allow internal users to bypass all safety features and injection checks.6

### **Pricing and Competitive Intelligence**

The leak also disclosed previously secret billing details relevant to enterprise competitors. For instance, the "Opus 4.6 Fast Mode" is hardcoded to cost $30 per million input tokens, representing a 6x markup over normal mode for the same model weights, purely for priority inference.6 Additionally, the source revealed a flat $0.01 cost per web search query, a detail that was previously undisclosed to the public.6 This data provides competitors like Cursor and GitHub Copilot with a precise benchmark for the operational costs and margin structures of Anthropic’s first-party tools.8

## **Conclusion**

The Anthropic Claude Code source code disclosure of March 2026 represents a critical failure of internal release controls with permanent consequences for the AI industry. The event demonstrated that even companies at the forefront of AI safety and security are vulnerable to basic packaging oversights. The multidimensional response on GitHub—characterized by archival efforts, behavioral reimplementations, and clean-room rewrites—suggests that once an agentic harness of this complexity is leaked, it is impossible to fully retract.

For open-source compliance researchers, the incident highlights a growing shift in the legal landscape: as AI models become the primary authors of their own software, traditional copyright protections are being challenged by new "AI-first" development workflows. The success of Sigrid Jin’s claw-code and similar projects indicates that the "clean-room" methodology, combined with AI-assisted translation, has become a potent tool for bypassing the DMCA in the age of generative models. Ultimately, the blueprint for Claude Code is now part of the global technical commons, likely accelerating the development of decentralized, model-agnostic coding agents and shifting the competitive advantage from the agentic harness to the underlying model weights and proprietary data used for reinforcement learning.

#### **Works cited**

1. Anthropic Leaked Claude Code's Entire Source — Here's What 512K Lines of TypeScript Reveal | danilchenko.dev, accessed April 6, 2026, [https://danilchenko.dev/posts/2026-04-01-claude-code-source-code-leak-kairos-npm/](https://danilchenko.dev/posts/2026-04-01-claude-code-source-code-leak-kairos-npm/)  
2. The Great Claude Code Leak of 2026: Accident, Incompetence, or the Best PR Stunt in AI History? \- DEV Community, accessed April 6, 2026, [https://dev.to/varshithvhegde/the-great-claude-code-leak-of-2026-accident-incompetence-or-the-best-pr-stunt-in-ai-history-3igm](https://dev.to/varshithvhegde/the-great-claude-code-leak-of-2026-accident-incompetence-or-the-best-pr-stunt-in-ai-history-3igm)  
3. Claude Code Leak. On March 30, 2026, Anthropic published… | by Onix React \- Medium, accessed April 6, 2026, [https://medium.com/@onix\_react/claude-code-leak-d5871542e6e8](https://medium.com/@onix_react/claude-code-leak-d5871542e6e8)  
4. Anthropic's AI coding tool, Claude Code, accidentally reveals its source code; here's what happened, accessed April 6, 2026, [https://www.livemint.com/technology/tech-news/anthropics-ai-coding-tool-claude-code-accidentally-reveals-its-source-code-heres-what-happened-11774977255558.html](https://www.livemint.com/technology/tech-news/anthropics-ai-coding-tool-claude-code-accidentally-reveals-its-source-code-heres-what-happened-11774977255558.html)  
5. Claude Code Source Map Leak, What Was Exposed and What It Means \- Penligent, accessed April 6, 2026, [https://www.penligent.ai/hackinglabs/claude-code-source-map-leak-what-was-exposed-and-what-it-means/](https://www.penligent.ai/hackinglabs/claude-code-source-map-leak-what-was-exposed-and-what-it-means/)  
6. Anthropic Accidentally Leaks Claude Code's Entire Source Code via npm \- FAUN.dev(), accessed April 6, 2026, [https://faun.dev/co/news/kala/anthropic-accidentally-leaks-claude-codes-entire-source-code-via-npm/](https://faun.dev/co/news/kala/anthropic-accidentally-leaks-claude-codes-entire-source-code-via-npm/)  
7. GitHub \- Ringmast4r/claw-cli-claude-code-source-code-v2.1.88, accessed April 6, 2026, [https://github.com/ringmast4r/claw-cli-claude-code-source-code-v2.1.88](https://github.com/ringmast4r/claw-cli-claude-code-source-code-v2.1.88)  
8. Anthropic Leak Claude Code: 512,000 Lines Exposed by One Bug \- Ruh AI Blog, accessed April 6, 2026, [https://www.ruh.ai/blogs/anthropic-claude-code-leak-2026-npm-source-exposure](https://www.ruh.ai/blogs/anthropic-claude-code-leak-2026-npm-source-exposure)  
9. What Is Claw Code? The Claude Code Rewrite Explained | WaveSpeedAI Blog, accessed April 6, 2026, [https://wavespeed.ai/blog/posts/what-is-claw-code/](https://wavespeed.ai/blog/posts/what-is-claw-code/)  
10. Python Version of Claude Code After Major Overhaul Could Reach 100000 Stars on GitHub Fastest. Clone Now\! \- 36氪, accessed April 6, 2026, [https://eu.36kr.com/en/p/3749018747699717](https://eu.36kr.com/en/p/3749018747699717)  
11. A 4 am scramble turned Anthropic's leak into a 'workflow revelation', accessed April 6, 2026, [https://graphopedagogie972.fr/news/89969](https://graphopedagogie972.fr/news/89969)  
12. A 4 am scramble turned Anthropic's leak into a 'workflow revelation', accessed April 6, 2026, [https://valentinagirardello.it/topic/trade](https://valentinagirardello.it/topic/trade)  
13. Claude Code の流出したソースコードを GitHub に公開した人が著作権違反を回避した方法がヤバすぎ \#AI \- Qiita, accessed April 6, 2026, [https://qiita.com/LostMyCode/items/a867e1954b80e78cf146](https://qiita.com/LostMyCode/items/a867e1954b80e78cf146)  
14. How an engineer ensured Claude Code source code leak stays on GitHub despite Anthropic's takedown notice, accessed April 6, 2026, [https://timesofindia.indiatimes.com/technology/tech-news/how-an-engineer-ensured-claude-code-source-code-leak-stays-on-github-despite-anthropics-takedown-notice/articleshow/129978276.cms](https://timesofindia.indiatimes.com/technology/tech-news/how-an-engineer-ensured-claude-code-source-code-leak-stays-on-github-despite-anthropics-takedown-notice/articleshow/129978276.cms)  
15. Kuberwastaken/claurst: Your favorite Terminal Coding ... \- GitHub, accessed April 6, 2026, [https://github.com/Kuberwastaken/claude-code](https://github.com/Kuberwastaken/claude-code)  
16. antonoly/claude-code-anymodel: Use Claude Code with ... \- GitHub, accessed April 6, 2026, [https://github.com/antonoly/claude-code](https://github.com/antonoly/claude-code)  
17. claw-cli/claw-code-rust: Build better harness tooling—not ... \- GitHub, accessed April 6, 2026, [https://github.com/claw-cli/claw-code-rust](https://github.com/claw-cli/claw-code-rust)  
18. hangsman/claude-code-source \- GitHub, accessed April 6, 2026, [https://github.com/hangsman/claude-code-source](https://github.com/hangsman/claude-code-source)  
19. Anthropic accidentally exposes Claude Code source code \- The Register, accessed April 6, 2026, [https://www.theregister.com/2026/03/31/anthropic\_claude\_code\_source\_code/](https://www.theregister.com/2026/03/31/anthropic_claude_code_source_code/)  
20. Anthropic GitHub Takedown Chaos: Accidental Removal of 8,100 Repositories Sparks Developer Fury | Bitcoinworld on Binance Square, accessed April 6, 2026, [https://www.binance.com/en/square/post/308004387543586](https://www.binance.com/en/square/post/308004387543586)  
21. Anthropic GitHub Takedown Chaos: Accidental Removal of 8,100 Repositories Sparks Developer Fury \- CryptoRank, accessed April 6, 2026, [https://cryptorank.io/news/feed/7f7e2-anthropic-github-takedown-accident-repositories](https://cryptorank.io/news/feed/7f7e2-anthropic-github-takedown-accident-repositories)  
22. When AI-Written Code Gets Rewritten by AI: The Copyright Vacuum Exposed by the Claude Code Leak, accessed April 6, 2026, [https://yage.ai/share/claude-code-copyright-paradox-en-20260402.html](https://yage.ai/share/claude-code-copyright-paradox-en-20260402.html)  
23. Anthropic Claude Code Leak | ThreatLabz \- Zscaler, Inc., accessed April 6, 2026, [https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak](https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak)  
24. Claude Code leak leveraged to distribute malware | brief \- SC Magazine, accessed April 6, 2026, [https://www.scworld.com/brief/claude-code-leak-used-to-distribute-malware](https://www.scworld.com/brief/claude-code-leak-used-to-distribute-malware)  
25. Anthropic's Boris Cherny who made Doomsday prediction for engineers wants more automation as Anthropic blames 'human error' for Claude Code leak; says: Should have, accessed April 6, 2026, [https://timesofindia.indiatimes.com/technology/tech-news/anthropics-boris-cherny-who-made-doomsday-prediction-for-engineers-wants-more-automation-as-anthropic-blames-human-error-for-claude-code-leak-says-should-have-/articleshow/130007853.cms](https://timesofindia.indiatimes.com/technology/tech-news/anthropics-boris-cherny-who-made-doomsday-prediction-for-engineers-wants-more-automation-as-anthropic-blames-human-error-for-claude-code-leak-says-should-have-/articleshow/130007853.cms)  
26. Claude Code's Source Leak: What 512K Lines of Code Reveal About MCP \- Palma AI, accessed April 6, 2026, [https://palma.ai/blog/claude-code-source-leak-what-it-means-for-mcp](https://palma.ai/blog/claude-code-source-leak-what-it-means-for-mcp)