# Transformer Architecture

## Step 1: API Input

When you call an LLM API, the very first input is **not a plain string** — it's a structured list of messages in JSON:

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system",    "content": "You are a helpful assistant."},
    {"role": "user",      "content": "What is a transformer?"},
    {"role": "assistant", "content": "A transformer is a neural network architecture..."},
    {"role": "user",      "content": "How does attention work?"}
  ]
}
```

Each message has:
- **`role`** — who is speaking: `system`, `user`, or `assistant`
- **`content`** — what they said

The model needs roles because context matters — the same words mean different things depending on who said them.

## Step 2: Chat Template

Before tokenization, the backend serializes the messages array into a **single flat string** using a chat template. OpenAI uses the ChatML format:

```
<|im_start|>system
You are a helpful assistant.
<|im_end|>
<|im_start|>user
What is a transformer?
<|im_end|>
<|im_start|>assistant
A transformer is a neural network architecture...
<|im_end|>
<|im_start|>user
How does attention work?
<|im_end|>
<|im_start|>assistant
```

Special tokens like `<|im_start|>` and `<|im_end|>` mark message boundaries. The final `<|im_start|>assistant` with no closing tag is a prompt — it tells the model "now it's your turn to continue from here".

Different models use different templates (Llama 3, Gemini, Claude all have their own formats), but the principle is the same: **structured JSON → flat string with special delimiter tokens**.

## Step 3: Tokenization

The flat string is now a sequence of Unicode characters. Tokenization is a two-step process: **split** then **map to IDs**.

### Step 3a: Split

The string is split into chunks using **BPE (Byte Pair Encoding)**. Special tokens are matched first and never broken apart. Normal text is split into subword pieces:

```
"<|im_start|>system\nYou are"
        ↓  split
["<|im_start|>", "system", "\n", "You", " are"]
```

BPE starts with individual bytes and repeatedly merges the most frequent adjacent pairs during training. Common words get their own token; rare words get split:

```
"transformer"  → ["transform", "er"]
"tokenization" → ["token", "ization"]
"ChatGPT"      → ["Chat", "G", "PT"]
```

### Step 3b: Map to IDs

Each chunk is looked up in a vocabulary dictionary and replaced with an integer:

```
["<|im_start|>", "system", "\n", "You", " are"]
        ↓  map to IDs
[100264, 9125, 198, 2675, 527]
```

The tokenizer has a **special tokens registry** — strings that always map to a single ID and are never split by BPE:

```python
"<|im_start|>" → 100264  # "a new message starts here"
"<|im_end|>"   → 100265  # "a message ends here"
```

After this step, the entire conversation is a flat sequence of integers:

```python
[100264, 9125, 198, 2675, 527, 264, 11190, 18328, 13, 198, 100265, ...]
```

## Step 4: Embedding Lookup

The model cannot work with integers directly. Each token ID is converted to a **dense vector** via an embedding table — a learned lookup dictionary:

```python
# embedding table shape: [vocab_size, embedding_dim]
# e.g. GPT-4: [100277, 12288]

embedding_table = {
    100264: [0.12, -0.34, 0.87, ...],  # <|im_start|> → 12288 floats
      9125: [0.55,  0.21, -0.63, ...],  # "system"     → 12288 floats
       198: [-0.09, 0.44,  0.11, ...],  # "\n"         → 12288 floats
    ...
}
```

Each integer is replaced by its vector:

```
[100264,           9125,              198,             ...]
      ↓            ↓                   ↓
[0.12, -0.34, ...] [0.55, 0.21, ...]  [-0.09, 0.44, ...]
```

The result is a **matrix** of shape `[sequence_length, embedding_dim]` — a sequence of vectors. This is what flows into the transformer layers.

Two key points:
- These vectors are **learned during training**, not hand-crafted
- Similar tokens end up with similar vectors — semantic meaning is encoded in the geometry

## Step 5: Transformer Layers (overview)

The matrix flows through N stacked transformer layers (e.g. ~96 layers for GPT-4). Each layer refines the vectors. We will go deeper into this later.

## Step 6: Output — Logits → Token

After the final transformer layer, the model produces a **logits vector** — one score per token in the vocabulary:

```python
logits = [0.003, -0.12, 0.87, 0.002, -0.44, ...]  # 100,277 floats
```

**Softmax** converts logits into a probability distribution:

```python
probs = softmax(logits)
# all values between 0 and 1, sum to exactly 1.0
# e.g. probs[9125] = 0.24  → "system" has 24% chance of being next token
```

Then the model **samples** one token ID from the distribution:

```python
next_token_id = sample(probs)  # e.g. 9125 → "system"
```

The model generates **one token at a time**. The new token is appended to the sequence, and the whole forward pass runs again:

```
transformer layers
      ↓
logits [vocab_size floats]
      ↓ softmax
probabilities [vocab_size floats, sum=1]
      ↓ sample
