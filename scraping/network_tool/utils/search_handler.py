"""
Search Handler Module

This module provides functionality to search for URLs related to a person
using the search_engine.py tool.
"""

import logging
import sys
import time
from typing import Dict, List, Optional

# Import the search_engine module
sys.path.append('.')  # Add the current directory to the path
from tools.search_engine import search_with_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SearchHandler:
    """
    Handles searching for URLs related to a person.
    """
    
    def __init__(self, max_results_per_query: int = 5, max_retries: int = 3, rate_limit_delay: float = 2.0):
        """
        Initialize the SearchHandler.
        
        Args:
            max_results_per_query (int): Maximum number of results to return per query
            max_retries (int): Maximum number of retry attempts for a search
            rate_limit_delay (float): Delay between searches in seconds to avoid rate limiting
        """
        self.max_results_per_query = max_results_per_query
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.search_count = 0
    
    def search_for_person(self, query: str) -> List[Dict[str, str]]:
        """
        Search for URLs related to a person.
        
        Args:
            query (str): Search query
        
        Returns:
            List[Dict[str, str]]: List of search results with URLs, titles, and snippets
        """
        # Apply rate limiting if not the first search
        if self.search_count > 0:
            logger.info(f"Rate limiting: Waiting {self.rate_limit_delay} seconds before next search")
            time.sleep(self.rate_limit_delay)
        
        self.search_count += 1
        
        try:
            logger.info(f"Searching for: {query}")
            results = search_with_retry(
                query=query,
                max_results=self.max_results_per_query,
                max_retries=self.max_retries
            )
            
            # Format the results
            formatted_results = []
            for result in results:
                formatted_result = {
                    'url': result.get('href', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('body', '')
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return []
    
    def filter_results(self, results: List[Dict[str, str]], person_name: str, email_domain: str) -> List[Dict[str, str]]:
        """
        Filter search results to remove irrelevant URLs.
        
        Args:
            results (List[Dict[str, str]]): List of search results
            person_name (str): Name of the person
            email_domain (str): Domain of the person's email
        
        Returns:
            List[Dict[str, str]]: Filtered list of search results
        """
        if not results:
            return []
        
        # Split the name into parts for more flexible matching
        name_parts = person_name.lower().split()
        
        # Common domains to exclude (social media, generic sites)
        excluded_domains = {
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'pinterest.com', 'reddit.com', 'tumblr.com',
            'wikipedia.org', 'amazon.com', 'ebay.com', 'etsy.com'
        }
        
        filtered_results = []
        for result in results:
            url = result.get('url', '').lower()
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Skip results from excluded domains
            if any(domain in url for domain in excluded_domains):
                logger.debug(f"Skipping result from excluded domain: {url}")
                continue
            
            # Check if the result is relevant to the person
            # A result is considered relevant if:
            # 1. It contains parts of the person's name in the title or snippet
            # 2. It contains the email domain (if not a common domain)
            is_relevant = False
            
            # Check for name parts in title and snippet
            if any(part in title or part in snippet for part in name_parts):
                is_relevant = True
            
            # Check for email domain in URL
            if email_domain not in {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'} and email_domain in url:
                is_relevant = True
            
            if is_relevant:
                filtered_results.append(result)
            else:
                logger.debug(f"Skipping irrelevant result: {url}")
        
        logger.info(f"Filtered results: {len(filtered_results)} out of {len(results)}")
        return filtered_results 