use axum::{Router, routing::get};

// #[tokio::main] starts the Tokio async runtime.
// Without this, async fn main() won't work — Rust has no built-in async runtime.
#[tokio::main]
async fn main() {
    // Define routes: attach handler functions to paths and HTTP methods.
    let app = Router::new()
        .route("/", get(root_handler))
        .route("/hello", get(hello_handler));

    // Bind a TCP listener on port 8080 (Tokio's async version of TcpListener).
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    println!("HTTP server listening on http://localhost:8080");

    // Hand the listener to axum — it takes over and handles all HTTP from here.
    // axum handles: parsing requests, routing, calling handlers, sending responses.
    axum::serve(listener, app).await.unwrap();
}

// Handler functions return anything that implements IntoResponse.
// &'static str (string literal) is the simplest — axum sends it as plain text 200 OK.
async fn root_handler() -> &'static str {
    "Welcome to the Rust HTTP server!"
}

async fn hello_handler() -> &'static str {
    "Hello from axum!"
}
