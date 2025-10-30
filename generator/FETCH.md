# Wikipedia Article Fetcher

Python script to fetch French Wikipedia articles and convert them to clean markdown.

## Features

- Fetches articles using Wikipedia REST API
- Strips unwanted content (infoboxes, tables, images, navigation, references)
- Converts to clean markdown with:
  - Headers (h1-h6)
  - Bold and italic formatting
  - Lists (ordered and unordered)
  - Text from links (without the link markup)
- Cleans repetitive line breaks and empty list items

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python fetch_wikipedia.py <page_title>
```

### Example

```bash
# Fetch the Python programming language article
python fetch_wikipedia.py "Python_(langage)"

# Save to a file
python fetch_wikipedia.py "Python_(langage)" > python.md
```

### Finding Page Titles

Page titles are the same as in the Wikipedia URL. For example:
- URL: `https://fr.wikipedia.org/wiki/Python_(langage)`
- Title: `Python_(langage)`

## Output

The script outputs clean markdown to stdout. Progress messages are sent to stderr.
