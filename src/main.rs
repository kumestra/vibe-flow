fn main() {
    // =========================================================
    // INTEGERS
    // Signed (i) = can be negative. Unsigned (u) = zero or positive only.
    // Default integer type is i32.
    // =========================================================
    let a: i8 = -128;       // smallest signed 8-bit integer
    let b: u8 = 255;        // largest unsigned 8-bit integer
    let c: i32 = 1_000_000; // underscores make large numbers readable
    let d: i64 = 9_000_000_000;
    let e = 42;             // no annotation — Rust infers i32 by default

    println!("--- Integers ---");
    println!("i8:  {}", a);
    println!("u8:  {}", b);
    println!("i32: {}", c);
    println!("i64: {}", d);
    println!("inferred i32: {}", e);

    // =========================================================
    // FLOATS
    // f32 = 32-bit (less precise), f64 = 64-bit (more precise).
    // Default float type is f64.
    // =========================================================
    let f: f32 = 3.14;
    let g: f64 = 3.141592653589793;
    let h = 2.718; // Rust infers f64 by default

    println!("\n--- Floats ---");
    println!("f32: {}", f);
    println!("f64: {}", g);
    println!("inferred f64: {}", h);

    // =========================================================
    // BOOLEANS
    // Only two possible values: true or false. Type is bool.
    // =========================================================
    let is_running = true;
    let is_done: bool = false;

    println!("\n--- Booleans ---");
    println!("is_running: {}", is_running);
    println!("is_done: {}", is_done);

    // =========================================================
    // CHARACTERS
    // A single Unicode character. Written with SINGLE quotes.
    // 4 bytes — supports emoji and non-ASCII characters.
    // Note: "hello" (string) uses double quotes, 'A' (char) uses single quotes.
    // =========================================================
    let letter: char = 'A';
    let symbol = '€';
    let emoji = '🦀'; // Rust's mascot, Ferris the crab

    println!("\n--- Characters ---");
    println!("letter: {}", letter);
    println!("symbol: {}", symbol);
    println!("emoji:  {}", emoji);

    // =========================================================
    // TYPE CASTING
    // Rust does NOT auto-convert types. You must cast explicitly with `as`.
    // =========================================================
    let int_val: i32 = 42;
    let float_val = int_val as f64; // cast i32 → f64
    let small = float_val as u8;    // cast f64 → u8 (decimal part is dropped)

    println!("\n--- Type Casting ---");
    println!("i32 value: {}", int_val);
    println!("cast to f64: {}", float_val);
    println!("cast to u8: {}", small);

    // =========================================================
    // TUPLES
    // Fixed-size collection of values of DIFFERENT types.
    // Access elements with .0, .1, .2 ...
    // Useful for returning multiple values from a function.
    // =========================================================
    let point = (10, 20);
    let mixed = (42, 3.14, true, 'Z');

    println!("\n--- Tuples ---");
    println!("point: ({}, {})", point.0, point.1);
    println!("mixed.0 (i32):  {}", mixed.0);
    println!("mixed.1 (f64):  {}", mixed.1);
    println!("mixed.2 (bool): {}", mixed.2);
    println!("mixed.3 (char): {}", mixed.3);

    // Destructuring: unpack a tuple into individual variables
    let (x, y) = point;
    println!("destructured: x={}, y={}", x, y);

    // =========================================================
    // ARRAYS
    // Fixed-size collection of values of the SAME type.
    // Size must be known at compile time.
    // Use Vec<T> instead if you need a growable list.
    // =========================================================
    let nums = [1, 2, 3, 4, 5];       // [i32; 5]
    let zeros = [0; 4];               // shorthand: [value; count] = [0, 0, 0, 0]
    let floats: [f64; 3] = [1.1, 2.2, 3.3];

    println!("\n--- Arrays ---");
    println!("nums[0]: {}", nums[0]);
    println!("nums[4]: {}", nums[4]);
    println!("zeros: {:?}", zeros);    // {:?} prints the whole array (debug format)
    println!("floats: {:?}", floats);
    println!("array length: {}", nums.len());
}
