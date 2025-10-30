# Friday - Gemini API Client

A simple Python CLI tool to interact with Google's Gemini API and generate text content from user prompts.

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

3. Set your Gemini API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

## Usage

Run the script with your prompt as command line arguments:

```bash
uv run main.py "What is the meaning of life?"
```

The script will:
- Send your prompt to the Gemini API
- Return the generated response formatted as Markdown
- Display it in your terminal with rich text formatting

## Error Handling

- If the `GEMINI_API_KEY` environment variable is not set, the script will exit with an error message.
- If no prompt is provided, usage instructions will be displayed.
- API errors and invalid responses are handled gracefully with informative error messages.

## Dependencies

- requests: For making HTTP requests
- rich: For terminal formatting and Markdown rendering

## Alias (Optional)

For convenience, you can create a shell alias to run the script easily from anywhere:

```bash
alias friday='uv --directory <repo_full_path>/friday run main.py '
```

Add this line to your `~/.bashrc` or `~/.zshrc` to make the alias persistent.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
