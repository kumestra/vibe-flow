use reqwest;

#[tokio::main]
async fn main() {
    let base_url = "http://localhost:8080";

    // Send GET request to /
    println!("--- GET / ---");
    let response = reqwest::get(format!("{}/", base_url)).await.unwrap();
    println!("Status: {}", response.status());
    let body = response.text().await.unwrap();
    println!("Body: {}", body);

    // Send GET request to /hello
    println!("\n--- GET /hello ---");
    let response = reqwest::get(format!("{}/hello", base_url)).await.unwrap();
    println!("Status: {}", response.status());
    let body = response.text().await.unwrap();
    println!("Body: {}", body);
}
