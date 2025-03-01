"""
HTML Reducer Module

This module provides functionality to process HTML files in the output directory,
extracting only the relevant body text, URLs, and other important information.
It helps reduce the size of the stored data and makes it easier to analyze.
"""

import os
import re
import json
import logging
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTMLReducer:
    """
    Processes HTML files to extract and store only relevant content.
    """
    
    def __init__(self, output_dir: str = "data/output", reduced_dir: str = "data/reduced"):
        """
        Initialize the HTMLReducer.
        
        Args:
            output_dir (str): Directory containing the output data
            reduced_dir (str): Directory to store reduced HTML data
        """
        self.output_dir = output_dir
        self.reduced_dir = reduced_dir
        
        # Create reduced directory if it doesn't exist
        if not os.path.exists(self.reduced_dir):
            os.makedirs(self.reduced_dir)
            logger.info(f"Created reduced directory: {self.reduced_dir}")
        
    def process_all_html_files(self) -> Dict[str, int]:
        """
        Process all HTML files in the output directory.
        
        Returns:
            Dict[str, int]: Statistics about the processing
        """
        stats = {
            "total_people": 0,
            "total_files_processed": 0,
            "total_files_skipped": 0,
            "total_bytes_before": 0,
            "total_bytes_after": 0
        }
        
        # Check if output directory exists
        if not os.path.exists(self.output_dir):
            logger.error(f"Output directory {self.output_dir} does not exist")
            return stats
        
        # Get all person directories
        person_dirs = [d for d in os.listdir(self.output_dir) 
                      if os.path.isdir(os.path.join(self.output_dir, d))]
        
        stats["total_people"] = len(person_dirs)
        logger.info(f"Found {len(person_dirs)} person directories")
        
        # Process each person directory
        for person_dir in person_dirs:
            person_path = os.path.join(self.output_dir, person_dir)
            person_reduced_path = os.path.join(self.reduced_dir, person_dir)
            
            # Create person directory in reduced_dir if it doesn't exist
            if not os.path.exists(person_reduced_path):
                os.makedirs(person_reduced_path)
            
            person_stats = self._process_person_directory(person_path, person_reduced_path)
            
            # Update overall stats
            stats["total_files_processed"] += person_stats["files_processed"]
            stats["total_files_skipped"] += person_stats["files_skipped"]
            stats["total_bytes_before"] += person_stats["bytes_before"]
            stats["total_bytes_after"] += person_stats["bytes_after"]
        
        # Calculate reduction percentage
        if stats["total_bytes_before"] > 0:
            reduction_percent = (1 - (stats["total_bytes_after"] / stats["total_bytes_before"])) * 100
            logger.info(f"Total reduction: {reduction_percent:.2f}% (from {stats['total_bytes_before']} to {stats['total_bytes_after']} bytes)")
        
        # Save overall stats
        stats_path = os.path.join(self.reduced_dir, "reduction_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def _process_person_directory(self, person_dir: str, person_reduced_dir: str) -> Dict[str, int]:
        """
        Process all HTML files for a single person.
        
        Args:
            person_dir (str): Path to the person's directory
            person_reduced_dir (str): Path to store reduced data for this person
            
        Returns:
            Dict[str, int]: Statistics about the processing
        """
        person_name = os.path.basename(person_dir)
        logger.info(f"Processing files for {person_name}")
        
        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "bytes_before": 0,
            "bytes_after": 0
        }
        
        # Get all HTML files
        html_files = [f for f in os.listdir(person_dir) if f.endswith('.html')]
        
        for html_file in html_files:
            html_path = os.path.join(person_dir, html_file)
            reduced_path = os.path.join(person_reduced_dir, html_file.replace('.html', '.reduced.json'))
            
            try:
                # Process the HTML file
                before_size, after_size = self._process_html_file(html_path, reduced_path)
                
                stats["files_processed"] += 1
                stats["bytes_before"] += before_size
                stats["bytes_after"] += after_size
                
                logger.debug(f"Processed {html_file}: {before_size} -> {after_size} bytes")
            except Exception as e:
                logger.error(f"Error processing {html_file}: {str(e)}")
                stats["files_skipped"] += 1
        
        # Save person-specific stats
        stats_path = os.path.join(person_reduced_dir, "reduction_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Processed {stats['files_processed']} files for {person_name}")
        return stats
    
    def _process_html_file(self, html_path: str, reduced_path: str) -> Tuple[int, int]:
        """
        Process a single HTML file to extract relevant content.
        
        Args:
            html_path (str): Path to the HTML file
            reduced_path (str): Path to save the reduced data
            
        Returns:
            Tuple[int, int]: Size before and after processing
        """
        # Read the original HTML
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()
        
        before_size = len(html_content)
        
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract relevant information
        extracted_data = {
            "title": self._extract_title(soup),
            "meta_description": self._extract_meta_description(soup),
            "main_content": self._extract_main_content(soup),
            "links": self._extract_links(soup),
            "images": self._extract_images(soup)
        }
        
        # Save the reduced data
        with open(reduced_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2)
        
        after_size = os.path.getsize(reduced_path)
        
        return before_size, after_size
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract the meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
        
        # Try to find main content containers
        main_content = ""
        
        # Look for common content containers
        content_elements = soup.select('main, article, #content, .content, #main, .main')
        
        if content_elements:
            # Use the first content element found
            main_content = content_elements[0].get_text(separator='\n').strip()
        else:
            # Fallback to body content
            main_content = soup.body.get_text(separator='\n').strip() if soup.body else ""
        
        # Clean up the text
        main_content = re.sub(r'\n+', '\n', main_content)  # Remove multiple newlines
        main_content = re.sub(r'\s+', ' ', main_content)   # Normalize whitespace
        
        return main_content.strip()
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract links from the page."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                # Skip links longer than 2000 characters
                if len(href) <= 2000:
                    links.append({
                        "url": href,
                        "text": text
                    })
                else:
                    logger.debug(f"Skipping link with length {len(href)} characters")
        return links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract images from the page."""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            if src:
                images.append({
                    "src": src,
                    "alt": alt
                })
        return images

def main():
    """Main function to run the HTML reducer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process HTML files to extract relevant content')
    parser.add_argument('--output-dir', type=str, default='custom_output',
                        help='Directory containing the output data')
    parser.add_argument('--reduced-dir', type=str, default='custom_output/reduced',
                        help='Directory to store reduced HTML data')
    
    args = parser.parse_args()
    
    reducer = HTMLReducer(output_dir=args.output_dir, reduced_dir=args.reduced_dir)
    stats = reducer.process_all_html_files()
    
    print(f"Processed {stats['total_files_processed']} files for {stats['total_people']} people")
    print(f"Skipped {stats['total_files_skipped']} files due to errors")
    
    if stats['total_bytes_before'] > 0:
        reduction_percent = (1 - (stats['total_bytes_after'] / stats['total_bytes_before'])) * 100
        print(f"Total reduction: {reduction_percent:.2f}%")
        print(f"Before: {stats['total_bytes_before']} bytes")
        print(f"After: {stats['total_bytes_after']} bytes")
        print(f"Reduced data saved to: {args.reduced_dir}")

if __name__ == "__main__":
    main()
