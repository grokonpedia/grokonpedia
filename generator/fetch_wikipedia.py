#!/usr/bin/env python3
"""
Wikipedia Article Fetcher and Cleaner
Fetches French Wikipedia articles and converts them to clean markdown.
"""

import re
import sys
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


USER_AGENT = "Grokonpedia Browser"


def fetch_wikipedia_page(title, lang="fr"):
    """
    Fetch a Wikipedia page using the Wikipedia API.

    Args:
        title: The title of the Wikipedia page
        lang: Language code (default: fr for French)

    Returns:
        HTML content of the page
    """
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/html/{title}"
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


def clean_html(html_content):
    """
    Remove unwanted elements from Wikipedia HTML.

    Removes:
    - Aside elements (infoboxes, navboxes)
    - Images and figures
    - Tables
    - References
    - Navigation elements

    Keeps:
    - Main text content
    - Text inside links
    - Headers
    - Lists
    - Text formatting (bold, italic)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements
    for element in soup.find_all(['aside', 'table', 'figure', 'img', 'nav']):
        element.decompose()

    # Remove infoboxes and navboxes by class
    for element in soup.find_all(class_=lambda x: x and any(
        cls in x for cls in ['infobox', 'navbox', 'metadata', 'ambox', 'noprint', 'sistersitebox']
    )):
        element.decompose()

    # Remove reference sections
    for element in soup.find_all(['ol', 'ul'], class_=lambda x: x and 'references' in x):
        element.decompose()

    # Remove sup elements (reference markers)
    for sup in soup.find_all('sup'):
        sup.decompose()

    # Remove edit links
    for element in soup.find_all(class_=lambda x: x and 'mw-editsection' in x):
        element.decompose()

    return soup


def convert_to_markdown(soup):
    """
    Convert cleaned HTML to markdown.

    Supports:
    - Headers (h1-h6)
    - Bold (b, strong)
    - Italic (i, em)
    - Lists (ul, ol)
    - Paragraphs
    """
    markdown_lines = []

    def process_element(element, list_level=0):
        """Recursively process HTML elements and convert to markdown."""
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                return text
            return ""

        if not isinstance(element, Tag):
            return ""

        tag_name = element.name
        result = ""

        # Headers
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = get_text_content(element)
            if text:
                result = "\n" + ("#" * level) + " " + text + "\n"

        # Paragraphs
        elif tag_name == 'p':
            text = get_text_content(element)
            if text:
                result = "\n" + text + "\n"

        # Lists
        elif tag_name in ['ul', 'ol']:
            result = "\n"
            for i, li in enumerate(element.find_all('li', recursive=False)):
                prefix = "- " if tag_name == 'ul' else f"{i+1}. "
                text = get_text_content(li)
                if text:
                    indent = "  " * list_level
                    result += indent + prefix + text + "\n"
            result += "\n"

        # Divs and sections - process children
        elif tag_name in ['div', 'section', 'article', 'main', 'body']:
            for child in element.children:
                result += process_element(child, list_level)

        return result

    def get_text_content(element):
        """Extract text content with inline formatting."""
        if isinstance(element, NavigableString):
            # Don't strip to preserve spacing around inline elements
            return str(element)

        if not isinstance(element, Tag):
            return ""

        tag_name = element.name

        # Bold
        if tag_name in ['b', 'strong']:
            text = "".join(get_text_content(child) for child in element.children).strip()
            return f"**{text}**" if text else ""

        # Italic
        elif tag_name in ['i', 'em']:
            text = "".join(get_text_content(child) for child in element.children).strip()
            return f"*{text}*" if text else ""

        # Links - keep only the text
        elif tag_name == 'a':
            return "".join(get_text_content(child) for child in element.children)

        # Lists in inline context
        elif tag_name in ['ul', 'ol']:
            return ""

        # Other elements - process children
        else:
            result = ""
            for child in element.children:
                result += get_text_content(child)
            return result

    # Find the main content area
    main_content = soup.find('body') or soup

    markdown_text = process_element(main_content)

    return markdown_text


def clean_markdown(markdown_text):
    """
    Clean up the markdown text.

    - Remove repetitive line breaks (more than 2 consecutive)
    - Remove empty list items
    - Trim whitespace
    - Normalize multiple spaces to single space
    """
    # Normalize multiple spaces to single space (but preserve line breaks)
    markdown_text = re.sub(r'[ \t]+', ' ', markdown_text)

    # Remove repetitive line breaks (keep max 2)
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)

    # Remove empty list items
    markdown_text = re.sub(r'\n\s*[-*]\s*\n', '\n', markdown_text)
    markdown_text = re.sub(r'\n\s*\d+\.\s*\n', '\n', markdown_text)

    # Remove leading/trailing whitespace on each line
    lines = [line.strip() for line in markdown_text.split('\n')]
    markdown_text = '\n'.join(lines)

    # Remove repetitive line breaks again after cleaning
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)

    # Trim start and end
    markdown_text = markdown_text.strip()

    return markdown_text


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python fetch_wikipedia.py <page_title>")
        print("Example: python fetch_wikipedia.py Python_(langage)")
        sys.exit(1)

    page_title = sys.argv[1]

    try:
        html_content = fetch_wikipedia_page(page_title)
        cleaned_soup = clean_html(html_content)
        markdown = convert_to_markdown(cleaned_soup)
        cleaned_markdown = clean_markdown(markdown)

        print(cleaned_markdown)

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
