use std::io::Write;
use std::net::TcpStream;

// Encodes a string message and writes it to the TCP stream.
// Format: 4 bytes (length, big-endian u32) + N bytes (UTF-8 payload)
// A zero-length message (empty string) signals graceful close.
pub fn write_message(stream: &mut TcpStream, text: &str) -> std::io::Result<()> {
    let payload = text.as_bytes();
    let length = payload.len() as u32;

    // Convert the length to 4 bytes big-endian.
    // e.g. length=5 → [0x00, 0x00, 0x00, 0x05]
    let length_bytes = length.to_be_bytes();

    // Write length prefix first, then the payload.
    stream.write_all(&length_bytes)?;
    stream.write_all(payload)?;

    Ok(())
}
