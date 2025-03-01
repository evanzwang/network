"""
Input Handler Module

This module provides functionality to read and validate input data containing
names and emails from various file formats (CSV, JSON).
"""

import csv
import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InputHandler:
    """
    Handles the reading and validation of input data containing names and emails.
    """
    
    def __init__(self, input_file: str):
        """
        Initialize the InputHandler with the path to the input file.
        
        Args:
            input_file (str): Path to the input file (CSV or JSON)
        
        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If the input file format is not supported
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        self.input_file = input_file
        self.file_extension = os.path.splitext(input_file)[1].lower()
        
        if self.file_extension not in ['.csv', '.json']:
            raise ValueError(f"Unsupported file format: {self.file_extension}. Supported formats: CSV, JSON")
    
    def read_data(self) -> List[Dict[str, str]]:
        """
        Read the input file and return a list of dictionaries containing name and email.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'name' and 'email' keys
        
        Raises:
            ValueError: If the input file is empty or has invalid format
        """
        if self.file_extension == '.csv':
            return self._read_csv()
        elif self.file_extension == '.json':
            return self._read_json()
        else:
            # This should never happen due to the check in __init__
            raise ValueError(f"Unsupported file format: {self.file_extension}")
    
    def _read_csv(self) -> List[Dict[str, str]]:
        """
        Read data from a CSV file.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'name' and 'email' keys
        
        Raises:
            ValueError: If the CSV file is empty or missing required columns
        """
        try:
            with open(self.input_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check if the CSV has the required columns
                required_columns = {'name', 'email'}
                if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                    raise ValueError(f"CSV file must contain 'name' and 'email' columns. Found: {reader.fieldnames}")
                
                # Read and validate each row
                data = []
                for row in reader:
                    # Clean the data
                    cleaned_row = {
                        'name': row['name'].strip(),
                        'email': row['email'].strip().lower()
                    }
                    
                    # Validate the data
                    if self._validate_row(cleaned_row):
                        data.append(cleaned_row)
                
                if not data:
                    logger.warning("No valid data found in the CSV file")
                
                return data
                
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise
    
    def _read_json(self) -> List[Dict[str, str]]:
        """
        Read data from a JSON file.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'name' and 'email' keys
        
        Raises:
            ValueError: If the JSON file is empty or has invalid format
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as jsonfile:
                json_data = json.load(jsonfile)
                
                # Check if the JSON data is a list
                if not isinstance(json_data, list):
                    raise ValueError("JSON file must contain a list of objects")
                
                # Read and validate each item
                data = []
                for item in json_data:
                    # Check if the item has the required keys
                    if not isinstance(item, dict) or not {'name', 'email'}.issubset(set(item.keys())):
                        logger.warning(f"Skipping invalid JSON item: {item}")
                        continue
                    
                    # Clean the data
                    cleaned_item = {
                        'name': item['name'].strip(),
                        'email': item['email'].strip().lower()
                    }
                    
                    # Validate the data
                    if self._validate_row(cleaned_item):
                        data.append(cleaned_item)
                
                if not data:
                    logger.warning("No valid data found in the JSON file")
                
                return data
                
        except Exception as e:
            logger.error(f"Error reading JSON file: {str(e)}")
            raise
    
    def _validate_row(self, row: Dict[str, str]) -> bool:
        """
        Validate a row of data.
        
        Args:
            row (Dict[str, str]): Dictionary with 'name' and 'email' keys
        
        Returns:
            bool: True if the row is valid, False otherwise
        """
        # Check if name is not empty
        if not row['name']:
            logger.warning(f"Skipping row with empty name: {row}")
            return False
        
        # Check if email is valid
        if not self._is_valid_email(row['email']):
            logger.warning(f"Skipping row with invalid email: {row}")
            return False
        
        return True
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Check if an email address is valid.
        
        Args:
            email (str): Email address to validate
        
        Returns:
            bool: True if the email is valid, False otherwise
        """
        # Simple regex for email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def generate_search_query(person: Dict[str, str]) -> str:
        """
        Generate a search query for a person based on their name and email.
        
        Args:
            person (Dict[str, str]): Dictionary with 'name' and 'email' keys
        
        Returns:
            str: Search query string
        """
        name = person['name']
        email = person['email']
        email_domain = email.split('@')[-1]
        
        # Generate a search query that includes the name and optionally the email domain
        # but excludes common email providers to avoid generic results
        common_email_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com'}
        
        if email_domain not in common_email_domains:
            # If the email domain is not common, include it in the search
            return f"{name} {email_domain}"
        else:
            # Otherwise, just search for the name
            return name 