# Friday - Gemini API Client

A simple Python CLI tool to interact with Google's Gemini API and generate text
content from user prompts. Answers stream to your terminal as Markdown, tuned to
behave as a concise assistant for sysadmin/DevOps work.

## Features

- **Streaming output** — the answer renders live as Markdown while it arrives.
- **Model fallback** — if the primary model is unavailable (429/5xx "high
  demand"), it retries with exponential backoff, then falls back to a stable
  model.
- **Configurable thinking** — `off` (fastest, ~15x), `low`, or `high`.
- **Sysadmin-tuned system prompt** — command(s) first, short explanation only if
  needed.
- **Env-based config** — everything configurable via environment variables or a
  `.env` file.

## Prerequisites

- Python 3.13 or higher
- `uv` package manager (for dependency management)
- A Google Gemini API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/edupr91/friday.git
   cd friday
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

3. Configure your API key. Either set it in the environment:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   or copy the sample config and fill it in:
   ```bash
   cp env.dist .env
   # edit .env and set GEMINI_API_KEY
   ```

## Usage

Run the script with your prompt as command line arguments:

```bash
uv run main.py "How do I tail the last 100 lines of a log and follow it?"
```

The answer streams into your terminal, formatted as Markdown.

For a harder question, bump the model and thinking level for a single run:

```bash
GEMINI_MODEL=gemini-3-flash-preview GEMINI_THINKING=high uv run main.py "..."
```

## Configuration

All settings are read from environment variables (or a `.env` file). Defaults are
shown in `env.dist`.

| Variable                 | Default                  | Description                                             |
| ------------------------ | ------------------------ | ------------------------------------------------------- |
| `GEMINI_API_KEY`         | *(required)*             | Google Generative Language (Gemini) API key.            |
| `GEMINI_MODEL`           | `gemini-2.5-flash`       | Primary model.                                          |
| `GEMINI_FALLBACK_MODEL`  | `gemini-2.5-flash-lite`  | Model used after repeated 429/5xx errors.               |
| `GEMINI_THINKING`        | `off`                    | Thinking mode: `off` \| `low` \| `high`.                |
| `GEMINI_MAX_TOKENS`      | `1024`                   | Max tokens in the generated answer.                     |
| `GEMINI_MAX_RETRIES`     | `3`                      | Retries (exponential backoff) on transient 429/503.     |

> Note: `gemini-3` models can't fully disable thinking, so `off` and `low` behave
> the same for them; `thinkingLevel` is used instead of `thinkingBudget`.

## Error Handling

- If the `GEMINI_API_KEY` environment variable is not set, the script exits with
  an error message.
- If no prompt is provided, usage instructions are displayed.
- Transient errors (429/500/502/503/504) are retried with exponential backoff,
  then fall back to the secondary model before giving up.
- Other API errors and invalid responses are handled gracefully with informative
  messages.

## Dependencies

- requests: For making HTTP requests
- rich: For terminal formatting, live streaming, and Markdown rendering

## Alias (Optional)

For convenience, you can create a shell alias to run the script easily from anywhere:

```bash
alias friday='uv --directory <repo_full_path>/friday run main.py '
```

Add this line to your `~/.bashrc` or `~/.zshrc` to make the alias persistent.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
