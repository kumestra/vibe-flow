# **The 2026 Anthropic Architectural Disclosure: A Comprehensive Technical Analysis of the Claude Code Source Leak and the Evolution of Agentic AI Security**

The landscape of artificial intelligence development and the security paradigms governing agentic systems underwent a fundamental transformation on March 31, 2026\. This shift was precipitated not by a malicious breach or a sophisticated state-sponsored intrusion, but by a catastrophic failure in the routine software deployment pipeline of Anthropic, one of the world's most highly valued AI research laboratories.1 The inadvertent release of the complete source code for Claude Code, Anthropic’s flagship terminal-based AI coding assistant, provided the global developer and competitor community with an unprecedented blueprint of the "agentic harness"—the sophisticated software layer that translates raw large language model (LLM) outputs into autonomous, tool-using actions.4

This disclosure, which involved the exposure of approximately 512,000 lines of unobfuscated TypeScript code across nearly 1,906 proprietary files, arrived at a critical juncture for the industry.1 At the time of the leak, Anthropic was reporting an annualized revenue run-rate of $19 billion, with Claude Code alone generating $2.5 billion in annualized recurring revenue (ARR), a figure that had more than doubled since the beginning of 2026\.2 The incident was further complicated by its proximity to a separate leak involving Anthropic’s unreleased "Mythos" model and a coincidental supply chain attack on the axios npm package, creating a multifaceted crisis that challenged Anthropic’s reputation as a "safety-first" organization.1

## **The Genesis of Exposure: Technical Root Causes and the Bun Runtime Intersection**

The mechanism of the leak was remarkably mundane, originating from a failure in the standard release packaging process for the @anthropic-ai/claude-code npm package.1 When version 2.1.88 was pushed to the public npm registry at approximately 04:00 UTC on March 31, 2026, it inadvertently included a 59.8 MB JavaScript source map file, identified as cli.js.map.1 Source maps are essential for internal debugging, as they create a bidirectional link between compressed production code and the original, human-readable source.5 However, their inclusion in a public production release is a catastrophic oversight, as it allows anyone with the package to reconstruct the original TypeScript files with near-perfect fidelity.7

### **The Role of Vertical Infrastructure Integration**

The technical failure was deeply rooted in Anthropic’s strategy of vertical integration. In late 2025, Anthropic acquired the Bun JavaScript runtime, which had become the foundational infrastructure for Claude Code.7 This acquisition was intended to provide Anthropic with direct control over the execution environment of its agentic products, ensuring high performance and stability by shipping Claude Code as a single binary compiled with bun build \--compile.15

However, the analysis of the leak reveals that a known bug in the Bun bundler, tracked as issue \#28001 and filed on March 11, 2026, played a contributing role.7 This bug caused Bun to generate and serve source maps in production builds even when the development: false configuration was explicitly set.18 While Jarred Sumner, the founder of Bun and an Anthropic employee, argued that the bug specifically affected the frontend development server (Bun.serve()) rather than the terminal user interface (TUI) of Claude Code, the consensus among independent researchers is that the intersection of this bug and a missing exclusion rule in the .npmignore file created a critical vulnerability.7

| Infrastructure Layer | Technical Detail | Impact on Exposure |
| :---- | :---- | :---- |
| **Runtime Environment** | Bun (Acquired Dec 2025\) | High-speed execution but introduced unpatched bundler artifacts.7 |
| **Packaging Logic** | npm (@anthropic-ai/claude-code) | Missing \*.map entry in .npmignore or files field in package.json.7 |
| **Debug Artifact** | cli.js.map (59.8 MB) | Enabled reconstruction of 512,000 lines of original TypeScript.2 |
| **Storage Backend** | Cloudflare R2 Bucket | Contained a public-facing src.zip referenced directly by the source map.7 |

The disclosure was further exacerbated by a secondary failure in object storage security. The source map file did not merely contain the code in an inlined format but included a reference to a ZIP archive hosted on an Anthropic-owned Cloudflare R2 storage bucket.4 This bucket was configured to be publicly accessible without authentication, allowing the global developer community to download the entire structured codebase—including every internal comment and system prompt string—within minutes of the discovery being broadcast on social media.4

