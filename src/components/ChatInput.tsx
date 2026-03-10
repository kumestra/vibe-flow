type Props = {
  input: string;
  onChange: (value: string) => void;
  onSubmit: (e: { preventDefault(): void }) => void;
};

export default function ChatInput(props: Props) {
  return (
    <form onSubmit={props.onSubmit} className="flex gap-2">
      <input
        type="text"
        value={props.input}
        onChange={(e) => props.onChange(e.target.value)}
        placeholder="Type a message..."
        className="flex-1 border rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="bg-blue-500 text-white rounded-lg px-4 py-2 hover:bg-blue-600"
      >
        Send
      </button>
    </form>
  );
}
