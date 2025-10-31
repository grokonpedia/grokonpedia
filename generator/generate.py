#!/usr/bin/env python3
"""
Generate - Automate Hugo article creation from Wikipedia using Grokonify

This script takes a Wikipedia article title, processes it through grokonify.py,
and creates a new Hugo content file with the transformed content.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def title_to_slug(title):
    """
    Convert an article title to a Wikipedia-style slug.

    Args:
        title: The article title (e.g., "Soupe à l'oignon")

    Returns:
        Wikipedia-style slug (e.g., "Soupe_à_l'oignon")
    """
    # Replace spaces with underscores (Wikipedia style)
    slug = title.replace(' ', '_')

    return slug


def call_grokonify(article_title, verbose=False):
    """
    Call grokonify.py with the given article title and return the output.

    Args:
        article_title: Wikipedia article title
        verbose: Enable verbose output

    Returns:
        Transformed article content from grokonify
    """
    script_dir = Path(__file__).parent
    grokonify_script = script_dir / "grokonify.py"

    print(f"Calling grokonify.py for article: {article_title}")
    print("This may take a few minutes...", flush=True)

    try:
        # Build command
        cmd = [sys.executable, str(grokonify_script), article_title]
        if verbose:
            cmd.append('-v')

        # Run grokonify and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print("Grokonify completed successfully!")
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error running grokonify.py: {e.stderr}", file=sys.stderr)
        raise


def create_hugo_article(slug, content, project_root):
    """
    Create a new Hugo article with the given slug and content.

    Args:
        slug: Hugo-compatible article slug
        content: Article content to add
        project_root: Path to the Hugo project root

    Returns:
        Path to the created article file
    """
    # Create new Hugo content file
    print(f"Creating Hugo article: {slug}.md")

    try:
        # Run hugo new content command from project root
        result = subprocess.run(
            ["hugo", "new", "content", f"{slug}.md"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)

        # Path to the created file
        article_path = project_root / "content" / f"{slug}.md"

        # Append the grokonify content to the file
        print(f"Adding content to {article_path}")
        with open(article_path, 'a', encoding='utf-8') as f:
            f.write('\n')
            f.write(content)

        print(f"Article created successfully: {article_path}")
        return article_path

    except subprocess.CalledProcessError as e:
        print(f"Error creating Hugo article: {e.stderr}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error writing content: {e}", file=sys.stderr)
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate Hugo articles from Wikipedia using Grokonify',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Soupe à l'oignon"
  %(prog)s "French Revolution" -v
        """
    )
    parser.add_argument(
        'article_title',
        help='Title of the Wikipedia article'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()
    article_title = args.article_title

    try:
        # Get project paths
        script_dir = Path(__file__).parent
        project_root = script_dir.parent

        # Convert title to Wikipedia-style slug
        slug = title_to_slug(article_title)
        print(f"Article slug: {slug}")

        # Call grokonify to get transformed content
        content = call_grokonify(article_title, verbose=args.verbose)

        # Create Hugo article with content
        article_path = create_hugo_article(slug, content, project_root)

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Article: {article_title}")
        print(f"Slug: {slug}")
        print(f"File: {article_path}")
        print("\nYou can now build your Hugo site with: hugo server")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
