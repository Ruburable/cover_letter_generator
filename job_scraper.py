import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import argparse
from datetime import datetime


class JobScraper:
    """Scrape job postings from URLs and save them as text files."""

    def __init__(self, output_dir="input"):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped job postings (default: input)
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _clean_text(self, text):
        """Clean extracted text by removing extra whitespace."""
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)

    def _generate_filename(self, url):
        """Generate a filename from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"job_{domain}_{timestamp}.txt"

    def scrape_url(self, url, delay=1):
        """
        Scrape a single URL and extract job posting content.

        Args:
            url: URL to scrape
            delay: Delay in seconds before scraping (to be polite)

        Returns:
            Dictionary with 'url', 'content', and 'success' keys
        """
        print(f"\nScraping: {url}")
        time.sleep(delay)  # Be polite to servers

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()

            # Try to find job posting content
            # Common selectors for job postings
            content = None

            # Try common job posting containers
            selectors = [
                {'class': 'job-description'},
                {'class': 'job-details'},
                {'class': 'posting-description'},
                {'id': 'job-description'},
                {'role': 'main'},
                {'class': 'description'},
                {'class': 'content'},
            ]

            for selector in selectors:
                element = soup.find(**selector)
                if element:
                    content = element.get_text()
                    break

            # If no specific container found, get main content
            if not content:
                # Try to find main or article tag
                main = soup.find('main') or soup.find('article')
                if main:
                    content = main.get_text()
                else:
                    # Fall back to body
                    content = soup.body.get_text() if soup.body else soup.get_text()

            # Clean the text
            content = self._clean_text(content)

            # Add URL at the top
            content = f"Source URL: {url}\n\n{content}"

            print(f"✓ Successfully scraped (length: {len(content)} chars)")
            return {
                'url': url,
                'content': content,
                'success': True
            }

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to scrape: {str(e)}")
            return {
                'url': url,
                'content': None,
                'success': False,
                'error': str(e)
            }

    def scrape_from_file(self, urls_file, delay=1, save_individual=True):
        """
        Scrape multiple URLs from a text file.

        Args:
            urls_file: Path to file containing URLs (one per line)
            delay: Delay between requests in seconds
            save_individual: If True, save each job posting as separate file

        Returns:
            List of results dictionaries
        """
        # Read URLs from file
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(f"Error: File not found: {urls_file}")
            return []

        if not urls:
            print("No URLs found in file")
            return []

        print(f"Found {len(urls)} URLs to scrape")

        results = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            result = self.scrape_url(url, delay=delay)
            results.append(result)

            # Save individual file if requested and successful
            if save_individual and result['success']:
                filename = self._generate_filename(url)
                filepath = os.path.join(self.output_dir, filename)
                self.save_content(result['content'], filepath)

        # Print summary
        successful = sum(1 for r in results if r['success'])
        print(f"\n{'=' * 60}")
        print(f"Scraping complete: {successful}/{len(urls)} successful")
        print(f"{'=' * 60}")

        return results

    def save_content(self, content, filepath):
        """Save content to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Saved to: {filepath}")

    def scrape_and_combine(self, urls_file, output_file=None, delay=1):
        """
        Scrape multiple URLs and combine into a single file.

        Args:
            urls_file: Path to file containing URLs
            output_file: Path for combined output (default: auto-generated)
            delay: Delay between requests
        """
        results = self.scrape_from_file(urls_file, delay=delay, save_individual=False)

        # Combine all successful results
        combined_content = []
        for result in results:
            if result['success']:
                combined_content.append("=" * 80)
                combined_content.append(result['content'])
                combined_content.append("\n")

        if combined_content:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(self.output_dir, f"combined_jobs_{timestamp}.txt")

            final_content = '\n'.join(combined_content)
            self.save_content(final_content, output_file)
            print(f"\nCombined file created: {output_file}")
        else:
            print("\nNo successful scrapes to combine")


def main():
    """Command-line interface for the job scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape job postings from URLs"
    )
    parser.add_argument(
        "--urls-file",
        default="offers/job_urls.txt",
        help="Path to file containing URLs (default: offers/job_urls.txt)"
    )
    parser.add_argument(
        "--output-dir",
        default="input",
        help="Directory to save scraped jobs (default: input)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all jobs into a single file instead of separate files"
    )
    parser.add_argument(
        "--combined-output",
        help="Path for combined output file (only with --combine)"
    )

    args = parser.parse_args()

    scraper = JobScraper(output_dir=args.output_dir)

    if args.combine:
        scraper.scrape_and_combine(
            args.urls_file,
            output_file=args.combined_output,
            delay=args.delay
        )
    else:
        scraper.scrape_from_file(
            args.urls_file,
            delay=args.delay,
            save_individual=True
        )


if __name__ == "__main__":
    main()