# Ownership in Rust

## What is Ownership?

Ownership is Rust's approach to memory management — no garbage collector, no manual `free()`. Instead, the compiler enforces rules at compile time that guarantee memory safety.

The core idea:
> Every value in memory has exactly **one owner** — a variable that is directly responsible for freeing that value when it goes out of scope.

---

## Three Rules of Ownership

1. Each value has exactly **one owner** at a time
2. When the owner goes out of scope, the value is **automatically freed**
3. Ownership can be **moved** to another variable (but only one owner at a time)

---

## Rule 1 & 2: Owner and Scope

```rust
{
    let s = String::from("hello");  // s owns the string in memory
    // use s...
}   // s goes out of scope → string is automatically freed here
```

No garbage collector needed. Memory is freed the moment the owner's scope ends — deterministic and predictable.

---

## Rule 3: Move — Ownership Transfers

```rust
let s1 = String::from("hello");  // s1 owns the string
let s2 = s1;                     // ownership MOVES to s2, s1 is now invalid
println!("{}", s1);              // ❌ compiler error — s1 no longer owns anything
println!("{}", s2);              // ✅ fine — s2 is the owner now
```

Unlike Java/Python where both variables would point to the same object, in Rust ownership transfers — `s1` becomes invalid after the move.

This prevents **double-free** bugs — only one variable is ever responsible for freeing the memory.

---

## Borrowing — Temporary Access Without Ownership

If other code needs to access a value without taking ownership, it **borrows** it via a reference:

**Immutable borrow (`&`)** — read-only access:
```rust
let s1 = String::from("hello");
let s2 = &s1;                    // s2 borrows s1, does NOT take ownership
println!("{}", s1);              // ✅ s1 still owns the string
println!("{}", s2);              // ✅ s2 can read through the reference
```

**Mutable borrow (`&mut`)** — read and write access:
```rust
let mut s1 = String::from("hello");
let s2 = &mut s1;                // s2 mutably borrows s1
s2.push_str(" world");           // s2 can modify s1's value
```

---

## Borrow Rules

The compiler enforces these rules to prevent data races:

1. You can have **many immutable borrows** at the same time (`&`)
2. You can have **only one mutable borrow** at a time (`&mut`)
3. You cannot have an immutable borrow and a mutable borrow at the same time

```rust
let mut s = String::from("hello");

let r1 = &s;      // ✅ immutable borrow
let r2 = &s;      // ✅ another immutable borrow — fine
let r3 = &mut s;  // ❌ cannot have mutable borrow while immutable borrows exist
```

---

## Ownership vs Borrowing vs Mutability

These are three separate but related concepts:

| Concept | What it controls |
|---|---|
| Ownership | Who is responsible for freeing the memory |
| Borrowing (`&`, `&mut`) | Temporary access without taking ownership |
| Mutability (`mut`) | Whether the value can be modified |

```rust
let s = String::from("hello");      // owns, immutable
let mut s = String::from("hello");  // owns, mutable
let r = &s;                         // borrows, immutable
let r = &mut s;                     // borrows, mutable
```

---

## Copy Types — No Move

Simple types that fit on the stack (integers, bools, chars, floats) are **copied** instead of moved:

```rust
let x = 5;
let y = x;          // x is COPIED into y, not moved
println!("{}", x);  // ✅ x is still valid — integers implement Copy
```

`String` is heap-allocated so it moves. `i32` is stack-allocated so it copies. The compiler knows which types implement `Copy`.

---

## Why Ownership?

| | Java/Python | C++ | Rust |
|---|---|---|---|
| Memory management | Garbage collector | Manual (`new`/`delete`) | Ownership (compile time) |
| When memory is freed | Non-deterministic (GC decides) | When you call `delete` | When owner goes out of scope |
| Dangling pointer | Not possible (GC prevents) | Possible (major bug source) | Not possible (compiler prevents) |
| Runtime overhead | GC pauses | None | None |

Rust gets the best of both worlds:
- Like C++ — no GC, predictable performance
- Like Java — memory safety guaranteed, no dangling pointers
- Unlike both — enforced at **compile time**, zero runtime cost

---

## Summary

```
Ownership:
- one owner per value
- owner goes out of scope → value freed
- assignment moves ownership (for heap types)

Borrowing:
- & → immutable reference, many allowed at once
- &mut → mutable reference, only one allowed at a time

Copy types (stack):
- i32, f64, bool, char → copied on assignment, not moved

Move types (heap):
- String, Vec, Box → moved on assignment, old variable invalid
```
