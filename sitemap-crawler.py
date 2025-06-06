import csv
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests


class SitemapCrawler:
    """Efficient sitemap crawler that extracts URLs with metadata to CSV."""

    SITEMAP_NS = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def __init__(self, base_url: str, delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.delay = delay
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create configured requests session."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Python Sitemap Crawler 1.0',
            'Accept': 'application/xml, text/xml, */*'
        })
        return session

    def _fetch_xml(self, url: str) -> Optional[ET.Element]:
        """Fetch and parse XML from URL with error handling."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            time.sleep(self.delay)
            return ET.fromstring(response.content)

        except (requests.RequestException, ET.ParseError) as e:
            print(f"Error processing {url}: {e}")
            return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute."""
        return url if url.startswith('http') else urljoin(self.base_url, url)

    def _extract_text(self, element: Optional[ET.Element]) -> str:
        """Safely extract text from XML element."""
        return element.text.strip() if element is not None and element.text else ''

    def _extract_sitemap_urls(self, root: ET.Element) -> List[str]:
        """Extract sitemap URLs from sitemap index."""
        urls = []

        # Try with namespace first, then without
        for xpath in ['.//ns:sitemap/ns:loc', './/sitemap/loc']:
            elements = root.findall(xpath, self.SITEMAP_NS if 'ns:' in xpath else {})
            urls.extend(self._extract_text(elem) for elem in elements)
            if urls:
                break

        return [url for url in urls if url]

    def _extract_url_data(self, root: ET.Element, source: str) -> List[Dict[str, str]]:
        """Extract URL data with metadata from sitemap."""
        url_data = []

        # Try with namespace first, then without
        for xpath in ['.//ns:url', './/url']:
            namespace = self.SITEMAP_NS if 'ns:' in xpath else {}
            prefix = 'ns:' if 'ns:' in xpath else ''

            for url_elem in root.findall(xpath, namespace):
                loc = self._extract_text(url_elem.find(f'{prefix}loc', namespace))
                if not loc:
                    continue

                url_data.append({
                    'url': loc,
                    'last_modified': self._extract_text(url_elem.find(f'{prefix}lastmod', namespace)),
                    'source_sitemap': source
                })

            if url_data:
                break

        return url_data

    def crawl_sitemap_index(self, sitemap_index_url: str) -> List[Dict[str, str]]:
        """Crawl sitemap index and extract all URLs with metadata."""
        sitemap_index_url = self._make_absolute_url(sitemap_index_url)
        print(f"Starting crawl from: {sitemap_index_url}")

        root = self._fetch_xml(sitemap_index_url)
        if root is None:
            return []

        # Get sitemap URLs
        sitemap_urls = self._extract_sitemap_urls(root)

        if not sitemap_urls:
            # Treat as regular sitemap
            print("Processing as regular sitemap")
            return self._extract_url_data(root, "sitemap_index.xml")

        print(f"Found {len(sitemap_urls)} sitemaps to process")

        # Process each sitemap
        all_url_data = []
        for sitemap_url in sitemap_urls:
            abs_url = self._make_absolute_url(sitemap_url)
            source_name = abs_url.split('/')[-1]

            sitemap_root = self._fetch_xml(abs_url)
            if sitemap_root is not None:  # Fixed: explicit None check
                url_data = self._extract_url_data(sitemap_root, source_name)
                all_url_data.extend(url_data)
                print(f"Extracted {len(url_data)} URLs from {source_name}")

        return all_url_data

    def save_to_csv(self, url_data: List[Dict[str, str]], filename: str = "extracted_urls.csv") -> None:
        """Save URL data to CSV file."""
        if not url_data:
            print("No URLs to save")
            return

        # Sort by URL for consistent output
        sorted_data = sorted(url_data, key=lambda x: x['url'])

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'last_modified', 'source_sitemap']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"Saved {len(url_data)} URLs to {filename}")

    def print_statistics(self, url_data: List[Dict[str, str]]) -> None:
        """Print crawling statistics."""
        if not url_data:
            return

        print(f"\nCrawling Statistics:")
        print(f"Total URLs: {len(url_data)}")

        # Domain breakdown
        domains = {}
        for item in url_data:
            domain = urlparse(item['url']).netloc
            domains[domain] = domains.get(domain, 0) + 1

        print(f"\nDomain breakdown:")
        for domain, count in sorted(domains.items()):
            print(f"  {domain}: {count} URLs")

        # Source sitemap breakdown
        sources = {}
        for item in url_data:
            source = item['source_sitemap']
            sources[source] = sources.get(source, 0) + 1

        print(f"\nSource sitemap breakdown:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count} URLs")



def main():
    """Main execution function."""
    BASE_URL = ""
    SITEMAP_INDEX_URL = "sitemap_index.xml"
    OUTPUT_FILE = "extracted_urls.csv"

    crawler = SitemapCrawler(base_url=BASE_URL, delay=1.0)

    # Crawl and extract URLs
    url_data = crawler.crawl_sitemap_index(SITEMAP_INDEX_URL)

    # Save results and show statistics
    crawler.save_to_csv(url_data, OUTPUT_FILE)
    crawler.print_statistics(url_data)


if __name__ == "__main__":
    main()