# Grokonify - Wikipedia Article AI Transformer

Python script to transform Wikipedia articles using AI. Fetches French Wikipedia articles and processes them through an OpenAI-compatible GPT completion endpoint using a custom prompt template.

## Features

- Converts article titles to Wikipedia slugs automatically
- Fetches Wikipedia articles using `fetch_wikipedia.py`
- Loads customizable prompt templates with variable substitution
- Supports custom OpenAI-compatible API endpoints
- Configurable model selection via environment variables
- Outputs the AI-generated transformation to stdout
- Quiet by default (use `-v` for progress messages)
- Clean output for easy piping and redirection

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file in the generator directory with your API configuration:

```bash
LLM_API_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4
```

## Usage

```bash
python grokonify.py [-v|--verbose] <article_title>
```

### Options

- `-v, --verbose`: Enable verbose output to show progress messages (sent to stderr)

### Example

```bash
# Transform a French onion soup article (quiet mode)
python grokonify.py "Soupe à l'oignon"

# Save the result to a file
python grokonify.py "Soupe à l'oignon" > grokonified_soupe.md

# Use verbose mode to see progress
python grokonify.py -v "Python (langage)" > grokonified_python.md

# Get help
python grokonify.py --help
```

### Article Titles

You can provide article titles in natural language format:
- Script automatically converts spaces to underscores
- Handles special characters and accents
- URL-encodes when necessary

Examples:
- `"Soupe à l'oignon"` → `Soupe_à_l'oignon`
- `"Python (langage)"` → `Python_(langage)`

## Configuration

### Environment Variables

Create a `.env` file in the same directory as the script:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_URL` | Yes | - | Base URL for the API endpoint (e.g., `https://api.openai.com/v1`) |
| `LLM_API_KEY` | Yes | - | API authentication key |
| `LLM_MODEL` | No | `gpt-4` | Model name to use for completions |

### Prompt Template

Edit `PROMPT.txt` to customize how articles are transformed. Use the `{{ article }}` placeholder where you want the Wikipedia article content to be inserted.

## Output

The script outputs the AI-generated result to stdout. By default, the script runs quietly with no progress messages. Use the `-v` or `--verbose` flag to see progress updates. Error messages are always sent to stderr.

## Custom API Endpoints

This script uses the official OpenAI Python library and works with any OpenAI-compatible API endpoint. Popular alternatives include:
- OpenAI API: `https://api.openai.com/v1`
- Azure OpenAI: Configure via the OpenAI library's Azure support
- Local models via LM Studio, Ollama, or similar (use their base URL)

## Error Handling

The script provides clear error messages for common issues:
- Missing or invalid article titles
- Wikipedia article not found
- Missing environment variables
- API connection errors
- Invalid API responses

All errors are sent to stderr with appropriate exit codes.
