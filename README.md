
# Sitemap Crawler

A Python tool for extracting URLs and metadata from XML sitemaps and sitemap indexes.

## Description

This crawler efficiently processes XML sitemaps and sitemap indexes, extracting all URLs along with their metadata (last modified date, change frequency, priority) and exports the results to CSV format.

## Features

- Crawls sitemap indexes and individual sitemaps
- Extracts URL metadata (lastmod, changefreq, priority)
- Handles both namespaced and non-namespaced XML
- Exports results to CSV format
- Provides crawling statistics
- Configurable request delays for respectful crawling
- Error handling for network and parsing issues

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone this repository:
`git clone https://github.com/kweidner14/sitemap-crawler.git cd sitemap-crawler`
2. Install dependencies: `pip install requests`


## Usage

### Basic Usage
Modify the `BASE_URL` and `SITEMAP_INDEX_URL` variables in the `main()` function, then run: `python sitemap-crawler.py`

### Programmatic Usage
`python from sitemap_crawler import SitemapCrawler
crawler = SitemapCrawler(base_url="[https://example.com](https://example.com)", delay=1.0) url_data = crawler.crawl_sitemap_index("sitemap_index.xml") crawler.save_to_csv(url_data, "output.csv")`


## Output

The tool generates a CSV file with the following columns:
- `url`: The extracted URL
- `last_modified`: Last modification date (if available)
- `change_frequency`: Change frequency (if available)
- `priority`: URL priority (if available)
- `source_sitemap`: Source sitemap filename

## Configuration

- `delay`: Time delay between requests (default: 1.0 seconds)
- `base_url`: Base URL for resolving relative paths
- Output filename can be customized

## License

This project is licensed under the GNU General Public License v2.0
