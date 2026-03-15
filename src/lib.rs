use std::io::{Read, Write};
use std::net::TcpStream;

// Encodes a string message and writes it to the TCP stream.
// Format: 4 bytes (length, big-endian u32) + N bytes (UTF-8 payload)
// A zero-length message (empty string) signals graceful close.
//
// Return type: std::io::Result<()>
// This is a syntax sugar for: Result<(), std::io::Error>
// Which means:
//   Ok(())            → success, nothing to return
//   Err(io::Error)    → something went wrong (e.g. broken pipe, network error)
pub fn write_message(stream: &mut TcpStream, text: &str) -> std::io::Result<()> {
    let payload = text.as_bytes();
    // payload.len() returns usize — Rust's pointer-sized integer (8 bytes on 64-bit systems),
    // used for all sizes and indices in Rust.
    // `as u32` casts it to u32 (4 bytes) to match our protocol's 4-byte length field.
    let length = payload.len() as u32;

    // Convert the length to 4 bytes big-endian.
    // e.g. length=5 → [0x00, 0x00, 0x00, 0x05]
    let length_bytes = length.to_be_bytes();

    // Write length prefix first, then the payload.
    stream.write_all(&length_bytes)?;
    stream.write_all(payload)?;

    Ok(())
}

// Reads a length-prefixed message from the TCP stream and decodes it as a string.
// Format: 4 bytes (length, big-endian u32) + N bytes (UTF-8 payload)
// Returns None if the connection was closed gracefully (length = 0).
//
// Return type: std::io::Result<Option<String>>
// This is a syntax sugar for: Result<Option<String>, std::io::Error>
// Which means:
//   Ok(Some(text))  → success, received a message
//   Ok(None)        → graceful close, length was 0
//   Err(io::Error)  → something went wrong (e.g. connection dropped)
pub fn read_message(stream: &mut TcpStream) -> std::io::Result<Option<String>> {
    // Step 1: Read exactly 4 bytes for the length field.
    // [0u8; 4] creates an array of 4 bytes, all initialized to 0.
    let mut length_bytes = [0u8; 4];
    stream.read_exact(&mut length_bytes)?;

    // Convert the 4 bytes back to a u32 big-endian number.
    // e.g. [0x00, 0x00, 0x00, 0x05] → 5
    let length = u32::from_be_bytes(length_bytes);

    // A zero-length message is the graceful close signal.
    if length == 0 {
        return Ok(None);
    }

    // Step 2: Read exactly N bytes for the payload.
    // vec![0u8; length as usize] creates a Vec of `length` bytes, all initialized to 0.
    // We cast length back to usize because Vec sizing uses usize.
    let mut payload = vec![0u8; length as usize];
    stream.read_exact(&mut payload)?;

    // Decode the payload bytes as a UTF-8 string.
    // from_utf8 returns an error if the bytes are not valid UTF-8.
    // map_err converts the UTF-8 error into an io::Error so we can use ? on it.
    let text = String::from_utf8(payload)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;

    Ok(Some(text))
}
