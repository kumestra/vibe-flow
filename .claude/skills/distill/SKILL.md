---
name: distill
description: Distill conversation into a structured document by topic
disable-model-invocation: true
---

# Distill Conversation to Document

The user wants to extract and organize information from the current conversation into a document.

**Topic:** $ARGUMENTS

## Instructions

1. If `$ARGUMENTS` is empty, do NOT proceed. Instead, tell the user: "Please provide a topic, e.g. `/distill auth design for API`" and stop.
2. Scan the entire conversation history.
3. Extract all information relevant to the topic above.
   - **Privacy rule**: Never include personal user data in the document. This includes but is not limited to: names, gender, age, passwords, API keys, tokens, email addresses, phone numbers, addresses, or any other private/sensitive information. If such data appears in the conversation, omit it entirely.
4. Organize the content in **logical order** (not chat order). Group related ideas together and build a coherent narrative or structure.
5. Choose the best document format for the content. For example:
   - **Design doc** — for software architecture or system design discussions
   - **Concept notes** — for learning and Q&A about a concept or technology
   - **Decision log** — for discussions that led to specific decisions
   - **Tutorial/guide** — for how-to or step-by-step discussions
   - **Comparison/analysis** — for evaluating trade-offs between options
   - Use any other format that best fits the content.
6. Write the document in Markdown. Where a Mermaid diagram would help the reader understand structure, flow, or relationships, include one using a `mermaid` fenced code block. Where an emoji would help the reader quickly grasp a concept, category, or tone, add it inline. Where a reference would help the reader navigate or find related context, add one — use link references for external URLs, heading anchors for cross-section links, or footnotes for supplementary notes.
7. Auto-generate a concise, descriptive filename in kebab-case based on the topic (e.g., `auth-design.md`, `react-state-management.md`).
8. Before writing, check if the filename already exists in `docs/distilled/`. If it does, automatically append a version suffix to avoid conflict (e.g., `auth-design-v2.md`, `auth-design-v3.md`) and proceed without asking the user.
9. Create the directory `docs/distilled/` if it does not exist.
10. Write the file to `docs/distilled/<generated-filename>.md`.
11. After writing, tell the user the file path and a brief summary of what was captured.
