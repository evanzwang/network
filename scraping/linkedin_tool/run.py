import csv
import os
import json
import requests
import time
from urllib.parse import urlparse
import concurrent.futures
import threading

# Thread-safe print lock
print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with print_lock:
        print(*args, **kwargs)

def extract_linkedin_id(linkedin_url):
    """Extract the LinkedIn ID from a LinkedIn URL."""
    if not linkedin_url or linkedin_url.lower() == 'none':
        return None
    
    parsed_url = urlparse(linkedin_url)
    path = parsed_url.path.strip('/')
    
    # Handle different URL formats
    if path.startswith('in/'):
        return path[3:]  # Remove 'in/' prefix
    return path

def scrape_linkedin_profile(linkedin_url):
    """Scrape a LinkedIn profile using the ScrapingDog API."""
    linkedin_id = extract_linkedin_id(linkedin_url)
    if not linkedin_id:
        return None
    
    api_key = "67c2d1d4cb75a93982012721"
    url = "https://api.scrapingdog.com/linkedin"
    
    # First try with private mode
    params = {
        "api_key": api_key,
        "type": "profile",
        "linkId": linkedin_id,
        "private": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            safe_print(f"Request failed for {linkedin_url} with status code: {response.status_code}, trying with private=true")
            
            # If first request fails, try with private=false
            params["private"] = "true"
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                safe_print(f"Second request also failed for {linkedin_url} with status code: {response.status_code}")
                return None
    except Exception as e:
        safe_print(f"Error scraping {linkedin_url}: {str(e)}")
        return None

def process_person(row, output_dir):
    """Process a single person from the CSV."""
    name = row.get("name", "").strip()
    linkedin_url = row.get("LinkedIn Url", "").strip()
    
    # Skip if name is empty or LinkedIn URL is None/empty
    if not name or not linkedin_url or linkedin_url.lower() == "none":
        safe_print(f"Skipping {name}: No LinkedIn URL")
        return
    
    # Create a directory for the person
    person_dir = os.path.join(output_dir, name.replace("/", "_"))
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    
    # Check if profile already exists
    profile_file = os.path.join(person_dir, "linkedin_profile.json")
    if os.path.exists(profile_file):
        safe_print(f"Skipping {name}: Profile already exists")
        return
    
    safe_print(f"Processing {name} with LinkedIn URL: {linkedin_url}")
    
    # Scrape the LinkedIn profile
    profile_data = scrape_linkedin_profile(linkedin_url)
    
    if profile_data:
        # Save the profile data to a JSON file
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
        safe_print(f"Saved LinkedIn profile for {name}")
    else:
        safe_print(f"Failed to scrape LinkedIn profile for {name}")
    
    # Add a delay to avoid rate limiting
    time.sleep(2)

def main():
    """Main function to process the LinkedIn CSV file."""
    # Create output directory if it doesn't exist
    output_dir = "linkedin_profiles"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the CSV file
    with open("linkedin2.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    # Process people in parallel with 4 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit tasks
        futures = [executor.submit(process_person, row, output_dir) for row in rows]
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        
    safe_print("All LinkedIn profiles processed.")

if __name__ == "__main__":
    main()
