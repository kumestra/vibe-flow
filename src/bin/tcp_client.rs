use std::net::TcpStream;
use vibe_flow::{read_message, write_message};

fn main() {
    // Connect to the server.
    let mut stream = TcpStream::connect("127.0.0.1:8080").unwrap();
    println!("Connected to server.");

    // Send a message.
    write_message(&mut stream, "hello from client!").unwrap();
    println!("Sent: hello from client!");

    // Read the server's reply.
    match read_message(&mut stream) {
        Ok(Some(reply)) => println!("Received: {}", reply),
        Ok(None)        => println!("Server closed connection."),
        Err(e)          => println!("Error: {}", e),
    }

    // Send graceful close signal.
    write_message(&mut stream, "").unwrap();
    println!("Sent close signal. Goodbye.");
}
