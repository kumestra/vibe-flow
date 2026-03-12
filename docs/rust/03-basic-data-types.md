# Basic Data Types in Rust

Rust is a **statically typed** language — every variable has a type known at compile time. However, Rust can often **infer** the type for you, so you don't always need to write it explicitly.

---

## Scalar Types

Scalar types represent a single value. Rust has four primary scalar types:

---

### 1. Integers

Whole numbers (no decimal point).

| Type | Size | Range |
|------|------|-------|
| `i8` | 8-bit | -128 to 127 |
| `i16` | 16-bit | -32,768 to 32,767 |
| `i32` | 32-bit | -2,147,483,648 to 2,147,483,647 |
| `i64` | 64-bit | very large |
| `i128` | 128-bit | extremely large |
| `isize` | pointer-sized | depends on CPU architecture |
| `u8` | 8-bit | 0 to 255 |
| `u16` | 16-bit | 0 to 65,535 |
| `u32` | 32-bit | 0 to 4,294,967,295 |
| `u64` | 64-bit | very large |
| `u128` | 128-bit | extremely large |
| `usize` | pointer-sized | depends on CPU architecture |

- `i` = signed (can be negative), `u` = unsigned (always positive or zero)
- **Default integer type is `i32`** — this is what Rust uses when you don't specify

```rust
let a = 42;          // i32 (default)
let b: i64 = 42;     // explicitly i64
let c: u8 = 255;     // u8, max value
```

**`isize` / `usize`**: Size depends on whether you're on a 32-bit or 64-bit system. Mostly used for indexing arrays and collections.

```rust
let index: usize = 0;  // used to index into a Vec or array
```

---

### 2. Floats

Numbers with a decimal point. Rust has two float types:

| Type | Size | Precision |
|------|------|-----------|
| `f32` | 32-bit | ~7 decimal digits |
| `f64` | 64-bit | ~15 decimal digits |

- **Default float type is `f64`** — more precise, and on modern CPUs just as fast as `f32`

```rust
let x = 3.14;        // f64 (default)
let y: f32 = 3.14;   // explicitly f32
```

---

### 3. Booleans

Either `true` or `false`. Type is `bool`.

```rust
let is_active = true;
let is_done: bool = false;
```

Used in `if` conditions and loops.

---

### 4. Characters

A single Unicode character. Written with **single quotes**. Type is `char`.

```rust
let letter = 'A';
let emoji = '😊';    // valid! Rust char is full Unicode (4 bytes)
```

Note: `char` uses single quotes `'A'`, while `String`/`str` uses double quotes `"hello"`. Don't mix them up.

---

## Compound Types

Compound types group multiple values into one type.

---

### 5. Tuples

A fixed-size collection of values of **different types**.

```rust
let point = (10, 20);           // (i32, i32)
let mixed = (42, 3.14, true);   // (i32, f64, bool)
```

Access elements by index using a dot:

```rust
let x = point.0;  // 10
let y = point.1;  // 20
```

You can also destructure a tuple:

```rust
let (x, y) = point;
println!("{} {}", x, y);  // 10 20
```

Tuples are useful for returning multiple values from a function.

---

### 6. Arrays

A fixed-size collection of values of the **same type**. Size is known at compile time.

```rust
let nums = [1, 2, 3, 4, 5];   // [i32; 5]
let zeros = [0; 3];            // [0, 0, 0] — repeat 0 three times
```

Access elements by index:

```rust
let first = nums[0];  // 1
let third = nums[2];  // 3
```

Type annotation format: `[type; length]`

```rust
let nums: [i32; 5] = [1, 2, 3, 4, 5];
```

**Array vs Vec**: Arrays have a fixed size known at compile time. If you need a growable list, use `Vec<T>` (covered later).

---

## Type Inference

Rust can usually figure out the type from context — you don't need to annotate everything:

```rust
let x = 5;        // Rust infers i32
let y = 3.14;     // Rust infers f64
let z = true;     // Rust infers bool
```

But sometimes you need to be explicit, especially when the default type doesn't fit:

```rust
let big: i64 = 10_000_000_000;  // too big for i32
let byte: u8 = 200;
```

---

## Type Casting

Rust does **not** do implicit type conversion. You must cast explicitly using `as`:

```rust
let x: i32 = 42;
let y = x as f64;   // cast i32 to f64
let z = x as i64;   // cast i32 to i64
```

This is intentional — Rust wants you to be explicit about conversions to avoid subtle bugs.

---

## Numeric Literals — Readability Tricks

You can use underscores `_` as visual separators in numbers:

```rust
let million = 1_000_000;
let hex = 0xFF;          // hexadecimal
let binary = 0b1010;     // binary
let octal = 0o77;        // octal
```

---

## Quick Reference

| Type | Example | Default? |
|------|---------|----------|
| `i32` | `let x = 42;` | Yes (integers) |
| `f64` | `let x = 3.14;` | Yes (floats) |
| `bool` | `let x = true;` | — |
| `char` | `let x = 'A';` | — |
| tuple | `let x = (1, 2.0);` | — |
| array | `let x = [1, 2, 3];` | — |
