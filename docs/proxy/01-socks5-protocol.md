# SOCKS5 Protocol

## What is SOCKS?

SOCKS is a **proxy protocol** — it sits between a client and a target server, forwarding traffic on behalf of the client.

```
without proxy:
client ──────────────────────────── target server

with SOCKS proxy:
client ──── SOCKS proxy ──────────── target server
```

The client talks to the proxy, the proxy talks to the target. The target only sees the proxy's IP, not the client's.

---

## Why SOCKS exists

**Original reason:** Firewall traversal — clients behind a corporate firewall couldn't reach the internet directly. The SOCKS proxy sat at the boundary and forwarded traffic on their behalf.

**Common uses today:**
- Privacy — hide your real IP
- Bypass geo-restrictions
- Access internal networks (VPN alternative)
- Tor network uses SOCKS5 as its interface

---

## SOCKS vs HTTP proxy

| | HTTP proxy | SOCKS proxy |
|---|---|---|
| Works with | HTTP/HTTPS only | Any TCP traffic (HTTP, SSH, FTP, etc.) |
| Protocol aware | Yes — reads HTTP headers | No — just forwards raw bytes |
| Level | Application layer | Session layer (lower) |
| Flexibility | Less | More |

SOCKS is **protocol agnostic** — it doesn't care what's inside the bytes. It just connects two endpoints and copies bytes between them.

---

## SOCKS4 vs SOCKS5

| | SOCKS4 | SOCKS5 |
|---|---|---|
| Authentication | No | Yes (username/password) |
| IPv6 support | No | Yes |
| Domain names | No (IP only) | Yes |
| UDP support | No | Yes |
| Complexity | Simple | Moderate |

SOCKS5 is the current standard.

---

## SOCKS5 — 3 Phases

SOCKS5 has three phases: greeting, connect request, and relay.

---

## Phase 1: Greeting

### Client → Proxy

```
+-----+----------+----------+
| VER | NMETHODS | METHODS  |
+-----+----------+----------+
|  1  |    1     | 1 to 255 |
+-----+----------+----------+
```

- `VER` — SOCKS version, always `0x05` for SOCKS5
- `NMETHODS` — how many auth methods the client supports
- `METHODS` — list of supported methods, one byte each:
  - `0x00` = no authentication
  - `0x02` = username/password

Example — client says "I support no-auth and user/pass":
```
05 02 00 02
│  │  │  └─ method: username/password (0x02)
│  │  └──── method: no auth (0x00)
│  └─────── 2 methods supported
└────────── SOCKS version 5
```

### Proxy → Client

```
+-----+--------+
| VER | METHOD |
+-----+--------+
|  1  |   1    |
+-----+--------+
```

Proxy picks one method and replies:
```
05 00
│  └─ chosen method: no auth
└──── SOCKS version 5
```

If proxy replies `0xFF` for METHOD, it means "no acceptable method" — connection is closed.

---

## Phase 2: Connect Request

### Client → Proxy

```
+-----+-----+------+------+----------+----------+
| VER | CMD | RSV  | ATYP |   ADDR   |   PORT   |
+-----+-----+------+------+----------+----------+
|  1  |  1  | 0x00 |  1   | variable |    2     |
+-----+-----+------+------+----------+----------+
```

- `VER` — `0x05` again
- `CMD` — command type:
  - `0x01` = CONNECT (most common — establish TCP connection)
  - `0x02` = BIND
  - `0x03` = UDP ASSOCIATE
- `RSV` — reserved, always `0x00`
- `ATYP` — address type:
  - `0x01` = IPv4 (4 bytes)
  - `0x03` = domain name (1 byte length + N bytes)
  - `0x04` = IPv6 (16 bytes)
- `ADDR` — the target address
- `PORT` — target port, 2 bytes, big-endian

Example — client wants to connect to `google.com:443`:
```
05 01 00 03 0a 67 6f 6f 67 6c 65 2e 63 6f 6d 01 bb
│  │  │  │  │  └──────────────────────────┘ └─────┘
│  │  │  │  │        "google.com"            port 443
│  │  │  │  └── 10 bytes (length of "google.com")
│  │  │  └───── 0x03 = domain name
│  │  └──────── reserved
│  └─────────── 0x01 = CONNECT
└────────────── version 5
```

### Proxy → Client

```
+-----+-----+------+------+----------+----------+
| VER | REP | RSV  | ATYP |   ADDR   |   PORT   |
+-----+-----+------+------+----------+----------+
|  1  |  1  | 0x00 |  1   | variable |    2     |
+-----+-----+------+------+----------+----------+
```

- `REP` — reply code:
  - `0x00` = success
  - `0x01` = general failure
  - `0x02` = connection not allowed
  - `0x03` = network unreachable
  - `0x04` = host unreachable
  - `0x05` = connection refused

Success reply:
```
05 00 00 01 00 00 00 00 00 00
│  │  │  │  └──────────┘ └───┘
│  │  │  │   bound addr    port (zeros, we don't care)
│  │  │  └── 0x01 = IPv4
│  │  └───── reserved
│  └──────── 0x00 = success
└─────────── version 5
```

---

## Phase 3: Relay

After the proxy sends a success reply, it:
1. Connects to the target server
2. Copies bytes from client → target
3. Copies bytes from target → client
4. Does this simultaneously, until one side closes the connection

The proxy becomes completely transparent — it has no idea what protocol is running inside (HTTP, SSH, anything). Just raw bytes flowing in both directions.

```
client ──→ proxy ──→ target
client ←── proxy ←── target
```

---

## Full Byte Flow Summary

```
── Phase 1: Greeting ──────────────────────────────────────────
C→P: 05 02 00 02
     (SOCKS5, 2 methods: no-auth + user/pass)
P→C: 05 00
     (SOCKS5, chosen: no auth)

── Phase 2: Connect ───────────────────────────────────────────
C→P: 05 01 00 03 0a 67 6f 6f 67 6c 65 2e 63 6f 6d 01 bb
     (CONNECT google.com:443)
P→C: 05 00 00 01 00 00 00 00 00 00
     (success)

── Phase 3: Relay ─────────────────────────────────────────────
C↔P↔T: raw bytes flowing in both directions indefinitely
```

---

## Key Points

- Every field has a **fixed position and size** — no text parsing needed, just read exact byte counts
- `PORT` is always **2 bytes, big-endian** — e.g. port 443 = `0x01 0xBB`
- Domain name address type (`0x03`) has a **1-byte length prefix** before the name
- Phase 3 requires **bidirectional concurrent copy** — both directions must flow simultaneously
- The proxy does **not** inspect what's inside — it's protocol agnostic