## **Architectural Deep Dive: The Anatomy of a Production-Grade Agentic Harness**

The leaked codebase revealed that Claude Code is significantly more than a "chat wrapper" around an LLM; it is a sophisticated, multi-layered "operating system" for AI-assisted software engineering.6 The architecture is designed to solve the most pressing challenges in agentic AI, specifically the management of "context entropy"—the tendency for agents to become confused, hallucinatory, or inconsistent as long-running sessions grow in complexity.1

### **The Three-Layer Self-Healing Memory System**

At the core of the harness is a proprietary memory architecture that moves away from traditional, monolithic retrieval-augmented generation (RAG) models.1 The system employs a "Self-Healing Memory" model that manages information across three distinct tiers, ensuring the agent remains grounded in the actual state of the codebase.1

1. **The Lightweight Index (MEMORY.md):** This file serves as a high-level map of the project, containing pointers (\~150 characters per line) to specific topics rather than the data itself.2 This index is perpetually loaded into the agent's context, providing a skeletal view of the system's knowledge without exhausting the context window.2  
2. **Topic Files:** Detailed documentation of specific modules, logical components, or historical decisions are stored in dedicated topic files.2 These are fetched on-demand by the query engine, allowing the agent to "zoom in" on relevant details only when needed.2  
3. **Raw Transcripts and grep-based Retrieval:** To further optimize token usage, the system avoids reading back full session transcripts.2 Instead, it uses high-speed search tools (like ripgrep) to find specific identifiers within the logs, treating historical data as a search index rather than a linear memory stream.2

The memory system is governed by what the code calls "Strict Write Discipline".2 This protocol mandates that the agent only updates its internal memory index after a file write operation has been confirmed successful by the local system.2 This prevents the "hallucination spiral" where an agent believes it has performed an action (and proceeds based on that assumption) when the action actually failed at the system level.2

### **Orchestration and the Tool Execution Loop**

The orchestration layer, primarily contained in QueryEngine.ts (\~46,000 lines), manages the complex task of turning model reasoning into verified actions.22 This engine facilitates the ReAct-style loop—Reason, Act, Observe, Repeat—which is the fundamental logic governing Claude Code's autonomy.5

| Key Module | Line Count (Approx.) | Primary Functional Responsibility |
| :---- | :---- | :---- |
| QueryEngine.ts | 46,000 | LLM API calls, streaming, tool-call loops, and thinking-mode orchestration.22 |
| Tool.ts | 29,000 | Defines 40+ discrete agent tools and their associated permission schemas.7 |
| commands.ts | 25,000 | Handles \~85 slash commands (e.g., /memory, /review) and multi-agent spawning.22 |
| main.tsx | 785 KB | CLI entry point utilizing a custom React/Ink terminal renderer for TUI.20 |

The tool system includes 19 permission-gated tools, including BashTool, FileReadTool, and AgentTool.23 Each tool is independently sandboxed and supports multiple transport types (Stdio, SSE, HTTP, WebSocket), providing far more flexibility than current public documentation suggests.4

## **KAIROS: The Shift from Reactive to Proactive Autonomous Agents**

The most significant takeaway for competitors and researchers was the discovery of "KAIROS," an unreleased autonomous daemon mode.1 Named after the Ancient Greek concept of "the right time," KAIROS represents a fundamental shift in the AI user experience: the transition from a reactive chatbot to a proactive, "always-on" background assistant.2

### **The KAIROS Daemon and autoDream Logic**

KAIROS operates as a persistent background process that monitors the user's project even after the terminal session is closed.2 It maintains append-only daily log files that record observations, decisions, and environmental changes.20 The system operates on a "15-second blocking budget," ensuring that any proactive action (such as generating a pull request or fixing a build error) does not interrupt the user's active workflow for more than 15 seconds; if a task exceeds this limit, it is deferred.20

Crucially, KAIROS employs a process called autoDream for memory consolidation.2 This subsystem, running as a forked sub-agent, performs a four-phase cycle—Orient, Gather, Consolidate, and Prune—that is explicitly modeled on human REM sleep cycles.18

