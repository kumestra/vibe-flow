"use client";

import { useState } from "react";
import MessageList from "@/components/MessageList";
import ChatInput from "@/components/ChatInput";
import type { Message } from "@/types/chat";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");

    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: newMessages }),
    });

    const reply = await response.json();
    setMessages([...newMessages, reply]);
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <MessageList messages={messages} />

      <ChatInput
        input={input}
        onChange={setInput}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
