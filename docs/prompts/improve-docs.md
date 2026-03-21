# Prompt: Improve Docs in a Directory

Use this prompt when you want Claude to review and improve a set of documentation files in a given folder.

---

Read all files in `<target-directory>`. Improve their quality — you have full editorial freedom: rewrite sections, restructure content, split or merge files, rename files, create new files, or delete existing ones. The goal is a well-organized, high-quality reference for this directory.

Guidelines:
- Content should be accurate, clear, and appropriately concise
- Examples should be practical and illustrative
- Related concepts should be grouped logically — reorganize across files if it improves cohesion
- Remove redundancy; don't repeat the same point in multiple places
- Headings, tables, and code blocks should be used where they add clarity
- Maintain a consistent tone and depth throughout

After making changes, briefly explain what you changed and why.

---

## Usage

Replace `<target-directory>` with the path to the folder you want improved, e.g.:

```
Read all files in `docs/python-lang/`. Improve their quality ...
```