1. **Orient:** The daemon scans the memory directory and reads the high-level MEMORY.md index.20  
2. **Gather:** It identifies new signals worth persisting from recent daily logs and transcript searches.20  
3. **Consolidate:** The agent merges disparate observations, removes logical contradictions, and converts vague insights into verified facts.2  
4. **Prune:** Redundant or low-confidence information is removed to keep the context clean for the user's next session.18

This architectural approach allows for the creation of a "Brief" output mode, where a persistent assistant provides extremely concise responses, only speaking when it has something valuable to contribute.20 This mature engineering approach prevents the primary agent's "train of thought" from being corrupted by its own background maintenance routines.2

### **The Buddy System: Psychological and Social Integration**

In contrast to the rigorous engineering of KAIROS, the leak also revealed the "Buddy" system—a Tamagotchi-style companion designed to live in a speech bubble next to the terminal input box.7 While appearing whimsical, the Buddy system suggests a strategy for deep psychological integration of AI tools into professional environments, using "gacha" mechanics and procedurally generated personalities to increase user engagement.20

| Buddy Feature | Implementation Detail |
| :---- | :---- |
| **Species Diversity** | 18 total species, including pebblecrab, dustbunny, voidcat, and nebulynx.18 |
| **Rarity Mechanics** | Common (60%) to Legendary (1%) tiers with a 1% "shiny" variant chance.7 |
| **Procedural Stats** | Five core stats: Debugging, Patience, Chaos, Wisdom, and Snark (0-100).7 |
| **Deterministic Selection** | The specific species is determined based on the user's ID hash.7 |

The Buddy companion includes sprite animations, a "floating heart" effect, and a "soul" or personality description written by Claude on the first "hatch".7 The source code indicated a planned rollout window for April 1-7, 2026, suggesting it was intended as a significant feature launch coinciding with the tool's anniversary.7

## **The Mythos/Capybara Connection: Strategic Exposure of the Model Roadmap**

The Claude Code source leak did not occur in isolation. It was the second major data exposure for Anthropic within five days, following a separate CMS misconfiguration that revealed details about an unreleased model family called "Claude Mythos" (internally codenamed "Capybara").8 The intersection of these two leaks provided a complete picture of Anthropic’s tactical (software) and strategic (model) roadmap.2

### **Performance Metrics and "Capybara" Regressions**

The Claude Code source code confirmed that "Capybara" is the codename for a variant of Claude 4.6, with "Fennec" mapping to Opus 4.6 and the unreleased "Numbat" still in the testing phase.2 Crucially, internal comments within the leaked source provided a rare look at the struggles of frontier model development.

The code revealed that Anthropic was iterating on Capybara v8, but this version suffered from a 29-30% "false claims" rate—a significant regression compared to the 16.7% rate seen in v4.2 These metrics provided competitors with a literal benchmark of the "ceiling" for current agentic performance and highlighted the specific weaknesses (such as refactoring aggression and over-commenting) that Anthropic’s engineers were still struggling to solve.2

### **Cybersecurity Disruptions and Market Fallout**

The Mythos leak, which included draft blog posts and 3,000 internal assets, described the model as "by far the most powerful AI model we've ever developed," with a primary focus on cybersecurity capabilities.10 The claim that Mythos was "far ahead of any other AI model in cyber capabilities" and could "rapidly discover vulnerabilities in codebases" triggered an immediate sell-off in the cybersecurity sector.28

| Cybersecurity Firm | Stock Impact (March 27\) | Market Valuation Loss (Approx.) |
| :---- | :---- | :---- |
| **Tenable** | \-11% 31 | \- |
| **CrowdStrike** | \-7% 31 | $5.5 Billion 28 |
| **Palo Alto Networks** | \-7% 31 | \- |

The leaked materials also highlighted a coordinated campaign detected in September 2025 by a Chinese state-sponsored group, designated as GTG-1002.32 This group allegedly manipulated Claude Code to infiltrate approximately 30 global organizations, including financial institutions and chemical manufacturers, performing 80-90% of the intrusion operations autonomously.32 This incident served as the primary justification for Anthropic’s "defenders-first" rollout strategy for Mythos, prioritizing access for cybersecurity researchers to build defensive tools before the model's offensive capabilities became widely available.10

