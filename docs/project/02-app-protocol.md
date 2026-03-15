# Application Layer Protocol

## Overview

This is a simple custom protocol designed for this project to test the SOCKS5 proxy without the complexity of HTTP. It runs over TCP.

The goal is to be as simple as possible while solving the core TCP problem: **knowing where one message ends and the next begins**.

---

## The Problem with Raw TCP

TCP is a byte stream — it has no concept of message boundaries. If a client sends "hello" and "world" as two separate messages, the server might receive:

- `"hello"` and `"world"` separately — ideal but not guaranteed
- `"helloworld"` merged — one read, two messages
- `"hel"` then `"loworld"` — split mid-message

The protocol must define how to detect message boundaries.

---

## Protocol Design

**Length-prefixed messages** — the simplest and most reliable solution.

```
+--------+----------+
| LENGTH |  PAYLOAD |
+--------+----------+
|   4    | variable |
+--------+----------+
```

- `LENGTH` — 4 bytes, unsigned 32-bit integer, big-endian
  - Indicates how many bytes the payload contains
- `PAYLOAD` — N bytes of UTF-8 encoded text
  - N is exactly the value of LENGTH

---

## How to Read a Message

1. Read exactly **4 bytes** → parse as u32 big-endian → this is the payload length `N`
2. Read exactly **N bytes** → decode as UTF-8 → this is the message

No scanning for special characters. No ambiguity. Always two steps.

---

## How to Write a Message

1. Encode the text as UTF-8 bytes → get length `N`
2. Write `N` as 4 bytes big-endian
3. Write the payload bytes

---

## Example

Sending the message `"hello"` (5 bytes):

```
00 00 00 05 68 65 6c 6c 6f
└─────────┘ └─────────────┘
  length=5     "hello"
```

Sending the message `"hi"` (2 bytes):

```
00 00 00 02 68 69
└─────────┘ └───┘
  length=2   "hi"
```

---

## Why Big-Endian?

Multi-byte numbers can be stored in two ways:

- **Big-endian** — most significant byte first: `00 00 00 05`
- **Little-endian** — least significant byte first: `05 00 00 00`

Network protocols (TCP/IP, HTTP, SOCKS5) universally use **big-endian**, also called **network byte order**. We follow the same convention.

---

## Limits

- Maximum message size: 2^32 - 1 bytes (~4 GB) — more than enough for testing
- Payload must be valid UTF-8 text

---

## Usage in This Project

This protocol is used by:
- `tcp_server` — listens, receives a message, prints it, sends a reply
- `tcp_client` — connects through the SOCKS5 proxy, sends a message, receives the reply

The SOCKS5 proxy sits in between and forwards the raw bytes without knowing or caring about this protocol.

```
tcp_client ──[this protocol]──→ socks5_proxy ──[this protocol]──→ tcp_server
```
