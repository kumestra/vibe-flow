# Codex CLI Models Comparison

As of April 6, 2026, the local Codex CLI cache on this machine lists these
models as selectable:

- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.3-codex`
- `gpt-5.2-codex`
- `gpt-5.2`
- `gpt-5.1-codex-max`
- `gpt-5.1-codex`
- `gpt-5.1`
- `gpt-5-codex`
- `gpt-5`
- `gpt-5.1-codex-mini`
- `gpt-5-codex-mini`

## Current Documented Models

These models have current public documentation with published pricing.

| Model | Positioning / ability | Input price | Output price | Official context window |
|---|---|---:|---:|---:|
| `gpt-5.4` | Best overall quality for coding and agentic work | $2.50 / 1M | $15.00 / 1M | 1,050,000 |
| `gpt-5.4-mini` | Strong mini model with better speed and cost | $0.75 / 1M | $4.50 / 1M | 400,000 |
| `gpt-5.1` | Previous flagship for coding and agentic tasks | $1.25 / 1M | $10.00 / 1M | 400,000 |
| `gpt-5` | Older previous reasoning and coding model | $1.25 / 1M | $10.00 / 1M | 400,000 |
| `gpt-5.1-codex` | Codex-optimized GPT-5.1 | $1.25 / 1M | $10.00 / 1M | 400,000 |
| `gpt-5-codex` | Codex-optimized GPT-5 | $1.25 / 1M | $10.00 / 1M | 400,000 |
| `gpt-5.1-codex-mini` | Cheaper and faster Codex model | $0.25 / 1M | $2.00 / 1M | 400,000 |

## CLI-Listed Models Without A Clear Current Public Pricing Page

For these, the local Codex CLI cache provides the model description and effective
CLI context window, but there is no clearly corresponding current public pricing
page cited here.

| Model | Codex CLI description | Local CLI context window |
|---|---|---:|
| `gpt-5.3-codex` | Frontier Codex-optimized agentic coding model. | 272,000 |
| `gpt-5.2-codex` | Frontier agentic coding model. | 272,000 |
| `gpt-5.2` | Optimized for professional work and long-running agents | 272,000 |
| `gpt-5.1-codex-max` | Codex-optimized model for deep and fast reasoning. | 272,000 |
| `gpt-5-codex-mini` | Optimized for codex. Cheaper, faster, but less capable. | 272,000 |

## Important Caveat

The local Codex CLI cache reports a `272000` context window for all models in
this install. Official API model pages list larger public context windows for
several models.

The safest interpretation is:

- API docs show the model's published maximum context window.
- Codex CLI cache shows the effective context window currently used by this
  Codex client.

## Practical Recommendations

- Best quality: `gpt-5.4`
- Best value: `gpt-5.4-mini`
- Best cheap coding option: `gpt-5.1-codex-mini`
- Use legacy or CLI-only aliases only if you specifically want older behavior

## Local Data Used

- Local cache file: `~/.codex/models_cache.json`
- Local cache fetched at: `2026-04-06T05:45:45Z`
- Local Codex CLI client version: `0.118.0`

## Sources

- https://developers.openai.com/api/docs/models/compare
- https://developers.openai.com/api/docs/models/gpt-5.4
- https://developers.openai.com/api/docs/models/gpt-5.4-mini
- https://developers.openai.com/api/docs/models/gpt-5.1
- https://developers.openai.com/api/docs/models/gpt-5
- https://developers.openai.com/api/docs/models/gpt-5.1-codex
- https://developers.openai.com/api/docs/models/gpt-5-codex
- https://developers.openai.com/api/docs/models/gpt-5.1-codex-mini