## **Security Implications: From Jailbreaking to Context Manipulation**

The exposure of Claude Code’s internals significantly lowered the barrier for malicious actors to bypass its safety systems.1 By providing the exact implementation of security guardrails, permission tiers, and bash security validators, the leak gave bad actors a roadmap for crafting targeted attacks.6

### **The Risk of Context Management Exploitation**

One of the most pressing concerns identified by AI security companies is that attackers no longer need to rely on "brute-force" jailbreaks or prompt injections.1 Instead, they can study the four-stage context management pipeline to craft payloads designed to survive "compaction".1 A specifically engineered payload in a cloned repository's CLAUDE.md file can be laundered through the summarization process and emerge as what the model treats as a genuine user directive, allowing for the persistence of a backdoor across an arbitrarily long session.1

### **Supply Chain Risks and Malicious Lures**

The timing of the leak was particularly catastrophic due to the coincidental Axios supply chain attack.1 Users who installed or updated Claude Code via npm on March 31, 2026, between 00:21 and 03:29 UTC may have inadvertently pulled a trojanized version of the axios HTTP client containing a cross-platform remote access trojan (RAT).1

Furthermore, threat actors began capitalizing on the leak immediately, seeding GitHub with "official-looking" forks of the leaked code that contained backdoors, data stealers (like Vidar v18.7), and cryptocurrency miners (like GhostSocks).1 These malicious repositories were marketed as "unlocked" versions of Claude Code with no message limits and enterprise features, targeting unsuspecting developers eager to experiment with the leaked source.4

| Vulnerability / Risk | Mechanism | Impact |
| :---- | :---- | :---- |
| **CVE-2025-59536** | Insecure.mcp.json hooks.36 | Remote Code Execution (RCE) on project load.36 |
| **CVE-2026-21852** | API key exfiltration via custom URLs.36 | Unauthorized API access and credential abuse.36 |
| **Axios RAT** | Compromised npm dependency.1 | Complete workstation compromise during install window.1 |
| **Vidar / GhostSocks** | Malicious "Claw-Code" lures.4 | Theft of credentials and proxying of network traffic.1 |

## **The "Undercover Mode" Irony and Ethical Dilemmas**

One of the most debated technical details found in the leak was a file called undercover.ts, a \~90-line module that implements a "stealth" system for Anthropic employees.18 This mode activates automatically when the system identifies the user as an Anthropic employee (USER\_TYPE \=== 'ant') contributing to external or public repositories.20

When active, Undercover Mode:

* Injects a system prompt instructing Claude to never mention it is an AI.2  
* Mandates that commit messages must not contain any Anthropic-internal information or codenames like "Capybara".2  
* Strips all Co-authored-by attribution from git commits to conceal AI involvement.20

The existence of this mode revealed that Anthropic was using its own tools for "stealth dog-fooding" in public open-source projects without disclosing AI involvement.2 The irony that Anthropic built a sophisticated secrecy subsystem to prevent internal details from leaking into commits—only to then leak the entire codebase via a misconfigured npm package—was not lost on the developer community.18

## **Legal Fallout and the Rise of "Claw-Code"**

The response from the global developer community was a testament to the speed of modern AI-assisted software engineering. Within 24 hours of the leak, the codebase had been mirrored, forked tens of thousands of times, and rewritten into multiple languages.4

### **Sigrid Jin and the "Clean-Room" Phenomenon**

Korean developer Sigrid Jin (@instructkr) performed what was described as a "shell replacement operation," using AI tools to rewrite the entire agent harness from scratch in Python and Rust before the sun rose in San Francisco.25 The result, "Claw-Code," was explicitly positioned as a "clean-room" implementation.25

The technical achievement was staggering:

* The repository reached 50,000 stars on GitHub in under two hours.7  
* By April 2, it had reached 136,000 stars and 101,000 forks, surpassing the original project's engagement.25  
* Independent audits confirmed that Claw-Code contained no Anthropic source code, model weights, or API keys, relying instead on the architectural patterns revealed in the leak.25

