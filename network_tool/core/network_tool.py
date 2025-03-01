"""
Network Tool Core Module

This module integrates all components of the network tool to provide a complete
workflow for searching, scraping, and saving information about individuals.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

# Add the parent directory to the path
sys.path.append('.')

# Import utility modules
from network_tool.utils.input_handler import InputHandler
from network_tool.utils.search_handler import SearchHandler
from network_tool.utils.scraper_handler import ScraperHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetworkTool:
    """
    Main class for the network tool that integrates all components.
    """
    
    def __init__(self, 
                 input_file: str, 
                 output_dir: str = 'data/output',
                 max_results_per_query: int = 5,
                 max_concurrent_scrapes: int = 3,
                 search_rate_limit: float = 2.0,
                 scrape_rate_limit: float = 1.0,
                 max_retries: int = 3,
                 retry_delay: float = 2.0):
        """
        Initialize the NetworkTool.
        
        Args:
            input_file (str): Path to the input file (CSV or JSON)
            output_dir (str): Directory to save the output files
            max_results_per_query (int): Maximum number of search results per query
            max_concurrent_scrapes (int): Maximum number of concurrent scraping tasks
            search_rate_limit (float): Delay between searches in seconds
            scrape_rate_limit (float): Delay between scraping tasks in seconds
            max_retries (int): Maximum number of retry attempts for a failed request
            retry_delay (float): Delay between retry attempts in seconds
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize handlers
        self.input_handler = InputHandler(input_file)
        self.search_handler = SearchHandler(
            max_results_per_query=max_results_per_query,
            rate_limit_delay=search_rate_limit
        )
        self.scraper_handler = ScraperHandler(
            max_concurrent=max_concurrent_scrapes,
            rate_limit_delay=scrape_rate_limit,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        # Initialize statistics
        self.stats = {
            'total_people': 0,
            'total_searches': 0,
            'total_urls_found': 0,
            'total_urls_scraped': 0,
            'total_files_saved': 0,
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        }
    
    async def run(self) -> Dict:
        """
        Run the network tool workflow.
        
        Returns:
            Dict: Statistics about the run
        """
        logger.info(f"Starting network tool with input file: {self.input_file}")
        
        # Read input data
        people = self.input_handler.read_data()
        self.stats['total_people'] = len(people)
        
        if not people:
            logger.warning("No valid people data found in the input file")
            return self.stats
        
        logger.info(f"Processing {len(people)} people")
        
        # Process each person
        for i, person in enumerate(people, 1):
            logger.info(f"Processing person {i}/{len(people)}: {person['name']}")
            
            # Generate search query
            query = self.input_handler.generate_search_query(person)
            
            # Search for URLs
            search_results = self.search_handler.search_for_person(query)
            self.stats['total_searches'] += 1
            
            if not search_results:
                logger.warning(f"No search results found for {person['name']}")
                continue
            
            # Filter results
            email_domain = person['email'].split('@')[-1]
            filtered_results = self.search_handler.filter_results(
                search_results, person['name'], email_domain
            )
            
            if not filtered_results:
                logger.warning(f"No relevant search results found for {person['name']}")
                continue
            
            # Extract URLs
            urls = [result['url'] for result in filtered_results]
            self.stats['total_urls_found'] += len(urls)
            
            # Scrape URLs
            scraped_data = await self.scraper_handler.scrape_urls(urls)
            self.stats['total_urls_scraped'] += len(scraped_data)
            
            if not scraped_data:
                logger.warning(f"No data scraped for {person['name']}")
                continue
            
            # Save scraped data
            saved_files = self.scraper_handler.save_scraped_data(
                scraped_data, self.output_dir, person['name']
            )
            
            # Update statistics
            for url, files in saved_files.items():
                self.stats['total_files_saved'] += len(files)
            
            # Save search results for reference
            self._save_search_results(filtered_results, person['name'])
            
            logger.info(f"Completed processing for {person['name']}")
        
        # Update final statistics
        self.stats['end_time'] = time.time()
        self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
        
        # Save statistics
        self._save_statistics()
        
        logger.info(f"Network tool completed in {self.stats['duration']:.2f} seconds")
        logger.info(f"Processed {self.stats['total_people']} people")
        logger.info(f"Found {self.stats['total_urls_found']} URLs")
        logger.info(f"Scraped {self.stats['total_urls_scraped']} URLs")
        logger.info(f"Saved {self.stats['total_files_saved']} files")
        
        return self.stats
    
    def _save_search_results(self, results: List[Dict[str, str]], person_name: str) -> None:
        """
        Save search results to a JSON file.
        
        Args:
            results (List[Dict[str, str]]): List of search results
            person_name (str): Name of the person
        """
        person_dir = os.path.join(self.output_dir, person_name.replace(' ', '_').lower())
        os.makedirs(person_dir, exist_ok=True)
        
        results_file = os.path.join(person_dir, 'search_results.json')
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Saved search results for {person_name}")
            
        except Exception as e:
            logger.error(f"Error saving search results for {person_name}: {str(e)}")
    
    def _save_statistics(self) -> None:
        """
        Save statistics to a JSON file.
        """
        stats_file = os.path.join(self.output_dir, 'statistics.json')
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
            
            logger.info(f"Saved statistics to {stats_file}")
            
        except Exception as e:
            logger.error(f"Error saving statistics: {str(e)}")


async def main(input_file: str, output_dir: str, **kwargs) -> Dict:
    """
    Main function to run the network tool.
    
    Args:
        input_file (str): Path to the input file (CSV or JSON)
        output_dir (str): Directory to save the output files
        **kwargs: Additional arguments to pass to NetworkTool
    
    Returns:
        Dict: Statistics about the run
    """
    tool = NetworkTool(input_file, output_dir, **kwargs)
    return await tool.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Network Tool - Search and scrape information about individuals")
    parser.add_argument("input_file", help="Path to the input file (CSV or JSON)")
    parser.add_argument("--output-dir", default="data/output", help="Directory to save the output files")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of search results per query")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Maximum number of concurrent scraping tasks")
    parser.add_argument("--search-rate-limit", type=float, default=2.0, help="Delay between searches in seconds")
    parser.add_argument("--scrape-rate-limit", type=float, default=1.0, help="Delay between scraping tasks in seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retry attempts for a failed request")
    parser.add_argument("--retry-delay", type=float, default=2.0, help="Delay between retry attempts in seconds")
    
    args = parser.parse_args()
    
    asyncio.run(main(
        input_file=args.input_file,
        output_dir=args.output_dir,
        max_results_per_query=args.max_results,
        max_concurrent_scrapes=args.max_concurrent,
        search_rate_limit=args.search_rate_limit,
        scrape_rate_limit=args.scrape_rate_limit,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay
    )) 