# Result and Error Handling in Rust

## Philosophy

Rust has no exceptions. Instead, errors are **values** — returned explicitly from functions. The compiler forces you to handle them. No silent failures.

Compare:

```python
# Python — exception can be thrown anywhere, easy to forget to handle
def read_file():
    return open("file.txt").read()  # can throw, nothing forces you to handle it

read_file()  # if it throws and you don't catch, program crashes
```

```rust
// Rust — error is part of the return type, compiler forces you to handle it
fn read_file() -> Result<String, io::Error> { ... }

read_file();  // compiler warning: Result must be used
```

---

## The Result Type

```rust
enum Result<T, E> {
    Ok(T),   // success, contains a value of type T
    Err(E),  // failure, contains an error of type E
}
```

`T` and `E` are generic — they can be any type:

```rust
Result<TcpListener, io::Error>  // Ok = TcpListener, Err = io::Error
Result<String, ParseIntError>   // Ok = String,      Err = ParseIntError
Result<(), io::Error>           // Ok = nothing,     Err = io::Error
```

---

## io::Result\<T\> — Syntax Sugar

`std::io::Result<T>` is a shorthand defined in the standard library:

```rust
// this:
std::io::Result<TcpListener>

// expands to:
Result<TcpListener, std::io::Error>
```

Almost all I/O operations fail with `std::io::Error`, so the alias saves typing.

---

## 7 Ways to Handle Result

---

### 1. match — most explicit

Handle both `Ok` and `Err` manually. Most verbose but most control.

```rust
match TcpListener::bind("0.0.0.0:8080") {
    Ok(listener) => println!("listening"),
    Err(e)       => println!("failed: {}", e),
}
```

---

### 2. .unwrap() — panic on error

`unwrap()` is a method defined on the `Result` enum. Internally it is just a `match`:

```rust
impl<T, E> Result<T, E> {
    pub fn unwrap(self) -> T {
        match self {
            Ok(value) => value,          // return the value
            Err(e)    => panic!("{}", e), // crash the program
        }
    }
}
```

- If `Ok` → returns the value inside, program continues
- If `Err` → **panics** and crashes the program

```rust
Ok(42).unwrap()          // returns 42
Err("oops").unwrap()     // panics: 'called `Result::unwrap()` on an `Err` value: "oops"'
```

**Panic** is not a normal exit — it prints an error message with file and line number, then terminates with a non-zero exit code:

| | Normal exit | Panic |
|---|---|---|
| Exit code | 0 (success) | non-zero (failure) |
| Message | nothing | error message + location |
| Cause | program finished normally | unexpected error |

Use only during development and testing. Not for production code.

---

### 3. .expect("msg") — panic with custom message

Like `.unwrap()` but panics with your message — more informative when debugging.

```rust
let listener = TcpListener::bind("0.0.0.0:8080")
    .expect("failed to bind port 8080");
```

---

### 4. ? operator — propagate error to caller

If `Ok`, unwraps the value and continues. If `Err`, returns the error immediately from the current function.

Can only be used inside a function that returns `Result`.

```rust
fn parse_number(s: &str) -> Result<i32, ParseIntError> {
    let n = s.parse::<i32>()?;  // returns Err immediately if parse fails
    Ok(n * 2)
}
```

Equivalent to writing:

```rust
let n = match s.parse::<i32>() {
    Ok(n)  => n,
    Err(e) => return Err(e),
};
```

The `?` is the idiomatic Rust way to propagate errors up the call stack.

---

### 5. .unwrap_or(default) — fallback value on error

Returns the `Ok` value, or a default if `Err`.

```rust
let value = some_result.unwrap_or(0);  // use 0 if error
```

---

### 6. .unwrap_or_else(fn) — computed fallback on error

Like `.unwrap_or()` but computes the fallback with a closure. Useful when the fallback needs the error value or is expensive to compute.

```rust
let value = some_result.unwrap_or_else(|e| {
    println!("error occurred: {}", e);
    -1
});
```

---

### 7. .map() and .and_then() — transform and chain

`.map()` transforms the `Ok` value, leaves `Err` unchanged:

```rust
let doubled = Ok(21).map(|n| n * 2);  // Ok(42)
let same    = Err("oops").map(|n: i32| n * 2);  // Err("oops") — closure not called
```

`.and_then()` chains another `Result`-returning operation. If the first is `Ok`, runs the closure. If `Err`, skips the closure:

```rust
let result = parse_number("21")
    .and_then(|n| if n > 0 { Ok(n) } else { Err(...) });
```

Similar to JavaScript's `.then()` on Promises.

---

## The Option Type

Related to `Result` — used when a value may or may not exist (no error involved):

```rust
enum Option<T> {
    Some(T),  // there is a value
    None,     // there is no value
}
```

Use `Result` when something can **fail**. Use `Option` when something can be **absent**.

```rust
// Option — no error, just may not exist
fn find_user(id: u32) -> Option<User> { ... }

// Result — can fail with an error
fn load_from_db(id: u32) -> Result<User, DbError> { ... }
```

`Option` has the same handling methods as `Result`:
`.unwrap()`, `.expect()`, `.unwrap_or()`, `.map()`, `.and_then()`, etc.

---

## Combining Result and Option

Sometimes you need both — use `ok_or()` to convert `Option` into `Result`:

```rust
let maybe: Option<i32> = Some(42);
let result: Result<i32, &str> = maybe.ok_or("value was missing");
// Some(42) → Ok(42)
// None     → Err("value was missing")
```

---

## Summary

```
Result<T, E>
├── Ok(T)   → success
└── Err(E)  → failure

Option<T>
├── Some(T) → value exists
└── None    → value absent

Handling methods:
├── match              → explicit, full control
├── .unwrap()          → panic on Err/None (dev only)
├── .expect("msg")     → panic with message (dev only)
├── ?                  → propagate to caller (idiomatic)
├── .unwrap_or(v)      → fallback value
├── .unwrap_or_else(f) → computed fallback
└── .map() / .and_then() → transform and chain
```
