"""
Scraper Handler Module

This module provides functionality to scrape and parse HTML content from URLs
using the web_scraper.py tool.
"""

import asyncio
import logging
import os
import random
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Import the web_scraper module
sys.path.append('.')  # Add the current directory to the path
from tools.web_scraper import parse_html, validate_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScraperHandler:
    """
    Handles scraping and parsing HTML content from URLs.
    """
    
    # List of common user agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    ]
    
    def __init__(self, max_concurrent: int = 3, rate_limit_delay: float = 1.0, max_retries: int = 3, retry_delay: float = 2.0):
        """
        Initialize the ScraperHandler.
        
        Args:
            max_concurrent (int): Maximum number of concurrent scraping tasks
            rate_limit_delay (float): Delay between scraping tasks in seconds
            max_retries (int): Maximum number of retry attempts for a failed request
            retry_delay (float): Delay between retry attempts in seconds
        """
        self.max_concurrent = max_concurrent
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def scrape_urls(self, urls: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Scrape HTML content from multiple URLs concurrently.
        
        Args:
            urls (List[str]): List of URLs to scrape
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping URLs to their content and metadata
        """
        if not urls:
            logger.warning("No URLs provided for scraping")
            return {}
        
        # Validate URLs
        valid_urls = [url for url in urls if validate_url(url)]
        if len(valid_urls) < len(urls):
            logger.warning(f"Skipping {len(urls) - len(valid_urls)} invalid URLs")
        
        if not valid_urls:
            logger.warning("No valid URLs to scrape")
            return {}
        
        logger.info(f"Scraping {len(valid_urls)} URLs with max concurrency of {self.max_concurrent}")
        
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create tasks for each URL
        tasks = []
        for url in valid_urls:
            tasks.append(self._scrape_url_with_semaphore(url, semaphore))
        
        # Run tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Combine results into a dictionary
        scraped_data = {}
        for url, html_content, parsed_content in results:
            if html_content:
                scraped_data[url] = {
                    'html': html_content,
                    'text': parsed_content,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
        
        logger.info(f"Successfully scraped {len(scraped_data)} out of {len(valid_urls)} URLs")
        return scraped_data
    
    async def _scrape_url_with_semaphore(self, url: str, semaphore: asyncio.Semaphore) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Scrape a URL with a semaphore to limit concurrency.
        
        Args:
            url (str): URL to scrape
            semaphore (asyncio.Semaphore): Semaphore to limit concurrency
        
        Returns:
            Tuple[str, Optional[str], Optional[str]]: URL, HTML content, and parsed content
        """
        async with semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # Try to fetch the page with retries
            html_content = await self._fetch_with_retry(url)
            
            if html_content:
                parsed_content = parse_html(html_content)
                logger.info(f"Successfully scraped URL: {url}")
                return url, html_content, parsed_content
            else:
                logger.warning(f"Failed to scrape URL after {self.max_retries} attempts: {url}")
                return url, None, None
    
    async def _fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch a URL with retry logic and rotating user agents.
        
        Args:
            url (str): URL to fetch
        
        Returns:
            Optional[str]: HTML content if successful, None otherwise
        """
        import aiohttp
        
        # Try multiple times with different user agents
        for attempt in range(1, self.max_retries + 1):
            # Select a random user agent
            user_agent = random.choice(self.USER_AGENTS)
            
            # Set headers with the selected user agent
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            try:
                logger.info(f"Fetching {url} (Attempt {attempt}/{self.max_retries})")
                
                # Create a new session for each attempt
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            # Check content type
                            content_type = response.headers.get('Content-Type', '').lower()
                            
                            # Handle PDF files
                            if 'application/pdf' in content_type:
                                logger.info(f"Detected PDF content for {url}")
                                return await self._handle_pdf_content(url, response)
                            
                            # Handle HTML content
                            try:
                                content = await response.text()
                                logger.info(f"Successfully fetched {url} on attempt {attempt}")
                                return content
                            except UnicodeDecodeError:
                                # Try with different encoding
                                logger.warning(f"Unicode decode error for {url}. Trying with different encoding...")
                                return await self._handle_non_utf8_content(response)
                        elif response.status == 403:
                            # Forbidden - try again with a different user agent
                            logger.warning(f"HTTP 403 error for {url} on attempt {attempt}. Retrying with a different user agent...")
                            
                            # Exponential backoff
                            backoff_time = self.retry_delay * (2 ** (attempt - 1))
                            logger.info(f"Waiting {backoff_time:.2f} seconds before next attempt")
                            await asyncio.sleep(backoff_time)
                        else:
                            # Other HTTP error
                            logger.error(f"HTTP {response.status} error for {url} on attempt {attempt}")
                            
                            # For non-403 errors, we might still want to retry but with less optimism
                            if attempt < self.max_retries:
                                backoff_time = self.retry_delay * (2 ** (attempt - 1))
                                logger.info(f"Waiting {backoff_time:.2f} seconds before next attempt")
                                await asyncio.sleep(backoff_time)
            except Exception as e:
                # Handle network errors, timeouts, etc.
                logger.error(f"Error fetching {url} on attempt {attempt}: {str(e)}")
                
                if attempt < self.max_retries:
                    backoff_time = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Waiting {backoff_time:.2f} seconds before next attempt")
                    await asyncio.sleep(backoff_time)
        
        # If we get here, all attempts failed
        return None
    
    async def _handle_non_utf8_content(self, response) -> Optional[str]:
        """
        Handle non-UTF-8 encoded content.
        
        Args:
            response: aiohttp response object
        
        Returns:
            Optional[str]: Decoded content if successful, None otherwise
        """
        # Try different encodings
        encodings = ['latin-1', 'iso-8859-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                # Get raw bytes
                raw_data = await response.read()
                
                # Try to decode with the current encoding
                content = raw_data.decode(encoding)
                logger.info(f"Successfully decoded content with {encoding} encoding")
                return content
            except Exception as e:
                logger.warning(f"Failed to decode with {encoding} encoding: {str(e)}")
        
        # If all encodings fail, try to extract text from raw bytes
        try:
            raw_data = await response.read()
            # Remove non-printable characters
            printable_content = ''.join(chr(c) if 32 <= c < 127 else ' ' for c in raw_data)
            logger.info("Extracted printable characters from raw bytes")
            return printable_content
        except Exception as e:
            logger.error(f"Failed to extract printable characters: {str(e)}")
            return None
    
    async def _handle_pdf_content(self, url: str, response) -> Optional[str]:
        """
        Handle PDF content.
        
        Args:
            url (str): URL of the PDF
            response: aiohttp response object
        
        Returns:
            Optional[str]: Extracted text from PDF if successful, None otherwise
        """
        try:
            # Import PyPDF2 for PDF handling
            try:
                from PyPDF2 import PdfReader
                from io import BytesIO
            except ImportError:
                logger.warning("PyPDF2 not installed. Cannot extract text from PDF.")
                return f"[PDF content at {url} - Install PyPDF2 to extract text]"
            
            # Get raw bytes
            raw_data = await response.read()
            
            # Create a PDF reader
            pdf_file = BytesIO(raw_data)
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            # Combine all pages
            full_text = "\n\n".join(text_content)
            
            if full_text.strip():
                logger.info(f"Successfully extracted text from PDF at {url}")
                return full_text
            else:
                logger.warning(f"Extracted empty text from PDF at {url}")
                return f"[PDF content at {url} - No text extracted]"
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF at {url}: {str(e)}")
            return f"[PDF content at {url} - Error: {str(e)}]"
    
    @staticmethod
    def save_scraped_data(scraped_data: Dict[str, Dict[str, str]], output_dir: str, person_name: str) -> Dict[str, Dict[str, str]]:
        """
        Save scraped data to files.
        
        Args:
            scraped_data (Dict[str, Dict[str, str]]): Dictionary mapping URLs to their content and metadata
            output_dir (str): Directory to save the files
            person_name (str): Name of the person for whom the data was scraped
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping URLs to their saved file paths
        """
        if not scraped_data:
            logger.warning(f"No scraped data to save for {person_name}")
            return {}
        
        # Create a directory for the person
        person_dir = os.path.join(output_dir, person_name.replace(' ', '_').lower())
        os.makedirs(person_dir, exist_ok=True)
        
        # Save each URL's data
        saved_files = {}
        for url, data in scraped_data.items():
            try:
                # Create a filename from the URL
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                path = parsed_url.path.replace('/', '_')
                if not path:
                    path = 'index'
                
                # Save HTML content
                html_filename = f"{domain}{path}.html"
                html_path = os.path.join(person_dir, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(data['html'])
                
                # Save parsed text content
                text_filename = f"{domain}{path}.txt"
                text_path = os.path.join(person_dir, text_filename)
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(data['text'])
                
                # Save metadata
                meta_filename = f"{domain}{path}.meta.txt"
                meta_path = os.path.join(person_dir, meta_filename)
                with open(meta_path, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Timestamp: {data['timestamp']}\n")
                    f.write(f"Person: {person_name}\n")
                
                saved_files[url] = {
                    'html': html_path,
                    'text': text_path,
                    'meta': meta_path
                }
                
                logger.info(f"Saved data for URL: {url}")
                
            except Exception as e:
                logger.error(f"Error saving data for URL {url}: {str(e)}")
        
        logger.info(f"Saved data for {len(saved_files)} URLs for {person_name}")
        return saved_files 