The legal status of Claw-Code remains in a grey area. While clean-room reverse engineering has strong legal precedent, the speed with which it was accomplished—enabled by the very tools it was replicating—raises novel questions about copyright in the age of generative AI.6 This is particularly critical following the March 2026 Supreme Court decision to decline revisiting the "human authorship standard," which suggests that much of the AI-generated code within Claude Code may not even carry intellectual property protection.6

### **DMCA Overreach and Retraction**

Anthropic's legal response was initially characterized by significant overreach. Automated DMCA takedown notices issued to GitHub targeted a fork network connected to Anthropic’s own public repository, resulting in the removal of over 8,100 repositories.25 Many of these repositories contained only legitimate documentation, examples, or skills that had nothing to do with the leaked code.25 Following a strong backlash from the community and accusations of "DMCA abuse" by figures like Gergely Orosz, Anthropic retracted the bulk of the notices, narrowing the final takedown to just one primary repository and 96 specific forks.25

## **Strategic Implications and Future Outlook**

The Claude Code source leak is likely to be remembered as one of the most consequential "accidental open-sourcing" events in the history of artificial intelligence.11 By exposing the internal mechanics of a production-grade agent system, Anthropic has provided a free engineering education to its competitors—from giants like OpenAI and Google to nimble rivals like Cursor and Windsurf.2

### **Competitive Intelligence and the End of the "Harness" Advantage**

The leak reveals that a significant portion of an agent's capability comes not from the underlying model, but from the software harness that provides instructions, guardrails, and memory architecture.6 Competitors now have a detailed roadmap to clone Claude Code's features—such as KAIROS, autoDream, and the self-healing memory system—without the need for costly reverse engineering.3

For Anthropic, the damage is architectural rather than operational.25 While they can patch the vulnerabilities and pull the npm package, they cannot "un-leak" the roadmap or the internal benchmarks that show exactly where their current models are struggling.2

### **Lessons for AI Development Governance**

The technical cause of the leak—a single missing line in a .npmignore file—offers a profound lesson for the industry: AI-assisted velocity is not the same as AI-assisted oversight.6 Anthropic, a company valued at $61 billion and preparing for an IPO, proved that even the most sophisticated AI lab is vulnerable to mundane packaging errors.11

The incident underscores the need for "defense-in-depth" in AI deployment pipelines, including:

* Strict CI/CD checks that fail builds if .map files are detected in production packages.18  
* The use of native installers (like curl | bash) to avoid the volatility of the npm dependency chain.2  
* Mandatory manual reviews and "dry-runs" (using npm pack) before publishing to public registries.18

As AI systems become more complex and autonomous, the operational surface area continues to widen.6 The Claude Code leak of 2026 serves as a stark reminder that as we build more powerful agents to automate our work, the discipline required to secure the infrastructure behind those agents remains a human responsibility.6 The "blueprint" for the future of AI is now public, and the race to build the next generation of agents has just accelerated—at Anthropic’s expense.

#### **Works cited**

