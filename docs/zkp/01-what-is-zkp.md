# Zero Knowledge Proof (ZKP)

## What is ZKP?

You can **prove you know something** without **revealing what you know**.

---

## The Core Model

ZKP proves a relationship `f(x) = y` where:

```
f(x) = y

f → public  (everyone knows the function)
x → private (only you know the input)
y → public  (everyone can see the output)

ZKP proves: "I know an x such that f(x) = y"
```

The function `f` can be anything — hashing, comparison, arithmetic — as long as it can be expressed as a circuit.

| Function | Private input | Public output | Proves |
|---|---|---|---|
| `SHA256(x) = y` | `x` (password) | `y` (hash) | I know the password |
| `age(birthdate) >= 18` | birthdate | true | I'm an adult |
| `balance - amount >= 0` | balance | true | I have enough money |
| `vote ∈ {A, B, C}` | vote | true | My vote is valid |

**ZKP separates what you prove from what you reveal.** You prove `f(x) = y` holds, but only reveal `f` and `y`, never `x`.

---

## The Cave Analogy

Imagine a ring-shaped cave with a locked door in the middle. Two paths (A and B) lead to the door.

```
        entrance
           │
      ┌────┴────┐
      │         │
    path A    path B
      │         │
      └──[door]─┘
```

1. You claim you know the door's password
2. I stand at the entrance, you walk in and pick a random path
3. I shout "come out from path A" (or B, randomly)
4. If you know the password → you can always come out from whichever side I ask
5. If you don't know → you can only succeed 50% of the time

After 20 rounds, the chance of faking it is `(1/2)^20` = 1 in 1,048,576.

I'm now convinced you know the password — but I never learned the password itself.

---

## Three Properties

| Property | Meaning |
|---|---|
| **Completeness** | If you know the secret, you can always prove it |
| **Soundness** | If you don't know, you can't fake it |
| **Zero Knowledge** | The verifier learns nothing about the secret |

---

## Example — Hash Preimage

**Setup:**
- You know a secret string: `x = "my_secret"`
- Its hash is public: `SHA256("my_secret") = a1b2c3...`
- **Goal:** Prove you know `x` without revealing it.

**Step 1 — Define a Circuit**

A ZKP circuit describes **what** you want to prove, expressed as math constraints.

```
circuit HashPreimage:
    private input: x          ← only you know this
    public input:  hash       ← everyone can see this

    constraint: SHA256(x) == hash
```

The circuit is public. Your private input `x` stays with you.

**Step 2 — Circuit Becomes Math**

The framework converts the circuit into thousands of simple equations:

```
a + b = c
a * b = d
...
(tens of thousands of these for SHA256)
```

SHA256 produces ~30,000 constraints. Hash functions designed for ZKP (like Poseidon) produce only ~300.

**Step 3 — Generate the Proof**

The prover algorithm takes the circuit (public), your secret `x` (private), and the hash (public). It produces a **proof** — a small piece of data (~200 bytes) that encodes "all equations are satisfied" without revealing the values.

**Step 4 — Anyone Can Verify**

The verifier takes the circuit (public), the hash (public), and your proof. Runs a fast check → outputs **true** or **false**.

| | Prover | Verifier |
|---|---|---|
| Knows `x`? | Yes | No |
| Time | Slow (seconds) | Fast (milliseconds) |
| Output | Proof | true / false |

**Full Flow:**

```
You:       x = "my_secret"
              │
         SHA256(x) = a1b2c3...     ← public
              │
         circuit + x → [prover] → proof (200 bytes)
              │
Verifier: circuit + hash + proof → [verifier] → true ✓
```

---

## Real World Uses

| Use Case | How ZKP Helps |
|---|---|
| **Blockchain** (Zcash, zkSync) | Prove transaction is valid without revealing sender, receiver, or amount |
| **Authentication** | Prove you know a password without sending it |
| **Voting** | Prove your vote is valid without revealing who you voted for |
| **Identity** | Prove you are over 18 without revealing your birthdate |

---

## Using ZKP in Practice

When using a ZKP library, you only write the **circuit** — the function `f` with input `x` and output `y`. The framework handles everything else.

**You write:**
- The circuit (the function `f`)
- Provide the private input `x`
- Provide the public output `y`

**The framework handles:**
- Converting your circuit into math equations
- Generating the proof
- Verifying the proof
- All the cryptography (elliptic curves, polynomials, etc.)

Example in circom:

```circom
template Multiplier() {
    signal private input a;
    signal private input b;
    signal output c;

    c <== a * b;    // constraint: a * b must equal c
}
```

This proves: "I know two numbers `a` and `b` whose product is `c`" — without revealing `a` or `b`.

Writing a ZKP system from scratch requires deep math (abstract algebra, number theory, polynomial commitments, elliptic curve cryptography). In practice, developers always use frameworks:

| Framework | Language | Used by |
|---|---|---|
| **circom + snarkjs** | JavaScript | Most popular for beginners |
| **Halo2** | Rust | Zcash, Scroll |
| **Arkworks** | Rust | Research projects |
| **gnark** | Go | Linea, ConsenSys |
| **Cairo** | Custom lang | StarkNet |

---

## Proof Systems

Different mathematical approaches to construct proofs:

| System | Trusted Setup? | Proof Size | Verify Speed |
|---|---|---|---|
| **Groth16** | Yes | Very small (~200 bytes) | Very fast |
| **PLONK** | Universal (one-time) | Small | Fast |
| **STARKs** | No | Large (~100 KB) | Fast |
| **Halo2** | No | Small | Fast |

- **Trusted setup** = a one-time ceremony to generate shared parameters. If compromised, fake proofs can be created.
- **STARKs** avoid this but produce larger proofs.
- **Groth16** is the most widely deployed (used by Zcash).

---

## Summary

```
ZKP = prove f(x) = y without revealing x

Core model:
├── f → public  (the function / circuit)
├── x → private (your secret input)
└── y → public  (the output)

Three properties:
├── Completeness   → honest prover always succeeds
├── Soundness      → cheater can't fake it
└── Zero Knowledge → verifier learns nothing about x

Workflow:
├── Write circuit (define the relationship)
├── Prover generates proof (slow, uses private input)
└── Verifier checks proof (fast, no private input)

Practice:
├── Use frameworks (circom, arkworks, gnark)
└── Don't write crypto from scratch
```
