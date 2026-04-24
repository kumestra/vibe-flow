fn main() {
    dotenvy::dotenv().ok();
    let app_name = std::env::var("APP_NAME").unwrap_or_else(|_| "vibe-flow".to_string());
    let api_key = std::env::var("OPENROUTER_API_KEY").expect("OPENROUTER_API_KEY not set");
    println!("App: {app_name}");
    println!("OPENROUTER_API_KEY loaded ({} chars)", api_key.len());
}