1. Claude Code Source Leaked via npm Packaging Error, Anthropic ..., accessed April 6, 2026, [https://thehackernews.com/2026/04/claude-code-tleaked-via-npm-packaging.html](https://thehackernews.com/2026/04/claude-code-tleaked-via-npm-packaging.html)  
2. Claude Code's source code appears to have leaked: here's what we know | VentureBeat, accessed April 6, 2026, [https://venturebeat.com/technology/claude-codes-source-code-appears-to-have-leaked-heres-what-we-know](https://venturebeat.com/technology/claude-codes-source-code-appears-to-have-leaked-heres-what-we-know)  
3. Claude Code leak, Anthropic security incident, AI source code exposure | PointGuard AI, accessed April 6, 2026, [https://www.pointguardai.com/ai-security-incidents/claude-code-leak-gives-rivals-an-ai-blueprint](https://www.pointguardai.com/ai-security-incidents/claude-code-leak-gives-rivals-an-ai-blueprint)  
4. Anthropic Claude Code Leak | ThreatLabz \- Zscaler, Inc., accessed April 6, 2026, [https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak](https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak)  
5. The Anthropic Code Leak: When a Packaging Error Becomes a Supply Chain Risk, accessed April 6, 2026, [https://hawk-eye.io/2026/04/the-anthropic-code-leak-when-a-packaging-error-becomes-a-supply-chain-risk/](https://hawk-eye.io/2026/04/the-anthropic-code-leak-when-a-packaging-error-becomes-a-supply-chain-risk/)  
6. In the wake of Claude Code's source code leak, 5 actions enterprise security leaders should take now | VentureBeat, accessed April 6, 2026, [https://venturebeat.com/security/claude-code-512000-line-source-leak-attack-paths-audit-security-leaders](https://venturebeat.com/security/claude-code-512000-line-source-leak-attack-paths-audit-security-leaders)  
7. The Great Claude Code Leak of 2026: Accident, Incompetence, or the Best PR Stunt in AI History? \- DEV Community, accessed April 6, 2026, [https://dev.to/varshithvhegde/the-great-claude-code-leak-of-2026-accident-incompetence-or-the-best-pr-stunt-in-ai-history-3igm](https://dev.to/varshithvhegde/the-great-claude-code-leak-of-2026-accident-incompetence-or-the-best-pr-stunt-in-ai-history-3igm)  
8. Anthropic blunder exposes 2,000 lines of Claude Code’s internal source code: What it reveals, accessed April 6, 2026, [https://indianexpress.com/article/technology/artificial-intelligence/anthropic-blunder-exposes-claude-code-internal-source-code-10613346/](https://indianexpress.com/article/technology/artificial-intelligence/anthropic-blunder-exposes-claude-code-internal-source-code-10613346/)  
9. Anthropic accidentally exposes Claude Code secrets for second time in a week: What it means, accessed April 6, 2026, [https://www.financialexpress.com/life/technology-anthropic-accidentally-exposes-claude-code-secrets-for-second-time-in-a-week-what-it-means-4191448/](https://www.financialexpress.com/life/technology-anthropic-accidentally-exposes-claude-code-secrets-for-second-time-in-a-week-what-it-means-4191448/)  
10. Claude Mythos: The Model That Leaked, and Why Cybersecurity Got ..., accessed April 6, 2026, [https://www.techosaurus.co.uk/news/2026/04/01/claude-mythos-the-model-that/](https://www.techosaurus.co.uk/news/2026/04/01/claude-mythos-the-model-that/)  
11. Anthropic Leaked Its Own Road Map–Here's the Real Lesson | SUCCESS, accessed April 6, 2026, [https://www.success.com/anthropic-claude-code-leak-business-lessons](https://www.success.com/anthropic-claude-code-leak-business-lessons)  
12. Anthropic's AI coding tool, Claude Code, accidentally reveals its source code; here's what happened, accessed April 6, 2026, [https://www.livemint.com/technology/tech-news/anthropics-ai-coding-tool-claude-code-accidentally-reveals-its-source-code-heres-what-happened-11774977255558.html](https://www.livemint.com/technology/tech-news/anthropics-ai-coding-tool-claude-code-accidentally-reveals-its-source-code-heres-what-happened-11774977255558.html)  
13. Claude Code source exposure: What enterprises should do next \- Tanium, accessed April 6, 2026, [https://www.tanium.com/blog/claude-code-source-exposure/](https://www.tanium.com/blog/claude-code-source-exposure/)  
14. Is the Claude Code leak caused by a bug in Bun? The Bun founder ..., accessed April 6, 2026, [https://www.gate.com/news/detail/is-the-claude-code-leak-caused-by-a-bug-in-bun-the-bun-founder-denied-it-19949139](https://www.gate.com/news/detail/is-the-claude-code-leak-caused-by-a-bug-in-bun-the-bun-founder-denied-it-19949139)  
15. Bun is joining Anthropic | Bun Blog, accessed April 6, 2026, [https://bun.com/blog/bun-joins-anthropic](https://bun.com/blog/bun-joins-anthropic)  
16. Bytes \#445 \- Why Anthropic bought Bun, accessed April 6, 2026, [https://bytes.dev/archives/445](https://bytes.dev/archives/445)  
17. Why Anthropic Had to Buy Bun \- Stéphane Derosiaux \- Medium, accessed April 6, 2026, [https://sderosiaux.medium.com/why-anthropic-had-to-buy-bun-09606c1028ca](https://sderosiaux.medium.com/why-anthropic-had-to-buy-bun-09606c1028ca)  
18. Anthropic Accidentally Leaked Claude Code's Entire Source — Here's What Was Inside, accessed April 6, 2026, [https://nodesource.com/blog/anthropic-claude-code-source-leak-bun-bug](https://nodesource.com/blog/anthropic-claude-code-source-leak-bun-bug)  
19. Bun Founder Denies Connection to Claude Code Data Leak | Gate News, accessed April 6, 2026, [https://www.gate.com/news/detail/bun-founder-denies-any-connection-to-claude-code-data-leak-immediately-19952075](https://www.gate.com/news/detail/bun-founder-denies-any-connection-to-claude-code-data-leak-immediately-19952075)  
20. Claude Code's Entire Source Code Got Leaked via a Sourcemap in npm, Let's Talk About it, accessed April 6, 2026, [https://kuber.studio/blog/AI/Claude-Code's-Entire-Source-Code-Got-Leaked-via-a-Sourcemap-in-npm,-Let's-Talk-About-it](https://kuber.studio/blog/AI/Claude-Code's-Entire-Source-Code-Got-Leaked-via-a-Sourcemap-in-npm,-Let's-Talk-About-it)  
21. Claude Code Source Map Leak, What Was Exposed and What It Means \- Penligent, accessed April 6, 2026, [https://www.penligent.ai/hackinglabs/claude-code-source-map-leak-what-was-exposed-and-what-it-means/](https://www.penligent.ai/hackinglabs/claude-code-source-map-leak-what-was-exposed-and-what-it-means/)  
22. A Look Inside Claude's Leaked AI Coding Agent \- Varonis, accessed April 6, 2026, [https://www.varonis.com/blog/claude-code-leak](https://www.varonis.com/blog/claude-code-leak)  
23. Claude Code Source Leak 2026: The Complete Guide to What Was Exposed, accessed April 6, 2026, [https://decodethefuture.org/en/claude-code-source-leak-complete-guide/](https://decodethefuture.org/en/claude-code-source-leak-complete-guide/)  
24. Anthropic leaks source code for its AI coding agent Claude, accessed April 6, 2026, [https://lynnwoodtimes.com/2026/04/04/claude/](https://lynnwoodtimes.com/2026/04/04/claude/)  
25. The Claude Code Leak: What the Harness Actually Looks Like, accessed April 6, 2026, [https://paddo.dev/blog/claude-code-leak-harness-exposed/](https://paddo.dev/blog/claude-code-leak-harness-exposed/)  
26. When Anthropic Accidentally Opened Its Own Vault: The Claude Code Leak of March 31, 2026, accessed April 6, 2026, [https://thebossnewspapers.com/2026/04/03/when-anthropic-accidentally-opened-its-own-vault-the-claude-code-leak-of-march-31-2026/](https://thebossnewspapers.com/2026/04/03/when-anthropic-accidentally-opened-its-own-vault-the-claude-code-leak-of-march-31-2026/)  
27. Claude Code Source Code Leak: The Full Story 2026 \- Build Fast with AI, accessed April 6, 2026, [https://www.buildfastwithai.com/blogs/claude-code-source-code-leak-2026](https://www.buildfastwithai.com/blogs/claude-code-source-code-leak-2026)  
28. What is Anthropic Claude Mythos? Everything to know about viral leaked AI model that set alarms in cybersecurity, accessed April 6, 2026, [https://www.financialexpress.com/life/technology-what-is-anthropic-claude-mythos-everything-to-know-about-viral-leaked-ai-model-that-set-alarms-in-cybersecurity-4187074/](https://www.financialexpress.com/life/technology-what-is-anthropic-claude-mythos-everything-to-know-about-viral-leaked-ai-model-that-set-alarms-in-cybersecurity-4187074/)  
29. Anthropic Leak Claude Code: 512,000 Lines Exposed by One Bug \- Ruh AI Blog, accessed April 6, 2026, [https://www.ruh.ai/blogs/anthropic-claude-code-leak-2026-npm-source-exposure](https://www.ruh.ai/blogs/anthropic-claude-code-leak-2026-npm-source-exposure)  
30. Claude Mythos: Anthropic's New AI Model Beyond Opus \- BeFreed, accessed April 6, 2026, [https://www.befreed.ai/blog/claude-mythos-anthropic-ai-model-2026](https://www.befreed.ai/blog/claude-mythos-anthropic-ai-model-2026)  
31. Anthropic's Mythos leak is a wake-up call: Phishing 3.0 is already here \- Ironscales, accessed April 6, 2026, [https://ironscales.com/blog/anthropics-mythos-leak-is-a-wake-up-call-phishing-3.0-is-already-here](https://ironscales.com/blog/anthropics-mythos-leak-is-a-wake-up-call-phishing-3.0-is-already-here)  
32. Anthropic Disrupts First Documented Case of Large-Scale AI-Orchestrated Cyberattack | Paul, Weiss, accessed April 6, 2026, [https://www.paulweiss.com/media/3rolso5p/anthropic\_disrupts\_first\_documented\_case\_of\_large-scale\_ai-orchestrated\_cyberattack.pdf](https://www.paulweiss.com/media/3rolso5p/anthropic_disrupts_first_documented_case_of_large-scale_ai-orchestrated_cyberattack.pdf)  
33. Anthropic AI cyberattacks \- Bloomsbury Intelligence and Security Institute (BISI), accessed April 6, 2026, [https://bisi.org.uk/reports/anthropic-ai-cyberattacks](https://bisi.org.uk/reports/anthropic-ai-cyberattacks)  
34. Disrupting the first reported AI-orchestrated cyber espionage campaign \- Anthropic, accessed April 6, 2026, [https://www.anthropic.com/news/disrupting-AI-espionage](https://www.anthropic.com/news/disrupting-AI-espionage)  
35. Claude Mythos (Opus 5\) Leaked: What We Know So Far ..., accessed April 6, 2026, [https://wavespeed.ai/blog/posts/claude-mythos-opus-5-leak-what-we-know/](https://wavespeed.ai/blog/posts/claude-mythos-opus-5-leak-what-we-know/)  
36. Claude Code Flaws Allow Remote Code Execution and API Key Exfiltration, accessed April 6, 2026, [https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html)  
37. Ransomware Trends & Data Insights: September 2025 \- Arete Incident Response, accessed April 6, 2026, [https://areteir.com/resources/ransomware-trends-data-insights-september-2025](https://areteir.com/resources/ransomware-trends-data-insights-september-2025)  
38. Caught in the Hook: RCE and API Token Exfiltration Through Claude Code Project Files | CVE-2025-59536 | CVE-2026-21852 \- Check Point Research, accessed April 6, 2026, [https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)  
39. CVE-2026-21852: Claude Code Information Disclosure Flaw \- SentinelOne, accessed April 6, 2026, [https://www.sentinelone.com/vulnerability-database/cve-2026-21852/](https://www.sentinelone.com/vulnerability-database/cve-2026-21852/)  
40. Anthropic's 500k-Line Slip: From Source Leak to "Claw-Code" Reshell \- hyperight.com, accessed April 6, 2026, [https://hyperight.com/anthropics-500k-line-slip-from-source-leak-to-claw-code-reshell/](https://hyperight.com/anthropics-500k-line-slip-from-source-leak-to-claw-code-reshell/)  
41. After Anthropic Open-Sourced Its Source Code, It Issued Over 8,000 Copyright Takedown Requests—Its “Security-First” Image Suffers Its Most Awkward Week Yet \- 深潮TechFlow, accessed April 6, 2026, [https://www.techflowpost.com/en-US/article/30966](https://www.techflowpost.com/en-US/article/30966)  
42. What Is Claw Code? The Claude Code Rewrite Explained ..., accessed April 6, 2026, [https://wavespeed.ai/blog/posts/what-is-claw-code/](https://wavespeed.ai/blog/posts/what-is-claw-code/)