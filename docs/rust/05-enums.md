# Enums in Rust

## What is an Enum?

In most languages, an enum is a type with a limited set of **values**:

```python
# Python — limited fixed values
class Direction(Enum):
    NORTH = 1  # fixed value
    SOUTH = 2  # fixed value
```

In Rust, an enum is a type with a limited set of **states** — and each state can carry its own data:

```rust
// Rust — limited states, each state carries its own data
enum Shape {
    Circle(f64),         // state: Circle, data: any f64
    Rectangle(f64, f64), // state: Rectangle, data: any two f64s
    Triangle,            // state: Triangle, no data
}
```

- The **states** are limited and fixed — only `Circle`, `Rectangle`, `Triangle`
- The **data inside each state** can be any valid value of that type

This is formally called a **sum type** or **tagged union** — a concept from functional programming languages like Haskell and OCaml that Rust brought into systems programming.

---

## Basic Enum (no data, like other languages)

```rust
enum Direction {
    North,
    South,
    East,
    West,
}

let dir = Direction::North;
```

---

## Enum Carrying Data

Each variant can hold **different types and amounts of data**:

```rust
enum Shape {
    Circle(f64),           // holds one f64 (radius)
    Rectangle(f64, f64),   // holds two f64s (width, height)
    Triangle,              // holds nothing
}

let c = Shape::Circle(3.14);
let r = Shape::Rectangle(10.0, 5.0);
let t = Shape::Triangle;
```

Breaking down `let c = Shape::Circle(3.14)`:
- `c` — a variable
- type is `Shape` — the enum type
- current state is `Circle` — one of the three possible states
- carries the value `3.14` (f64) — the data inside this state

A variable can only be in **one state at a time** — `c` cannot be `Circle` and `Rectangle` simultaneously. Both `c` and `r` are the same type (`Shape`), but different states with different data.

---

## Using match with Enums

`match` is the primary way to work with enums — it forces you to handle every variant:

```rust
let shape = Shape::Circle(3.14);

match shape {
    Shape::Circle(radius)      => println!("circle with radius {}", radius),
    Shape::Rectangle(w, h)     => println!("rectangle {}x{}", w, h),
    Shape::Triangle            => println!("triangle"),
}
```

The compiler will not compile if you miss a variant — exhaustive checking.

---

## Real Example: Result

`Result` is just a built-in enum:

```rust
enum Result<T, E> {
    Ok(T),   // success, carries a value of type T
    Err(E),  // failure, carries an error of type E
}
```

`T` and `E` are **generic type parameters** — they can be any type. This makes `Result` reusable for any success/failure scenario.

---

## Real Example: Option

`Option` is another built-in enum — represents a value that may or may not exist:

```rust
enum Option<T> {
    Some(T),  // value exists, carries it
    None,     // value does not exist
}
```

Replaces `null`/`None` from other languages, but safely — the compiler forces you to handle the `None` case.

---

## Enum with Struct-like Variants

Variants can also hold named fields like a struct:

```rust
enum Message {
    Quit,                        // no data
    Move { x: i32, y: i32 },    // named fields
    Write(String),               // unnamed field
    Color(u8, u8, u8),           // multiple unnamed fields
}
```

---

## impl on Enums

Just like structs, you can add methods to enums with `impl`:

```rust
impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r)       => 3.14159 * r * r,
            Shape::Rectangle(w, h) => w * h,
            Shape::Triangle        => 0.0,  // simplified
        }
    }
}

let c = Shape::Circle(5.0);
println!("area: {}", c.area());
```

---

## if let — match one variant only

When you only care about one variant, `if let` is shorter than a full `match`:

```rust
let shape = Shape::Circle(3.14);

// full match — verbose when you only care about one case
match shape {
    Shape::Circle(r) => println!("radius: {}", r),
    _ => {}  // _ is a catch-all, ignore everything else
}

// if let — shorter
if let Shape::Circle(r) = shape {
    println!("radius: {}", r);
}
```

`_` in match is a **wildcard** — matches anything, used to ignore remaining variants.

---

## Enums vs Structs

| | Struct | Enum |
|---|---|---|
| Represents | One thing with multiple fields | One of several possible variants |
| Example | A user (name + age + email) | A shape (circle OR rectangle OR triangle) |
| Data | Always has all fields | Each variant has its own data |

Use **struct** when something always has the same fields.
Use **enum** when something can be one of several different forms.

---

## Comparison to Other Languages

| | Python | Java | Rust |
|---|---|---|---|
| Basic enum | `class Color(Enum)` | `enum Color` | `enum Color` |
| Variants with data | Not built-in (use dataclasses) | Not supported | Built-in |
| Null safety | No (`None` can appear anywhere) | No (`null` can appear anywhere) | Yes (`Option<T>` forces handling) |

---

## Summary

```
enum MyEnum {
    VariantA,              // no data
    VariantB(T),           // unnamed data
    VariantC { x: T }      // named data (struct-like)
}

// use match to handle all variants
match value {
    MyEnum::VariantA      => { ... }
    MyEnum::VariantB(v)   => { ... }
    MyEnum::VariantC { x } => { ... }
}

// use if let for one variant
if let MyEnum::VariantB(v) = value {
    ...
}
```

Rust's enums are one of its most powerful features — `Result` and `Option` are just two examples of how useful they are.
