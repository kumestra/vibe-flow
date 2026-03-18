# Zero Knowledge Proof (ZKP)

## What is ZKP?

You can **prove you know something** without **revealing what you know**.

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

| Function | Private input `x` | Public output `y` | Proves |
|---|---|---|---|
| `SHA256(x) = y` | password | hash | I know the password |
| `age(birthdate) >= 18` | birthdate | true | I'm an adult |
| `balance - amount >= 0` | balance | true | I have enough money |
| `vote ∈ {A, B, C}` | vote | true | My vote is valid |

**ZKP separates what you prove from what you reveal.** You prove `f(x) = y` holds, but only reveal `f` and `y`, never `x`.

---

## Real World Uses

| Use Case | How ZKP Helps |
|---|---|
| **Blockchain** (Zcash, zkSync) | Prove transaction is valid without revealing sender, receiver, or amount |
| **Authentication** | Prove you know a password without sending it |
| **Voting** | Prove your vote is valid without revealing who you voted for |
| **Identity** | Prove you are over 18 without revealing your birthdate |

---

## Trusted Setup

Before any proof can be generated or verified, a one-time ceremony must produce two cryptographic keys:

```
secret random numbers → CRS → proving key + verification key

proving key      → used by prover    → create proof
verification key → used by verifier  → check proof
```

If anyone keeps the secret random numbers after setup, they can generate fake proofs. So the secret must be destroyed.

**The Ceremony:**

To avoid trusting a single person, many people participate:

```
Person 1: generates random s1 → contributes → destroys s1
Person 2: takes output → adds random s2 → contributes → destroys s2
Person 3: takes output → adds random s3 → contributes → destroys s3
...
final output → proving key + verification key
```

As long as **at least one person** honestly destroys their secret, the system is safe.

Famous ceremonies:
- **Zcash** (2016) — 6 participants
- **Zcash Sapling** (2018) — 90 participants worldwide
- **Hermez** (2021) — 2000+ participants

**Types of trusted setup:**

| Type | Setup Required | Proof Size | Example |
|---|---|---|---|
| **Circuit-specific** | New ceremony per circuit | ~200 bytes | Groth16 |
| **Universal** | One ceremony for all circuits | Small | PLONK, Halo2 |
| **None** | No ceremony needed | ~100 KB | STARKs |

STARKs use only hash functions (no elliptic curves), so no secret randomness is needed. Trade-off: proof size is much larger (~100 KB vs ~200 bytes for Groth16).

---

## Example — Hash Preimage

**Setup:**
- You know a secret string: `x = "my_secret"`
- Its hash is public: `SHA256("my_secret") = a1b2c3...`
- **Goal:** Prove you know `x` without revealing it.

**Step 1 — Write a Circuit**

A ZKP circuit describes **what** you want to prove, expressed as math constraints.

```
circuit HashPreimage:
    private input: x          ← only you know this
    public input:  hash       ← everyone can see this

    constraint: SHA256(x) == hash
```

The circuit is public. Your private input `x` stays with you.

**Step 2 — Compile to R1CS Constraints**

ZKP proof systems only work with a specific math structure called **R1CS** (Rank-1 Constraint System) — a list of equations where each equation has exactly one multiplication:

```
(a * b = c)
```

The circom compiler breaks your circuit down into this format:

```
High level circuit:
    c <== a * b + 1;

Compiled to R1CS constraints:
    tmp = a * b        → (a * b - tmp = 0)
    c   = tmp + 1      → (tmp + 1 - c = 0)
```

Even `a * b + 1` needs two constraints because R1CS allows only one multiplication per equation. The output is a `.r1cs` file — a list of constraints with no actual values, just rules.

SHA256 produces ~30,000 constraints because its bit operations (XOR, AND, shifts) all need to be decomposed into multiplications and additions. Hash functions designed for ZKP (like Poseidon) produce only ~300.

**Step 3 — Compute the Witness**

The witness is all the values that satisfy every constraint — computed by the prover privately.

```
witness = {
    private input:  x = "my_secret"       ← only you know
    public input:   hash = a1b2c3...       ← everyone knows
    intermediate:   all values computed    ← internal wire values
                    along the way
}
```

The `.r1cs` contains only rules (no values). The witness fills them in:

```
.r1cs   =  "__ * __ = __"        ← the rule
witness =  " 3 * 11 = 33"        ← the rule filled with actual values
```

The witness is computed locally and never shared.

**Step 4 — Generate the Proof**

The prover combines the witness with the proving key to produce a proof:

```
witness + proving key → proof (~200 bytes)
```

The proving key provides elliptic curve parameters to "commit" to the witness values without revealing them. Think of it like a sealed envelope:

```
witness      = the secret message inside
proving key  = special ink that makes the envelope tamper-proof
proof        = the sealed envelope — verifier knows something valid
               is inside, but can never open it
```

**Step 5 — Verify**

The prover sends two things to the verifier:

```
proof         → "I computed the circuit correctly"
public inputs → hash = a1b2c3...  (the specific claim being made)
```

The verification key is already public — both prover and verifier have it from the trusted setup. The prover doesn't need to send it.

The verifier uses the verification key to check the proof against the public inputs, and outputs **true** or **false** in milliseconds — without ever seeing the witness.

| | Prover | Verifier |
|---|---|---|
| Has proving key? | Yes | No |
| Has verification key? | Yes | Yes (public) |
| Knows `x`? | Yes | No |
| Has witness? | Yes | No |
| Time | Slow (seconds) | Fast (milliseconds) |
| Output | Proof + public inputs | true / false |

**Full Flow:**

```
                    [trusted setup]
                     │           │
                proving key   verification key (public)
                     │           │
                     ↓           ↓
circuit + x → [witness] → [prover] → proof
                                        │
                                        ↓
                            proof + public inputs
                                        │
                                        ↓
                           [verifier] + verification key → true ✓
```

---

## Using ZKP in Practice

When using a ZKP library, you only write the **circuit**. The framework handles everything else.

**You write:**
- The circuit (the function `f` — what you want to prove)

**The framework handles:**
- Compiling the circuit to R1CS constraints
- Running the trusted setup ceremony
- Computing the witness from your private inputs
- Generating the proof
- Verifying the proof
- All the cryptography (elliptic curves, polynomials, etc.)

Example circuit in circom:

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

## Summary

```
ZKP = prove f(x) = y without revealing x

Core model:
├── f → public  (the circuit / function)
├── x → private (your secret input)
└── y → public  (the output / public inputs)

Three properties:
├── Completeness   → honest prover always succeeds
├── Soundness      → cheater can't fake it
└── Zero Knowledge → verifier learns nothing about x

Workflow:
├── Trusted setup  → proving key + verification key (one time)
├── Write circuit  → defines what to prove
├── Compile        → circuit becomes R1CS constraints (rules, no values)
├── Witness        → plug in private inputs, fill in all constraint values
├── Prove          → witness + proving key → proof (~200 bytes)
└── Verify         → proof + public inputs + verification key → true / false

Practice:
├── Use frameworks (circom + snarkjs, arkworks, gnark)
└── Don't write crypto from scratch
```
