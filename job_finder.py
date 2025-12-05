import requests
from bs4 import BeautifulSoup

class JobFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }

    def extract_job_details(self, url):
        """Extracts job description from a given URL."""
        try:
            print(f"Fetching job details from {url}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Simple extraction: get title and all text
            # This is generic and might need site-specific tuning
            title = soup.title.string if soup.title else "Unknown Job"
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            description = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                "title": title,
                "company": "Unknown Company", # Hard to extract generically
                "description": description[:10000], # Limit length for LLM
                "link": url
            }
        except Exception as e:
            print(f"Error fetching job: {e}")
            return None
