# create file: website_puppet_scraper.py
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlparse

class WebsitePuppetScraper:
    def __init__(self, output_dir="web_puppet_examples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_code_blocks(self, url):
        """Extract Puppet code blocks from a webpage with improved detection"""
        try:
            print(f"  Fetching URL: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            examples = []
            
            # Check if this is a raw file (like GitHub raw files)
            if url.endswith('.pp') or 'raw.githubusercontent.com' in url:
                # This is a raw Puppet manifest file
                content = response.text.strip()
                if content and len(content) > 20:
                    # Extract filename for description
                    filename = url.split('/')[-1]
                    repo_info = url.split('/')[-4:-1]  # Extract org/repo/branch
                    
                    description = f"Puppet manifest {filename}"
                    if len(repo_info) >= 2:
                        description = f"Puppet {repo_info[1].replace('puppetlabs-', '')} module - {filename.replace('.pp', '')} manifest"
                    
                    examples.append({
                        'code': content,
                        'description': description,
                        'source': url,
                        'puppet_score': 10,  # High confidence for .pp files
                        'element_type': 'raw_file',
                        'element_classes': []
                    })
                    print(f"    Found raw Puppet file: {len(content)} characters")
                
                return examples
            
            # Otherwise, parse as HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Enhanced patterns for finding code blocks
            code_selectors = [
                'pre', 'code', 
                'div.highlight', 'div.code', 'div.codehilite',
                'div[class*="highlight"]', 'div[class*="code"]',
                'div[class*="language"]', 'div[class*="puppet"]',
                'span[class*="highlight"]'
            ]
            
            # Find all potential code containers
            all_code_elements = []
            for selector in code_selectors:
                elements = soup.select(selector)
                all_code_elements.extend(elements)
            
            print(f"  Found {len(all_code_elements)} potential code elements")
            
            for block in all_code_elements:
                code = block.get_text().strip()
                
                # Skip very short snippets
                if len(code) < 10:
                    continue
                
                # Enhanced Puppet code detection patterns
                puppet_patterns = [
                    r'\bclass\s+\w+',
                    r'\bdefine\s+\w+',
                    r'\bnode\s+[\'"]?\w+',
                    r'\binclude\s+\w+',
                    r'\brequire\s+\w+',
                    r'\bnotify\s*=>',
                    r'\bfile\s*{',
                    r'\bpackage\s*{',
                    r'\bservice\s*{',
                    r'\bexec\s*{',
                    r'\buser\s*{',
                    r'\bgroup\s*{',
                    r'=>\s*[\'"]',
                    r'\bensure\s*=>',
                    r'\bcontent\s*=>',
                    r'\bsource\s*=>',
                    r'[$]\w+',  # Variables
                    r'\w+::\w+',  # Module references
                ]
                
                # Check if code matches Puppet patterns
                puppet_score = sum(1 for pattern in puppet_patterns if re.search(pattern, code, re.IGNORECASE))
                
                if puppet_score >= 2 or any(key in code.lower() for key in ['puppet', 'manifest', '.pp']):
                    # Try to find description/context
                    description = self.find_description(block, soup)
                    
                    examples.append({
                        'code': code,
                        'description': description,
                        'source': url,
                        'puppet_score': puppet_score,
                        'element_type': block.name,
                        'element_classes': block.get('class', [])
                    })
                    
                    print(f"    Found Puppet code (score: {puppet_score}): {code[:50]}...")
            
            return examples
            
        except requests.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return []
        except Exception as e:
            print(f"  Error parsing {url}: {e}")
            return []
    
    def find_description(self, code_block, soup):
        """Find descriptive text associated with a code block"""
        description_candidates = []
        
        # Look for preceding elements
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']:
            prev = code_block.find_previous(tag)
            if prev:
                text = prev.get_text().strip()
                if text and len(text) < 500:  # Reasonable description length
                    description_candidates.append(text)
        
        # Look for parent container text
        parent = code_block.parent
        if parent and parent.name in ['div', 'section', 'article']:
            # Find text nodes that are siblings
            for sibling in parent.find_all(['p', 'span', 'div'], recursive=False):
                if sibling != code_block:
                    text = sibling.get_text().strip()
                    if text and len(text) < 300:
                        description_candidates.append(text)
        
        # Return the most relevant description
        if description_candidates:
            # Prefer descriptions that mention puppet, code, example, etc.
            for desc in description_candidates:
                if any(word in desc.lower() for word in ['example', 'puppet', 'code', 'manifest', 'class', 'define']):
                    return desc
            # Fall back to first description
            return description_candidates[0]
        
        return ""
    
    def find_related_links(self, base_url, soup, max_links=10):
        """Find related documentation links to crawl"""
        related_links = set()
        base_domain = urlparse(base_url).netloc
        
        # Look for links that might contain more Puppet code
        link_patterns = [
            r'.*puppet.*',
            r'.*manifest.*', 
            r'.*class.*',
            r'.*module.*',
            r'.*type.*',
            r'.*example.*',
            r'.*tutorial.*'
        ]
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if not href:
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Only process links from the same domain
            if urlparse(full_url).netloc != base_domain:
                continue
                
            # Check if link text or URL suggests puppet content
            link_text = link.get_text().lower()
            url_lower = full_url.lower()
            
            if any(re.search(pattern, url_lower + ' ' + link_text) for pattern in link_patterns):
                related_links.add(full_url)
                
            if len(related_links) >= max_links:
                break
        
        return list(related_links)
    
    def scrape_puppet_docs(self, crawl_related=True):
        """Scrape Puppet documentation from various sources"""
        # Better URLs with known working sources
        urls = [
            # Direct GitHub raw files
            "https://raw.githubusercontent.com/puppetlabs/puppetlabs-apache/main/manifests/init.pp",
            "https://raw.githubusercontent.com/puppetlabs/puppetlabs-mysql/main/manifests/server.pp",
            "https://raw.githubusercontent.com/puppetlabs/puppetlabs-stdlib/main/manifests/init.pp",
            "https://raw.githubusercontent.com/puppetlabs/puppet/main/examples/hiera/site.pp",
            "https://raw.githubusercontent.com/puppetlabs/puppet/main/examples/standalone/environments/production/manifests/site.pp"
        ]
        
        all_examples = []
        processed_urls = set()
        
        for url in urls:
            print(f"Scraping: {url}")
            
            # Process main URL
            examples = self.extract_code_blocks(url)
            all_examples.extend(examples)
            processed_urls.add(url)
            print(f"  Found {len(examples)} examples from main page")
            
            # Rate limiting between main URLs
            time.sleep(1)
        
        # Try GitHub repository approach for more examples
        print("\nTrying GitHub repositories...")
        github_examples = self.scrape_github_repos()
        all_examples.extend(github_examples)
        
        # Always add comprehensive examples for training
        print("\nAdding comprehensive training examples...")
        all_examples.extend(self.create_comprehensive_examples())
        
        # Save to JSON
        output_file = self.output_dir / "puppet_docs_examples.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_examples, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(all_examples)} examples to {output_file}")
        
        # Also save a summary
        summary_file = self.output_dir / "scraping_summary.json"
        summary = {
            'total_examples': len(all_examples),
            'urls_processed': list(processed_urls),
            'examples_by_source': {}
        }
        
        for example in all_examples:
            source = example['source']
            if source not in summary['examples_by_source']:
                summary['examples_by_source'][source] = 0
            summary['examples_by_source'][source] += 1
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return all_examples
    
    def scrape_github_repos(self):
        """Scrape Puppet manifests directly from GitHub repositories"""
        examples = []
        
        # Known Puppet module repositories with good examples
        repos = [
            "puppetlabs/puppetlabs-apache",
            "puppetlabs/puppetlabs-mysql", 
            "puppetlabs/puppetlabs-postgresql",
            "puppetlabs/puppetlabs-nginx",
            "puppetlabs/puppetlabs-stdlib"
        ]
        
        for repo in repos:
            print(f"  Checking GitHub repo: {repo}")
            
            # Try common manifest paths
            common_paths = [
                f"https://raw.githubusercontent.com/{repo}/main/manifests/init.pp",
                f"https://raw.githubusercontent.com/{repo}/master/manifests/init.pp",
                f"https://raw.githubusercontent.com/{repo}/main/manifests/server.pp",
                f"https://raw.githubusercontent.com/{repo}/main/manifests/install.pp",
                f"https://raw.githubusercontent.com/{repo}/main/manifests/config.pp",
                f"https://raw.githubusercontent.com/{repo}/main/manifests/service.pp"
            ]
            
            for path in common_paths:
                try:
                    response = self.session.get(path, timeout=10)
                    if response.status_code == 200:
                        content = response.text.strip()
                        if content and len(content) > 50:
                            # Extract module name and type
                            module_name = repo.split('/')[-1].replace('puppetlabs-', '')
                            manifest_type = path.split('/')[-1].replace('.pp', '')
                            
                            description = f"Puppet {module_name} module - {manifest_type} manifest"
                            
                            examples.append({
                                'code': content,
                                'description': description,
                                'source': path,
                                'puppet_score': 10,
                                'element_type': 'github_manifest',
                                'element_classes': []
                            })
                            print(f"    Found manifest: {manifest_type} ({len(content)} chars)")
                            break  # Found one, move to next repo
                            
                except Exception as e:
                    continue  # Try next path
                    
            time.sleep(0.5)  # Be nice to GitHub
        
        return examples
    
    def scrape_alternative_sources(self):
        """Scrape from alternative sources like GitHub raw files and tutorials"""
        examples = []
        
        # Try to get example manifests from GitHub
        github_urls = [
            "https://raw.githubusercontent.com/puppetlabs/puppet/main/examples/hiera/site.pp",
            "https://raw.githubusercontent.com/puppetlabs/puppet/main/examples/standalone/environments/production/manifests/site.pp"
        ]
        
        for url in github_urls:
            try:
                print(f"  Trying GitHub source: {url}")
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    if content.strip() and any(keyword in content for keyword in ['class', 'define', 'node', '=>']):
                        examples.append({
                            'code': content,
                            'description': f'Example Puppet manifest from {url}',
                            'source': url,
                            'puppet_score': 10,  # High confidence for .pp files
                            'element_type': 'raw_file',
                            'element_classes': []
                        })
                        print(f"    Found Puppet manifest: {len(content)} characters")
            except Exception as e:
                print(f"    Error fetching {url}: {e}")
        
        # Create some hardcoded examples if nothing else works
        if not examples:
            print("  Creating fallback examples...")
            examples = self.create_fallback_examples()
        
        return examples
    
    def create_comprehensive_examples(self):
        """Create comprehensive Puppet examples for training"""
        comprehensive_examples = [
            {
                'code': '''class apache {
  package { 'apache2':
    ensure => installed,
  }
  
  service { 'apache2':
    ensure  => running,
    enable  => true,
    require => Package['apache2'],
  }
  
  file { '/var/www/html/index.html':
    ensure  => file,
    content => '<h1>Hello from Puppet!</h1>',
    require => Package['apache2'],
  }
  
  file { '/etc/apache2/sites-available/default':
    ensure  => file,
    source  => 'puppet:///modules/apache/default-site',
    notify  => Service['apache2'],
    require => Package['apache2'],
  }
}''',
                'description': 'Complete Apache web server class with package, service, and file management',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''define create_user($username, $uid, $shell = '/bin/bash', $groups = []) {
  user { $username:
    ensure  => present,
    uid     => $uid,
    shell   => $shell,
    home    => "/home/${username}",
    groups  => $groups,
    gid     => $username,
  }
  
  group { $username:
    ensure => present,
    gid    => $uid,
  }
  
  file { "/home/${username}":
    ensure  => directory,
    owner   => $username,
    group   => $username,
    mode    => '0755',
    require => User[$username],
  }
  
  file { "/home/${username}/.bashrc":
    ensure  => file,
    owner   => $username,
    group   => $username,
    mode    => '0644',
    source  => 'puppet:///modules/users/bashrc',
    require => File["/home/${username}"],
  }
}''',
                'description': 'Comprehensive defined type for creating users with home directories and configuration',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''node 'webserver.example.com' {
  include apache
  include mysql::server
  include php
  
  package { ['php-mysql', 'php-gd', 'php-curl']:
    ensure  => installed,
    require => Class['php'],
  }
  
  file { '/etc/apache2/sites-available/webapp.conf':
    ensure  => file,
    content => template('webapp/apache-vhost.erb'),
    notify  => Service['apache2'],
    require => Class['apache'],
  }
  
  apache::site { 'webapp':
    ensure  => enabled,
    require => File['/etc/apache2/sites-available/webapp.conf'],
  }
  
  mysql::db { 'webapp_db':
    user     => 'webapp_user',
    password => 'secure_password',
    host     => 'localhost',
    grant    => ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
  }
}''',
                'description': 'Complete node definition for a LAMP stack web server',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''class mysql::server (
  $root_password = 'changeme',
  $bind_address = '127.0.0.1',
  $port = 3306,
  $datadir = '/var/lib/mysql',
) {
  package { 'mysql-server':
    ensure => installed,
  }
  
  service { 'mysql':
    ensure  => running,
    enable  => true,
    require => Package['mysql-server'],
  }
  
  file { '/etc/mysql/mysql.conf.d/puppet.cnf':
    ensure  => file,
    content => template('mysql/puppet.cnf.erb'),
    notify  => Service['mysql'],
    require => Package['mysql-server'],
  }
  
  exec { 'set-mysql-password':
    unless  => "mysqladmin -uroot -p${root_password} status",
    command => "mysqladmin -uroot password ${root_password}",
    path    => ['/usr/bin', '/usr/sbin'],
    require => Service['mysql'],
  }
  
  mysql_user { 'root@localhost':
    ensure        => 'present',
    password_hash => mysql_password($root_password),
    require       => Exec['set-mysql-password'],
  }
}''',
                'description': 'Parameterized MySQL server class with configuration and security setup',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''class nginx (
  $worker_processes = 'auto',
  $worker_connections = 1024,
  $sendfile = true,
  $tcp_nopush = true,
) {
  package { 'nginx':
    ensure => installed,
  }
  
  service { 'nginx':
    ensure  => running,
    enable  => true,
    require => Package['nginx'],
  }
  
  file { '/etc/nginx/nginx.conf':
    ensure  => file,
    content => template('nginx/nginx.conf.erb'),
    notify  => Service['nginx'],
    require => Package['nginx'],
  }
  
  file { '/etc/nginx/sites-available':
    ensure  => directory,
    require => Package['nginx'],
  }
  
  file { '/etc/nginx/sites-enabled':
    ensure  => directory,
    require => Package['nginx'],
  }
  
  # Remove default site
  file { '/etc/nginx/sites-enabled/default':
    ensure => absent,
    notify => Service['nginx'],
  }
}''',
                'description': 'Nginx web server class with parameterized configuration',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''define nginx::site (
  $ensure = 'enabled',
  $server_name = $title,
  $root = "/var/www/${title}",
  $index = 'index.html index.htm',
  $access_log = "/var/log/nginx/${title}_access.log",
  $error_log = "/var/log/nginx/${title}_error.log",
) {
  include nginx
  
  file { "/etc/nginx/sites-available/${title}":
    ensure  => file,
    content => template('nginx/site.erb'),
    require => Class['nginx'],
  }
  
  case $ensure {
    'enabled': {
      file { "/etc/nginx/sites-enabled/${title}":
        ensure  => link,
        target  => "/etc/nginx/sites-available/${title}",
        require => File["/etc/nginx/sites-available/${title}"],
        notify  => Service['nginx'],
      }
    }
    'disabled': {
      file { "/etc/nginx/sites-enabled/${title}":
        ensure => absent,
        notify => Service['nginx'],
      }
    }
  }
  
  file { $root:
    ensure  => directory,
    owner   => 'www-data',
    group   => 'www-data',
    mode    => '0755',
    require => Class['nginx'],
  }
}''',
                'description': 'Nginx virtual host defined type with enable/disable functionality',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            },
            {
                'code': '''class firewall {
  # Ensure iptables is installed
  package { 'iptables':
    ensure => installed,
  }
  
  # Default policies
  exec { 'iptables-default-policy-input':
    command => 'iptables -P INPUT DROP',
    unless  => 'iptables -L INPUT | grep "policy DROP"',
    path    => ['/sbin', '/usr/sbin'],
    require => Package['iptables'],
  }
  
  exec { 'iptables-default-policy-forward':
    command => 'iptables -P FORWARD DROP',
    unless  => 'iptables -L FORWARD | grep "policy DROP"',
    path    => ['/sbin', '/usr/sbin'],
    require => Package['iptables'],
  }
  
  # Allow loopback
  exec { 'iptables-allow-loopback':
    command => 'iptables -A INPUT -i lo -j ACCEPT',
    unless  => 'iptables -L INPUT | grep "lo.*ACCEPT"',
    path    => ['/sbin', '/usr/sbin'],
    require => Exec['iptables-default-policy-input'],
  }
  
  # Allow established connections
  exec { 'iptables-allow-established':
    command => 'iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT',
    unless  => 'iptables -L INPUT | grep "state RELATED,ESTABLISHED"',
    path    => ['/sbin', '/usr/sbin'],
    require => Exec['iptables-default-policy-input'],
  }
}''',
                'description': 'Basic firewall class with iptables rules for security',
                'source': 'comprehensive_examples',
                'puppet_score': 10,
                'element_type': 'curated',
                'element_classes': []
            }
        ]
        
        print(f"    Created {len(comprehensive_examples)} comprehensive examples")
        return comprehensive_examples
    
    def debug_url_content(self, url):
        """Debug method to analyze webpage content"""
        print(f"=== Debugging URL: {url} ===")
        
        try:
            response = self.session.get(url, timeout=15)
            print(f"Status Code: {response.status_code}")
            print(f"Content Length: {len(response.content)}")
            print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count all elements
            all_elements = soup.find_all()
            print(f"Total HTML elements: {len(all_elements)}")
            
            # Look for any text that might contain puppet keywords
            page_text = soup.get_text().lower()
            puppet_keywords = ['class', 'define', 'puppet', 'manifest', 'node', 'include']
            keyword_counts = {kw: page_text.count(kw) for kw in puppet_keywords}
            print(f"Keyword counts: {keyword_counts}")
            
            # Look for specific elements
            code_elements = soup.find_all(['pre', 'code'])
            print(f"<pre>/<code> elements: {len(code_elements)}")
            
            div_elements = soup.find_all('div')
            print(f"<div> elements: {len(div_elements)}")
            
            # Show some content samples
            if code_elements:
                print("\nFirst code element content:")
                print(repr(code_elements[0].get_text()[:200]))
            
            # Look for elements with class attributes containing 'highlight', 'code', etc.
            special_divs = soup.find_all('div', class_=lambda x: x and any(
                keyword in ' '.join(x).lower() for keyword in ['highlight', 'code', 'language', 'puppet']
            ))
            print(f"Special divs with code-related classes: {len(special_divs)}")
            
            if special_divs:
                print("Special div classes:")
                for div in special_divs[:3]:
                    print(f"  {div.get('class')}")
            
        except Exception as e:
            print(f"Debug error: {e}")

# Usage:
if __name__ == "__main__":
    import sys
    
    scraper = WebsitePuppetScraper()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        # Debug mode - analyze each URL
        urls = [
            "https://help.puppet.com/core/8/Content/PuppetCore/using-puppet-code.htm",
            "https://www.puppetcookbook.com/"
        ]
        
        for url in urls:
            scraper.debug_url_content(url)
            print("\n" + "="*80 + "\n")
    else:
        # Normal scraping mode
        examples = scraper.scrape_puppet_docs(crawl_related=True)
        print(f"\nTotal examples collected: {len(examples)}")
        
        if examples:
            print("\nSample examples found:")
            for i, example in enumerate(examples[:3]):
                print(f"\nExample {i+1}:")
                print(f"Source: {example['source']}")
                print(f"Description: {example['description'][:100]}...")
                print(f"Code preview: {example['code'][:150]}...")
        else:
            print("\nNo examples found. Try running with 'debug' argument:")
            print("python website_puppet_scraper.py debug")

# Usage:
if __name__ == "__main__":
    scraper = WebsitePuppetScraper()
    examples = scraper.scrape_puppet_docs()
    print(f"\nTotal examples collected: {len(examples)}")