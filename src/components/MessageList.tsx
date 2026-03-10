import type { Message } from "@/types/chat";

type Props = {
  messages: Message[];
};

export default function MessageList(props: Props) {
  const messages = props.messages;
  return (
    // flex-1: take up all remaining vertical space
    // overflow-y-auto: show scrollbar when messages overflow
    // space-y-4: vertical gap (1rem) between each message
    // py-4: padding top and bottom (1rem)
    <div className="flex-1 overflow-y-auto space-y-4 py-4">
      {messages.map((message, index) => (
        // flex: use flexbox
        // justify-end: push user messages to the RIGHT
        // justify-start: push bot messages to the LEFT
        <div
          key={index}
          className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            // rounded-lg: rounded corners
            // px-4: padding left and right (1rem)
            // py-2: padding top and bottom (0.5rem)
            // max-w-sm: max width 24rem, prevents bubble stretching full width
            // bg-blue-500 text-white: user bubble (blue background, white text)
            // bg-gray-200 text-black: bot bubble (gray background, black text)
            className={`rounded-lg px-4 py-2 max-w-sm ${
              message.role === "user"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-black"
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
    </div>
  );
}
