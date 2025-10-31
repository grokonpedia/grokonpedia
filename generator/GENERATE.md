# Generate - Automated Hugo Article Creation

`generate.py` is an automation script that streamlines the process of creating Hugo articles from Wikipedia content using the Grokonify transformation pipeline.

## Overview

This script automates the entire workflow:
1. Takes a Wikipedia article title as input
2. Calls `grokonify.py` to fetch and transform the article
3. Converts the title to a Hugo-compatible slug
4. Creates a new Hugo content file
5. Populates it with the transformed content

## Prerequisites

- Python 3.7+
- Hugo installed and available in PATH
- All dependencies from `grokonify.py` (see main README)
- Proper `.env` configuration with LLM API credentials

## Installation

No additional dependencies beyond those required by `grokonify.py`:
- `openai`
- `python-dotenv`

## Usage

### Basic Usage

```bash
./generator/generate.py "Article Title"
```

### With Verbose Output

```bash
./generator/generate.py "Article Title" -v
```

### Examples

Generate an article about French Onion Soup:
```bash
./generator/generate.py "Soupe à l'oignon"
```

Generate an article about the Eiffel Tower with verbose output:
```bash
./generator/generate.py "Eiffel Tower" -v
```

Generate an article with special characters:
```bash
./generator/generate.py "Café au lait"
```

## How It Works

### 1. Title to Slug Conversion

The script converts Wikipedia article titles to Wikipedia-style slugs:
- Replaces spaces with underscores
- Preserves case and special characters (like Wikipedia URLs)

**Examples:**
- `"Soupe à l'oignon"` → `"Soupe_à_l'oignon"`
- `"French Revolution"` → `"French_Revolution"`
- `"Café au lait"` → `"Café_au_lait"`

### 2. Grokonify Processing

Calls `grokonify.py` with the article title:
- Fetches Wikipedia content
- Transforms it using the AI prompt
- Returns the transformed content

**Note:** This step can take several minutes depending on the article length and API response time.

### 3. Hugo Article Creation

Creates the Hugo content file:
- Runs `hugo new content {slug}.md` from the project root
- Hugo automatically generates frontmatter (title, date, draft status)
- Appends the transformed content to the file

### 4. File Output

The final file is created at:
```
content/{slug}.md
```

With structure:
```markdown
+++
date = '2025-10-31T...'
draft = false
title = "Article Title"
+++

[Transformed content from Grokonify]
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `article_title` | - | Wikipedia article title (required) |
| `--verbose` | `-v` | Enable verbose output to see progress |

## Error Handling

The script handles several error cases:

- **Missing dependencies**: Will fail with import error if required packages aren't installed
- **Grokonify errors**: If article fetching or transformation fails, error is displayed
- **Hugo errors**: If Hugo command fails, stderr is shown
- **File write errors**: If content can't be written, error is displayed

## Workflow Integration

### Typical Workflow

1. Choose a Wikipedia article
2. Run generate.py with the article title
3. Wait for processing (can take a few minutes)
4. Review the created file in `content/`
5. Run Hugo to preview: `hugo server`
6. Edit if needed, then publish

### Batch Processing

For multiple articles, you can create a simple bash script:

```bash
#!/bin/bash
articles=(
    "Soupe à l'oignon"
    "Eiffel Tower"
    "French Revolution"
)

for article in "${articles[@]}"; do
    ./generator/generate.py "$article"
    echo "Waiting before next article..."
    sleep 5
done
```

## File Structure

```
generator/
├── generate.py          # This script
├── grokonify.py         # AI transformation script
├── fetch_wikipedia.py   # Wikipedia fetcher
├── PROMPT.txt           # AI prompt template
├── GENERATE.md          # This documentation
└── .env                 # API credentials (not in git)

content/
└── {slug}.md           # Generated Hugo articles
```

## Troubleshooting

### Hugo command not found
Ensure Hugo is installed and in your PATH:
```bash
hugo version
```

### API errors
Check your `.env` file has correct credentials:
```bash
LLM_API_URL=your_api_url
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4
```

### Article not found
Verify the Wikipedia article exists and the title is correct. Check Wikipedia directly first.

### Permission denied
Make the script executable:
```bash
chmod +x generator/generate.py
```

## Advanced Usage

### Custom Hugo Content Types

If using custom Hugo archetypes, the script will respect them:
```bash
hugo new content --kind custom {slug}.md
```

Modify the `create_hugo_article()` function to add `--kind` parameter.

### Content Review Before Publishing

Generated articles are marked as `draft = false` by default (Hugo's behavior). To review before publishing:

1. Edit Hugo's archetype to set `draft = true`
2. Review the generated content
3. Manually set `draft = false` when ready

## Performance Notes

- **Processing time**: 2-10 minutes per article depending on length and API speed
- **Rate limiting**: Be mindful of API rate limits when batch processing
- **Caching**: Consider implementing caching in grokonify.py for repeated transformations

## Contributing

To improve `generate.py`:
1. Maintain compatibility with `grokonify.py`
2. Keep the slug conversion deterministic
3. Handle Unicode properly
4. Preserve error messages for debugging

## See Also

- `grokonify.py` - The core transformation script
- `fetch_wikipedia.py` - Wikipedia content fetcher
- Hugo documentation: https://gohugo.io/
