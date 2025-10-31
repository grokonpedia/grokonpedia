#!/usr/bin/env python3
"""
Grokonify - Transform Wikipedia articles using AI

This script takes a Wikipedia article title, fetches the article content,
and processes it through an OpenAI-compatible GPT endpoint using a custom prompt.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from openai import OpenAI


# Global verbose flag
VERBOSE = False


def log(message):
    """Print message to stderr only if verbose mode is enabled."""
    if VERBOSE:
        print(message, file=sys.stderr)


def title_to_slug(title):
    """
    Convert an article title to a Wikipedia slug.

    Args:
        title: The article title (e.g., "Soupe à l'oignon")

    Returns:
        Wikipedia-compatible slug (e.g., "Soupe_à_l'oignon")
    """
    # Replace spaces with underscores
    slug = title.replace(' ', '_')

    # URL-encode the slug to handle special characters
    # Use safe='_' to keep underscores unencoded
    slug = quote(slug, safe='_')

    return slug


def fetch_article_content(slug):
    """
    Fetch Wikipedia article content using fetch_wikipedia.py

    Args:
        slug: Wikipedia article slug

    Returns:
        Article content in markdown format
    """
    script_dir = Path(__file__).parent
    fetch_script = script_dir / "fetch_wikipedia.py"

    try:
        result = subprocess.run(
            [sys.executable, str(fetch_script), slug],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error fetching article: {e.stderr}", file=sys.stderr)
        raise


def load_prompt_template(template_path):
    """
    Load the prompt template from file.

    Args:
        template_path: Path to the PROMPT.txt file

    Returns:
        Template content as string
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def prepare_prompt(template, article_content):
    """
    Replace the {{ article }} placeholder in the template with article content.

    Args:
        template: Prompt template with {{ article }} placeholder
        article_content: The Wikipedia article content

    Returns:
        Completed prompt
    """
    return template.replace('{{ article }}', article_content)


def send_to_gpt(prompt, api_url, api_key, model="gpt-4"):
    """
    Send prompt to OpenAI-compatible GPT completion endpoint using OpenAI Python library.

    Args:
        prompt: The complete prompt to send
        api_url: Custom API endpoint base URL
        api_key: API authentication key
        model: Model name to use (default: gpt-4)

    Returns:
        GPT completion response
    """
    try:
        # Initialize OpenAI client with custom base URL
        client = OpenAI(
            api_key=api_key,
            base_url=api_url
        )

        # Create chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        raise


def main():
    """Main function."""
    global VERBOSE

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Transform Wikipedia articles using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'article_title',
        help='Title of the Wikipedia article (e.g., "Soupe à l\'oignon")'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (show progress messages)'
    )

    args = parser.parse_args()
    VERBOSE = args.verbose
    article_title = args.article_title

    # Load environment variables
    load_dotenv()

    api_url = os.getenv('LLM_API_URL')
    api_key = os.getenv('LLM_API_KEY')
    model = os.getenv('LLM_MODEL', 'gpt-4')

    if not api_url or not api_key:
        print("Error: LLM_API_URL and LLM_API_KEY must be set in .env file", file=sys.stderr)
        sys.exit(1)

    script_dir = Path(__file__).parent
    prompt_template_path = script_dir / "PROMPT.txt"

    try:
        # Convert title to Wikipedia slug
        log("Converting title to slug...")
        slug = title_to_slug(article_title)
        log(f"Slug: {slug}")

        # Fetch article content
        log("Fetching article content...")
        article_content = fetch_article_content(slug)
        log(f"Article fetched ({len(article_content)} characters)")

        # Load and prepare prompt
        log("Loading prompt template...")
        template = load_prompt_template(prompt_template_path)
        prompt = prepare_prompt(template, article_content)
        log(f"Prompt prepared ({len(prompt)} characters)")

        # Send to GPT
        log("Sending to LLM endpoint...")
        result = send_to_gpt(prompt, api_url, api_key, model)

        # Output result
        print(result)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
