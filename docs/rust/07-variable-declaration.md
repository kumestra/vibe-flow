# let and mut in Rust

## `let` — declare a variable

```rust
let x = 5;
```

Creates a new variable `x` with value `5`.

---

## Immutable by default

In Rust, variables are **immutable by default** — once assigned, the value cannot change:

```rust
let x = 5;
x = 10;  // ❌ compiler error: cannot assign twice to immutable variable
```

This is the opposite of most languages (Python, Java, C++) where variables are mutable by default.

---

## `mut` — opt into mutability

Add `mut` to allow the value to change:

```rust
let mut x = 5;
x = 10;  // ✅ fine
```

You must explicitly opt into mutability. This forces you to think: "does this variable actually need to change?"

---

## `mut` applies to the whole variable and all its fields

Mutability is **all or nothing** — it applies to the variable and every field of the object it owns:

```rust
struct User {
    name: String,
    age: u32,
}

let user = User { name: String::from("Alice"), age: 30 };
user.name = String::from("Bob");  // ❌ error — user is not mut
user.age = 31;                    // ❌ error — user is not mut

let mut user = User { name: String::from("Alice"), age: 30 };
user.name = String::from("Bob");  // ✅ fine
user.age = 31;                    // ✅ fine
```

Unlike C++ where individual fields can be marked `const` or `mutable`, Rust applies mutability to the whole variable — simpler and more consistent.

---

## Why immutable by default?

- **Safety** — prevents accidental modification of values
- **Concurrency** — immutable data can be shared across threads without locks
- **Clarity** — when you see `mut`, you immediately know this variable changes somewhere

---

## `let` vs `const`

| | `let` | `const` |
|---|---|---|
| Scope | local to a block | can be global |
| Type annotation | optional (inferred) | required |
| Value | set at runtime | must be known at compile time |
| Mutable | with `mut` | never |

```rust
const MAX_SIZE: u32 = 1024;  // compile-time constant, can be global
let x = 5;                   // runtime variable, local to block
```

---

## Shadowing

Rust allows re-declaring a variable with the same name using `let` again — called **shadowing**:

```rust
let x = 5;
let x = x + 1;    // new x shadows old x, value is 6
let x = "hello";  // can even change the type
```

Shadowing is different from `mut`:
- `mut` — modifies the existing variable in place
- shadowing — creates a brand new variable with the same name, old one is gone

Useful when you want to transform a value through several steps and keep the same name.

---

## Summary

```
let x = 5;          // immutable — cannot change
let mut x = 5;      // mutable — can change
const X: u32 = 5;   // compile-time constant — never changes
let x = x + 1;      // shadowing — new variable, same name
```
