#!/usr/bin/env python3
import os
import requests
import json
import re
import time
import subprocess

class TaiwanOpenDataCrawler:
    def __init__(self):
        self.base_url = "https://data.gov.tw"
        self.api_base = "https://data.gov.tw/api/v2/rest/dataset"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
    def get_dataset_via_api(self, dataset_id):
        """Fetch dataset information via API"""
        url = f"{self.api_base}/{dataset_id}"
        print(f"Fetching dataset via API: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching dataset {dataset_id}: {e}")
            return None
    
    def extract_ods_links_from_api(self, api_data):
        """Extract ODS file download links from API response"""
        ods_links = []
        
        if not api_data or 'result' not in api_data:
            return ods_links
        
        distributions = api_data['result'].get('distribution', [])
        
        for dist in distributions:
            # Get download URL
            download_url = dist.get('resourceDownloadUrl', '')
            
            # Only process ODS files
            if '.ods' in download_url.lower():
                # Extract year from filename (first 3 digits)
                filename = os.path.basename(download_url)
                year_match = re.match(r'^(\d{3})', filename)
                
                if year_match:
                    year = year_match.group(1)
                    # Convert ROC year to AD year
                    year = str(int(year) + 1911)
                else:
                    # Try to extract from description as fallback
                    description = dist.get('resourceDescription', '')
                    year_match = re.search(r'(\d{3,4})年', description)
                    if year_match:
                        year = year_match.group(1)
                        if len(year) == 3 and year.isdigit():
                            year = str(int(year) + 1911)
                    else:
                        year = 'unknown'
                
                ods_links.append({
                    'url': download_url,
                    'year': year,
                    'description': dist.get('resourceDescription', ''),
                    'records': dist.get('resourceAmount', 'N/A')
                })
        
        return ods_links
    
    def download_ods_file(self, url, output_path):
        """Download ODS file to specified path"""
        try:
            print(f"Downloading: {url}")
            
            # Enhanced headers to avoid 406 errors
            download_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/vnd.oasis.opendocument.spreadsheet, application/octet-stream, */*',
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://data.gov.tw/'
            }
            
            response = requests.get(url, headers=download_headers, stream=True, timeout=30)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded to: {output_path}")
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            # Try alternative download method with session
            try:
                session = requests.Session()
                session.headers.update(download_headers)
                response = session.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded (using session) to: {output_path}")
                return True
            except Exception as e2:
                print(f"Error with alternative download method: {e2}")
                return False
    
    def convert_ods_to_csv(self, ods_path, csv_path):
        """Convert ODS file to CSV using LibreOffice headless mode"""
        try:
            print(f"Converting ODS to CSV: {ods_path}")
            
            # Create output directory
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            
            # Use LibreOffice in headless mode for conversion
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to',
                'csv',
                '--outdir',
                os.path.dirname(csv_path),
                ods_path
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"LibreOffice error: {result.stderr}")
                return False
            
            # LibreOffice creates the file with the same name but .csv extension
            temp_csv = os.path.join(os.path.dirname(csv_path), 
                                   os.path.basename(ods_path).replace('.ods', '.csv'))
            
            # Rename to desired filename if different
            if temp_csv != csv_path:
                os.rename(temp_csv, csv_path)
            
            print(f"Converted to: {csv_path}")
            return True
            
        except subprocess.TimeoutExpired:
            print("LibreOffice conversion timed out")
            return False
        except Exception as e:
            print(f"Error converting ODS to CSV: {e}")
            return False
    
    def process_dataset(self, dataset_id):
        """Process a single dataset: fetch, download ODS files, and convert to CSV"""
        print(f"\nProcessing dataset: {dataset_id}")
        
        # Get dataset via API
        api_data = self.get_dataset_via_api(dataset_id)
        if not api_data:
            return
        
        # Extract ODS links from API response
        ods_links = self.extract_ods_links_from_api(api_data)
        print(f"Found {len(ods_links)} ODS files")
        
        # Process each ODS file
        for link_info in ods_links:
            print(f"\nProcessing: {link_info['description']} ({link_info['records']} records)")
            
            # Create paths
            ods_dir = f"temp_ods/{dataset_id}"
            csv_dir = f"raw/{dataset_id}"
            ods_path = os.path.join(ods_dir, f"{link_info['year']}.ods")
            csv_path = os.path.join(csv_dir, f"{link_info['year']}.csv")
            
            # Check if CSV already exists
            if os.path.exists(csv_path):
                print(f"CSV file already exists: {csv_path}, skipping download")
                continue
            
            # Download ODS
            if self.download_ods_file(link_info['url'], ods_path):
                # Convert to CSV
                if self.convert_ods_to_csv(ods_path, csv_path):
                    print(f"Successfully processed {link_info['year']}.csv")
                else:
                    print(f"Failed to convert {link_info['year']}.ods")
                
                # Clean up ODS file only if CSV was created successfully
                if os.path.exists(csv_path):
                    os.remove(ods_path)
                    print(f"Cleaned up temporary ODS file")
                else:
                    print(f"CSV file not created, keeping ODS file")
            
            # Be polite to the server
            time.sleep(1)
    
    def run(self, dataset_ids):
        """Run the crawler for multiple datasets"""
        for dataset_id in dataset_ids:
            self.process_dataset(dataset_id)
        
        print("\nCrawling completed!")

if __name__ == "__main__":
    # Dataset IDs to process
    dataset_ids = ['157217', '152223', '156470']
    
    # Create crawler instance and run
    crawler = TaiwanOpenDataCrawler()
    crawler.run(dataset_ids)