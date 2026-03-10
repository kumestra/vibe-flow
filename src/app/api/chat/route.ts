import OpenAI from "openai";

const client = new OpenAI();

export async function POST(request: Request) {
  const { messages } = await request.json();

  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages,
  });

  const reply = response.choices[0].message.content;

  return Response.json({ role: "assistant", content: reply });
}
