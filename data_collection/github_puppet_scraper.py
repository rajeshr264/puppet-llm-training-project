# create file: github_puppet_scraper.py
import os
import json
import time
from pathlib import Path
import requests

class GitHubPuppetScraper:
    def __init__(self, output_dir="raw_puppet_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def download_file(self, url, filepath):
        """Download a single file from GitHub"""
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True
        return False
    
    def scrape_repo(self, repo_url):
        """
        Scrape .pp files from a GitHub repo
        Example: https://github.com/puppetlabs/puppetlabs-apache
        """
        # Extract owner and repo name
        parts = repo_url.rstrip('/').split('/')
        owner = parts[-2]
        repo = parts[-1]
        
        # Create folder for this repo
        repo_dir = self.output_dir / f"{owner}_{repo}"
        repo_dir.mkdir(exist_ok=True)
        
        # Use GitHub API to list files
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        
        response = requests.get(api_url)
        if response.status_code != 200:
            print(f"Failed to access {repo_url}")
            return
        
        tree = response.json()['tree']
        puppet_files = [item for item in tree if item['path'].endswith('.pp')]
        
        print(f"Found {len(puppet_files)} Puppet files in {repo}")
        
        # Download each .pp file
        for file_info in puppet_files:
            file_path = file_info['path']
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
            
            # Save with directory structure
            local_path = repo_dir / file_path.replace('/', '_')
            
            if self.download_file(raw_url, local_path):
                print(f"  Downloaded: {file_path}")
            
            time.sleep(0.5)  # Be nice to GitHub
    
    def scrape_multiple_repos(self, repo_list):
        """Scrape multiple repositories"""
        for repo_url in repo_list:
            print(f"\nProcessing: {repo_url}")
            self.scrape_repo(repo_url)
            time.sleep(2)  # Pause between repos

# Usage example:
if __name__ == "__main__":
    scraper = GitHubPuppetScraper()
    
    # List of high-quality Puppet repos
    repos = [
        "https://github.com/puppetlabs/puppetlabs-apache",
        "https://github.com/puppetlabs/puppetlabs-mysql",
        "https://github.com/puppetlabs/puppetlabs-stdlib",
        "https://github.com/voxpupuli/puppet-nginx",
        "https://github.com/puppetlabs/puppetlabs-docker"
    ]
    
    scraper.scrape_multiple_repos(repos)