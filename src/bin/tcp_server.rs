use std::net::TcpListener;
use vibe_flow::{read_message, write_message};

fn main() {
    // Bind a TCP listener to port 8080.
    let listener = TcpListener::bind("0.0.0.0:8080").unwrap();
    println!("TCP server listening on port 8080...");

    // Accept connections one at a time (single-thread blocking).
    for stream in listener.incoming() {
        let mut stream = stream.unwrap();
        println!("--- New connection from: {} ---", stream.peer_addr().unwrap());

        // Keep reading messages until the connection closes.
        loop {
            match read_message(&mut stream) {
                Ok(Some(text)) => {
                    // Received a normal message — print it and send a reply.
                    println!("Received: {}", text);
                    let reply = format!("server received: {}", text);
                    write_message(&mut stream, &reply).unwrap();
                }
                Ok(None) => {
                    // Received graceful close signal (length = 0).
                    println!("Client closed connection gracefully.");
                    break;
                }
                Err(e) => {
                    // Unexpected disconnect or I/O error.
                    println!("Connection error: {}", e);
                    break;
                }
            }
        }

        println!("Connection closed.\n");
    }
}