one token ID
      ↓ append to sequence, repeat
```

This loop continues until the model samples `<|im_end|>`, signaling the end of its response.

### Context Window

The `200k` context window is a **maximum sequence length**, not a fixed input size. The input matrix is exactly as large as the actual input — no padding, no zeros:

```
1 token        → valid ✓  shape: [1, 12288]
100 tokens     → valid ✓  shape: [100, 12288]
200,000 tokens → valid ✓  shape: [200000, 12288]
200,001 tokens → error ✗  exceeds limit
```

The transformer architecture never changes — the same weights handle any sequence length. The limit exists because attention scales O(n²) in memory and compute.

### Thinking Mode

Some models (DeepSeek-R1, Claude with extended thinking) use special tokens to wrap internal reasoning before the final answer:

```
<|im_start|>assistant
<think>
Let me work through this step by step...
The user is asking about X, which means...
So the answer should be...
</think>

Here is my answer: ...
<|im_end|>
```

Key points:
- `<think>` and `</think>` are special delimiter tokens, just like `<|im_start|>`
- The model generates thinking tokens **one at a time**, same as normal text — it's the same next-token prediction loop
- The model was **fine-tuned** to use this pattern before answering
- Thinking tokens **consume context window** — long reasoning chains eat into the limit
- The API typically hides the thinking block or returns it separately

**How thinking mode is toggled — an engineering trick:**

The model learned during fine-tuning: "if I see `<think>`, I must reason until `</think>`, then answer. If I don't see `<think>`, I answer directly."

So the backend controls thinking mode purely through **assistant prefill** — injecting text at the start of the assistant turn before sending to the model:

```
# Thinking OFF (default) — no intervention, model answers naturally:
<|im_start|>assistant
↑ model generates here

# Thinking ON — backend pre-fills <think>, model is forced to continue the pattern:
<|im_start|>assistant
<think>
↑ model must continue here, generate reasoning, close </think>, then answer
```

No architecture change. No weight change. Just prompt manipulation. This is called **assistant prefill**.

The same principle applies everywhere:
- **Tool calling** — system prompt tells the model about tools; fine-tuning taught it to output tool call JSON when appropriate
- **JSON mode** — pre-fill with `{` forces the model to continue with valid JSON
- **Few-shot examples** — put examples in the prompt, model follows the pattern

> All LLM "modes" are just different inputs to the same stateless function.

**Thinking levels — also an engineering trick:**

Different thinking levels (light/deep) are controlled by a `budget_tokens` parameter. The model has no concept of levels — the backend enforces the budget by monitoring token count and injecting `</think>` when the limit is reached:

```python
# API parameter:
{"thinking": {"type": "enabled", "budget_tokens": 1000}}  # light
{"thinking": {"type": "enabled", "budget_tokens": 10000}} # deep
```

```
# What actually happens:
model generates: <think> tok tok tok tok tok ...
                                       ↑
                           backend counting tokens...
                           budget reached → inject </think>
                           model sees </think> → switches to answer mode
```

The model is just doing next-token prediction the whole time. The backend is watching, counting, and intervening.

This reveals a deeper truth — **the LLM has no self-control over its own output. The backend is always in control:**

| Behavior | How it's implemented |
|---|---|
| Max output length | Backend stops sampling after N tokens, injects `<\|im_end\|>` |
| Thinking budget | Backend injects `</think>` at the token limit |
| Thinking on/off | Backend pre-fills `<think>` or does nothing |
| JSON mode | Backend rejects invalid tokens at each step (constrained decoding) |
| Stop sequences | Backend watches for a specific string, stops when it appears |

The model is a pure function: give it tokens, it predicts the next one. All generation control lives in the backend, not the model.

**Why cut-off thinking still works — the fine-tuning reason:**

When the backend injects `</think>` mid-stream, the thinking block is incomplete. This is fine because of how the model was fine-tuned.

During fine-tuning, the model was trained on massive examples where thinking content was:
- incomplete and cut off
- contradictory and self-correcting
- going down wrong paths
- messy and unstructured

So the model learned: **"whatever is between `<think>` and `</think>`, use it as a hint, then produce the best answer I can."**

The thinking block is not a formal proof that must be complete — it's a scratchpad:

```
<think>
Let me consider option A... actually no
What about B... hmm
The key insight is X, so the answer must be...    ← budget cut off here
</think>                                           ← injected by backend
answer based on whatever reasoning existed
```

The model handles this gracefully because:
1. It was fine-tuned on messy/incomplete thinking — this is just another noisy input
2. It has no awareness of being "interrupted" — each forward pass is stateless
3. `</think>` is purely a pattern trigger — "now answer", regardless of what came before

The real tradeoff of thinking budget is **quality vs cost**:

| Budget too low | Budget too high |
|---|---|
| Reasoning cut short → potentially weaker answer | Model overthinks → slower and more expensive |
