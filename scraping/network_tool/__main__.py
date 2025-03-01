"""
Network Tool - Main Entry Point

This module provides a command-line interface for the network tool.
"""

import asyncio
import argparse
import logging
import sys
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the main module
from network_tool.core.network_tool import main as run_tool


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Network Tool - Search and scrape information about individuals"
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input file (CSV or JSON)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="data/output",
        help="Directory to save the output files"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of search results per query"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent scraping tasks"
    )
    
    parser.add_argument(
        "--search-rate-limit",
        type=float,
        default=2.0,
        help="Delay between searches in seconds"
    )
    
    parser.add_argument(
        "--scrape-rate-limit",
        type=float,
        default=1.0,
        help="Delay between scraping tasks in seconds"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts for a failed request"
    )
    
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Delay between retry attempts in seconds"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the network tool.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Run the tool
        stats = asyncio.run(run_tool(
            input_file=args.input_file,
            output_dir=args.output_dir,
            max_results_per_query=args.max_results,
            max_concurrent_scrapes=args.max_concurrent,
            search_rate_limit=args.search_rate_limit,
            scrape_rate_limit=args.scrape_rate_limit,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        ))
        
        # Print summary
        print("\nNetwork Tool - Summary")
        print("=====================")
        print(f"Processed {stats['total_people']} people")
        print(f"Found {stats['total_urls_found']} URLs")
        print(f"Scraped {stats['total_urls_scraped']} URLs")
        print(f"Saved {stats['total_files_saved']} files")
        print(f"Total time: {stats['duration']:.2f} seconds")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Network tool interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Error running network tool: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 