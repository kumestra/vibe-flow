#[tokio::main]
async fn main() {
    dotenvy::dotenv().ok();
    let api_key = std::env::var("OPENROUTER_API_KEY").expect("OPENROUTER_API_KEY not set");

    let client = reqwest::Client::new();
    let res = client
        .post("https://openrouter.ai/api/v1/chat/completions")
        .header("Authorization", format!("Bearer {api_key}"))
        .json(&serde_json::json!({
            "model": "openai/gpt-4o-mini",
            "messages": [
                { "role": "user", "content": "Say hello in one sentence." }
            ]
        }))
        .send()
        .await
        .expect("request failed");

    let body: serde_json::Value = res.json().await.expect("failed to parse response");
    let reply = &body["choices"][0]["message"]["content"];
    println!("{reply}");
}
