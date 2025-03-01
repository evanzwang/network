"""
Tests for the input handler module.
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Add the parent directory to the path
sys.path.append('.')

from network_tool.utils.input_handler import InputHandler


class TestInputHandler(unittest.TestCase):
    """
    Test cases for the InputHandler class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.csv_data = "name,email\nJohn Smith,john.smith@example.com\nJane Doe,jane.doe@company.org"
        self.json_data = """[
            {"name": "John Smith", "email": "john.smith@example.com"},
            {"name": "Jane Doe", "email": "jane.doe@company.org"}
        ]"""
    
    @patch('os.path.exists')
    def test_init_file_not_found(self, mock_exists):
        """
        Test initialization with a non-existent file.
        """
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            InputHandler('nonexistent.csv')
    
    @patch('os.path.exists')
    def test_init_unsupported_format(self, mock_exists):
        """
        Test initialization with an unsupported file format.
        """
        mock_exists.return_value = True
        
        with self.assertRaises(ValueError):
            InputHandler('file.txt')
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_read_csv(self, mock_file, mock_exists):
        """
        Test reading data from a CSV file.
        """
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = self.csv_data
        
        with patch('csv.DictReader') as mock_reader:
            mock_reader.return_value.fieldnames = ['name', 'email']
            mock_reader.return_value.__iter__.return_value = [
                {'name': 'John Smith', 'email': 'john.smith@example.com'},
                {'name': 'Jane Doe', 'email': 'jane.doe@company.org'}
            ]
            
            handler = InputHandler('test.csv')
            data = handler.read_data()
            
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['name'], 'John Smith')
            self.assertEqual(data[0]['email'], 'john.smith@example.com')
            self.assertEqual(data[1]['name'], 'Jane Doe')
            self.assertEqual(data[1]['email'], 'jane.doe@company.org')
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_read_json(self, mock_file, mock_exists):
        """
        Test reading data from a JSON file.
        """
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = self.json_data
        
        with patch('json.load') as mock_load:
            mock_load.return_value = [
                {'name': 'John Smith', 'email': 'john.smith@example.com'},
                {'name': 'Jane Doe', 'email': 'jane.doe@company.org'}
            ]
            
            handler = InputHandler('test.json')
            data = handler.read_data()
            
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['name'], 'John Smith')
            self.assertEqual(data[0]['email'], 'john.smith@example.com')
            self.assertEqual(data[1]['name'], 'Jane Doe')
            self.assertEqual(data[1]['email'], 'jane.doe@company.org')
    
    def test_is_valid_email(self):
        """
        Test email validation.
        """
        self.assertTrue(InputHandler._is_valid_email('test@example.com'))
        self.assertTrue(InputHandler._is_valid_email('test.name@example.co.uk'))
        self.assertFalse(InputHandler._is_valid_email('test@'))
        self.assertFalse(InputHandler._is_valid_email('test@example'))
        self.assertFalse(InputHandler._is_valid_email('test'))
    
    def test_generate_search_query(self):
        """
        Test search query generation.
        """
        # Test with common email domain
        person1 = {'name': 'John Smith', 'email': 'john.smith@gmail.com'}
        query1 = InputHandler.generate_search_query(person1)
        self.assertEqual(query1, 'John Smith')
        
        # Test with non-common email domain
        person2 = {'name': 'Jane Doe', 'email': 'jane.doe@company.org'}
        query2 = InputHandler.generate_search_query(person2)
        self.assertEqual(query2, 'Jane Doe company.org')


if __name__ == '__main__':
    unittest.main() 