# Generics in Rust

## What are Generics?

Generics let you write code that works for **any type** instead of a specific one. Write once, use for many types.

Without generics — you need a separate function for each type:
```rust
fn largest_i32(a: i32, b: i32) -> i32 { if a > b { a } else { b } }
fn largest_f64(a: f64, b: f64) -> f64 { if a > b { a } else { b } }
// duplicate code for every type...
```

With generics — one function works for all:
```rust
fn largest<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}
```

---

## Syntax

The generic type parameter is declared inside angle brackets `<T>` after the name:

```rust
fn name<T>(...)         // function
struct Name<T> { ... }  // struct
enum Name<T> { ... }    // enum
impl<T> Name<T> { ... } // impl block
```

`T` is just a convention (short for "Type") — you can use any name:
```rust
fn foo<MyType>(x: MyType) -> MyType { ... }  // valid but uncommon
fn foo<T>(x: T) -> T { ... }                 // conventional
```

Multiple type parameters use different letters:
```rust
fn foo<T, E>(value: T, error: E) { ... }  // two independent type parameters
```

---

## Generics in Functions

```rust
fn identity<T>(x: T) -> T {
    x  // returns whatever was passed in, same type
}

identity(42);       // T = i32, returns 42
identity("hello");  // T = &str, returns "hello"
identity(3.14);     // T = f64, returns 3.14
```

The compiler infers `T` from what you pass in — no need to specify it explicitly.

You can specify it explicitly using **turbofish syntax** (`::<T>`):
```rust
identity::<i32>(42);    // explicitly T = i32
"42".parse::<i32>();    // explicitly parse into i32
```

---

## Generics in Structs

```rust
struct Pair<T> {
    first: T,
    second: T,
}

let p1 = Pair { first: 1, second: 2 };          // T = i32
let p2 = Pair { first: "hi", second: "bye" };   // T = &str
```

Multiple type parameters:
```rust
struct KeyValue<K, V> {
    key: K,
    value: V,
}

let kv = KeyValue { key: "name", value: 42 };  // K = &str, V = i32
```

---

## Generics in Enums

This is how `Result` and `Option` are defined in the standard library:

```rust
enum Option<T> {
    Some(T),  // carries a value of type T
    None,     // carries nothing
}

enum Result<T, E> {
    Ok(T),   // carries a success value of type T
    Err(E),  // carries an error of type E
}
```

Usage:
```rust
let a: Option<i32> = Some(42);     // T = i32
let b: Option<&str> = Some("hi");  // T = &str
let c: Option<i32> = None;         // T = i32, no value

let d: Result<i32, &str> = Ok(42);           // T = i32, E = &str
let e: Result<i32, &str> = Err("failed");    // T = i32, E = &str
```

---

## Generics in impl Blocks

```rust
struct Pair<T> {
    first: T,
    second: T,
}

// impl<T> means "for any type T"
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Self {
        Pair { first, second }
    }
}

let p = Pair::new(1, 2);          // T = i32
let p = Pair::new("a", "b");      // T = &str
```

---

## Trait Bounds

A raw `<T>` accepts any type — but sometimes you need to restrict what types are allowed.

**Trait bounds** say "T must implement this trait":

```rust
// T must implement PartialOrd (supports < > comparison)
fn largest<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}
```

Without the bound, `a > b` won't compile — the compiler doesn't know if `T` supports comparison.

---

## Multiple Trait Bounds

Use `+` to require multiple traits:

```rust
// T must implement both PartialOrd and Display
fn print_largest<T: PartialOrd + std::fmt::Display>(a: T, b: T) {
    if a > b {
        println!("largest: {}", a);
    } else {
        println!("largest: {}", b);
    }
}
```

---

## where Clause — Cleaner Syntax for Complex Bounds

When bounds get long, use a `where` clause for readability:

```rust
// hard to read inline
fn foo<T: PartialOrd + std::fmt::Display + Clone, E: std::fmt::Debug>(a: T, b: E) { ... }

// cleaner with where
fn foo<T, E>(a: T, b: E)
where
    T: PartialOrd + std::fmt::Display + Clone,
    E: std::fmt::Debug,
{ ... }
```

Same meaning, just formatted differently.

---

## How Rust Compiles Generics — Monomorphization

Unlike Java (which uses type erasure), Rust resolves generics **at compile time**:

```rust
largest(5, 10);       // compiler generates a version for i32
largest(3.14, 2.71);  // compiler generates a version for f64
```

The compiler creates separate specialized functions for each type used. This is called **monomorphization**.

Result: **zero runtime overhead** — generics in Rust are as fast as writing the function manually for each type.

| | Java | Rust |
|---|---|---|
| When resolved | Runtime (type erasure) | Compile time (monomorphization) |
| Runtime overhead | Yes (boxing for primitives) | None |
| Binary size | Smaller (one copy) | Larger (one copy per type used) |

---

## Common Built-in Trait Bounds

| Trait | Meaning |
|---|---|
| `PartialOrd` | supports `<`, `>`, `<=`, `>=` |
| `PartialEq` | supports `==`, `!=` |
| `Clone` | can be cloned with `.clone()` |
| `Copy` | can be copied implicitly (integers, bools, chars) |
| `Display` | can be printed with `{}` |
| `Debug` | can be printed with `{:?}` |
| `Default` | has a default value via `T::default()` |

---

## Comparison to Other Languages

| | Java | C++ | Rust |
|---|---|---|---|
| Name | Generics | Templates | Generics |
| Syntax | `<T>` | `<T>` | `<T>` |
| Resolved at | Runtime (type erasure) | Compile time | Compile time |
| Constraints | `extends` / `implements` | `concept` (C++20) | Trait bounds |
| Runtime cost | Yes (boxing) | None | None |

---

## Summary

```
// generic function
fn name<T: Trait>(arg: T) -> T { ... }

// generic struct
struct Name<T> { field: T }

// generic enum
enum Name<T> { Variant(T), Empty }

// generic impl
impl<T> Name<T> { fn method(&self) -> T { ... } }

// multiple parameters
fn name<T, E>(a: T, b: E) { ... }

// multiple bounds
fn name<T: Trait1 + Trait2>(a: T) { ... }

// where clause (same as above, cleaner for complex bounds)
fn name<T>(a: T) where T: Trait1 + Trait2 { ... }
```
