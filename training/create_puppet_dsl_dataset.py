#!/usr/bin/env python3
"""
Create high-quality Puppet DSL training dataset with explicit formatting
"""

import json

def create_puppet_dsl_examples():
    """Create examples that clearly show input->output format for Puppet DSL"""
    
    examples = [
        # File resources - very explicit examples
        {
            "text": "# Create a Puppet file resource\nfile { '/etc/motd':\n  ensure  => present,\n  content => 'Welcome to this server',\n  owner   => 'root',\n  group   => 'root',\n  mode    => '0644',\n}"
        },
        {
            "text": "# Create a Puppet file resource\nfile { '/var/www/html/index.html':\n  ensure  => file,\n  content => '<h1>Hello World</h1>',\n  owner   => 'www-data',\n  group   => 'www-data',\n  mode    => '0644',\n}"
        },
        
        # Package resources
        {
            "text": "# Install nginx package\npackage { 'nginx':\n  ensure => installed,\n}"
        },
        {
            "text": "# Install apache package\npackage { 'apache2':\n  ensure => present,\n}"
        },
        
        # Service resources  
        {
            "text": "# Create a Puppet service resource\nservice { 'nginx':\n  ensure => running,\n  enable => true,\n}"
        },
        {
            "text": "# Manage apache2 service\nservice { 'apache2':\n  ensure     => running,\n  enable     => true,\n  hasrestart => true,\n  hasstatus  => true,\n}"
        },
        
        # Class definitions - exactly like Sonnet's examples
        {
            "text": "# Define a Puppet class for Apache web server\nclass apache {\n  package { 'apache2':\n    ensure => installed,\n  }\n  \n  file { '/etc/apache2/apache2.conf':\n    ensure  => present,\n    owner   => 'root',\n    group   => 'root',\n    mode    => '0644',\n    require => Package['apache2'],\n    notify  => Service['apache2'],\n  }\n  \n  service { 'apache2':\n    ensure     => running,\n    enable     => true,\n    hasrestart => true,\n    hasstatus  => true,\n    require    => Package['apache2'],\n  }\n}"
        },
        {
            "text": "# Define a Puppet class for web server\nclass webserver {\n  package { 'nginx':\n    ensure => installed,\n  }\n  \n  service { 'nginx':\n    ensure  => running,\n    enable  => true,\n    require => Package['nginx'],\n  }\n  \n  file { '/var/www/html/index.html':\n    ensure  => file,\n    content => '<h1>Welcome</h1>',\n    require => Package['nginx'],\n  }\n}"
        },
        
        # User management
        {
            "text": "# Create a user account\nuser { 'webapp':\n  ensure => present,\n  uid    => 1001,\n  shell  => '/bin/bash',\n  home   => '/home/webapp',\n}"
        },
        
        # Directory creation
        {
            "text": "# Create a directory\nfile { '/opt/myapp':\n  ensure => directory,\n  owner  => 'myapp',\n  group  => 'myapp',\n  mode   => '0755',\n}"
        },
        
        # Multiple resources
        {
            "text": "# Install and configure nginx\npackage { 'nginx':\n  ensure => installed,\n}\n\nservice { 'nginx':\n  ensure  => running,\n  enable  => true,\n  require => Package['nginx'],\n}\n\nfile { '/etc/nginx/nginx.conf':\n  ensure  => file,\n  owner   => 'root',\n  group   => 'root',\n  mode    => '0644',\n  require => Package['nginx'],\n  notify  => Service['nginx'],\n}"
        },
        
        # Exec resources
        {
            "text": "# Execute a command\nexec { 'update-apt':\n  command => '/usr/bin/apt-get update',\n  unless  => '/usr/bin/test -f /var/cache/apt/pkgcache.bin',\n}"
        },
        
        # Complete class with parameters
        {
            "text": "# Define a Puppet class for Apache web server\nclass apache (\n  String $server_name = 'localhost',\n  String $admin_email = 'admin@localhost'\n) {\n  package { 'apache2':\n    ensure => installed,\n  }\n  \n  file { '/var/www/html':\n    ensure  => directory,\n    owner   => 'www-data',\n    group   => 'www-data',\n    mode    => '0755',\n    require => Package['apache2'],\n  }\n  \n  service { 'apache2':\n    ensure     => running,\n    enable     => true,\n    hasrestart => true,\n    require    => Package['apache2'],\n  }\n}"
        },
        
        # Node definition
        {
            "text": "# Define a node\nnode 'webserver01.example.com' {\n  include apache\n}"
        },
        
        # Defined type
        {
            "text": "# Create a defined type\ndefine webapp::site (\n  String $docroot,\n  Integer $port = 80\n) {\n  file { \"/etc/apache2/sites-available/${title}.conf\":\n    ensure  => file,\n    content => \"DocumentRoot ${docroot}\\nListen ${port}\",\n    notify  => Service['apache2'],\n  }\n}"
        }
    ]
    
    return examples

def main():
    """Create Puppet DSL training dataset"""
    print("Creating high-quality Puppet DSL training dataset...")
    
    examples = create_puppet_dsl_examples()
    
    # Save to file
    with open('../data_processing/puppet_dsl_training.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2)
    
    print(f"Created DSL dataset with {len(examples)} examples")
    print("Saved to: ../data_processing/puppet_dsl_training.json")

if __name__ == "__main__":
    main()
