#!/usr/bin/env python3
"""
Multi-Generate - Run generate.py in parallel for multiple Wikipedia articles

This script reads article names from LIST.txt and executes generate.py for each
article in parallel, with a configurable concurrency limit.
"""

import sys
import argparse
import subprocess
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime


def setup_logging():
    """Configure logging to both file and console."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"multi-generate_{timestamp}.log"

    # Create formatters and handlers
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info(f"Logging to: {log_file}")
    return log_file


def load_article_list(list_file):
    """
    Load article names from LIST.txt file.

    Args:
        list_file: Path to the LIST.txt file

    Returns:
        List of article names (stripped of whitespace)
    """
    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            articles = [line.strip() for line in f if line.strip()]

        logging.info(f"Loaded {len(articles)} articles from {list_file}")
        return articles

    except FileNotFoundError:
        logging.error(f"File not found: {list_file}")
        raise
    except Exception as e:
        logging.error(f"Error reading {list_file}: {e}")
        raise


def run_generate(article_name, script_path, verbose=False):
    """
    Execute generate.py for a single article.

    Args:
        article_name: Name of the Wikipedia article
        script_path: Path to generate.py script
        verbose: Enable verbose output

    Returns:
        Tuple of (article_name, success, message)
    """
    try:
        # Build command
        cmd = [sys.executable, str(script_path), article_name]
        if verbose:
            cmd.append('-v')

        logging.info(f"Starting: {article_name}")

        # Run generate.py
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per article
        )

        if result.returncode == 0:
            logging.info(f"SUCCESS: {article_name}")
            return (article_name, True, "Completed successfully")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logging.error(f"FAILED: {article_name} - {error_msg}")
            return (article_name, False, error_msg)

    except subprocess.TimeoutExpired:
        error_msg = "Timeout (exceeded 10 minutes)"
        logging.error(f"TIMEOUT: {article_name}")
        return (article_name, False, error_msg)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"ERROR: {article_name} - {error_msg}")
        return (article_name, False, error_msg)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Run generate.py in parallel for multiple Wikipedia articles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 4              # Run with 4 parallel workers
  %(prog)s 2 -v           # Run with 2 workers in verbose mode
  %(prog)s 8 -l custom.txt  # Use custom article list file
        """
    )
    parser.add_argument(
        'workers',
        type=int,
        help='Number of parallel tasks to run simultaneously'
    )
    parser.add_argument(
        '-l', '--list',
        default='LIST.txt',
        help='Path to file containing article names (default: LIST.txt)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for generate.py'
    )

    args = parser.parse_args()

    # Validate workers count
    if args.workers < 1:
        print("Error: Number of workers must be at least 1", file=sys.stderr)
        sys.exit(1)

    try:
        # Setup logging
        log_file = setup_logging()

        # Get script paths
        script_dir = Path(__file__).parent
        generate_script = script_dir / "generate.py"
        list_file = script_dir / args.list

        # Verify generate.py exists
        if not generate_script.exists():
            logging.error(f"generate.py not found at: {generate_script}")
            sys.exit(1)

        # Load article list
        articles = load_article_list(list_file)

        if not articles:
            logging.warning("No articles found in list file")
            return

        # Start parallel processing
        logging.info(f"Starting parallel processing with {args.workers} workers")
        logging.info("="*60)

        results = {
            'success': [],
            'failed': []
        }

        # Use ProcessPoolExecutor for true parallelism
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            # Submit all tasks
            future_to_article = {
                executor.submit(run_generate, article, generate_script, args.verbose): article
                for article in articles
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_article):
                article_name, success, message = future.result()

                if success:
                    results['success'].append(article_name)
                else:
                    results['failed'].append((article_name, message))

        # Print summary
        logging.info("="*60)
        logging.info("SUMMARY")
        logging.info("="*60)
        logging.info(f"Total articles: {len(articles)}")
        logging.info(f"Successful: {len(results['success'])}")
        logging.info(f"Failed: {len(results['failed'])}")

        if results['failed']:
            logging.info("\nFailed articles:")
            for article, error in results['failed']:
                logging.info(f"  - {article}: {error}")

        logging.info(f"\nDetailed log saved to: {log_file}")

        # Exit with error code if any failed
        if results['failed']:
            sys.exit(1)

    except KeyboardInterrupt:
        logging.warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
