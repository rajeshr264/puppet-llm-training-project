#!/usr/bin/env python3
"""
Create enhanced training dataset with better Puppet DSL examples
"""

import json

def create_enhanced_puppet_dataset():
    """Create a high-quality Puppet training dataset with clear examples"""
    
    examples = [
        # Basic file resources
        {
            "text": "# Create a basic file resource\nfile { '/etc/motd':\n  ensure  => present,\n  content => 'Welcome to this server',\n  owner   => 'root',\n  group   => 'root',\n  mode    => '0644',\n}"
        },
        {
            "text": "# Create a directory with specific permissions\nfile { '/opt/myapp':\n  ensure => directory,\n  owner  => 'myapp',\n  group  => 'myapp',\n  mode   => '0755',\n}"
        },
        
        # Package resources
        {
            "text": "# Install a package\npackage { 'nginx':\n  ensure => installed,\n}"
        },
        {
            "text": "# Install specific package version\npackage { 'apache2':\n  ensure => '2.4.41-4ubuntu3.14',\n}"
        },
        
        # Service resources  
        {
            "text": "# Manage a service\nservice { 'nginx':\n  ensure => running,\n  enable => true,\n}"
        },
        {
            "text": "# Stop and disable a service\nservice { 'apache2':\n  ensure => stopped,\n  enable => false,\n}"
        },
        
        # Classes
        {
            "text": "# Define a simple class\nclass webserver {\n  package { 'apache2':\n    ensure => installed,\n  }\n  \n  service { 'apache2':\n    ensure  => running,\n    enable  => true,\n    require => Package['apache2'],\n  }\n}"
        },
        {
            "text": "# Class with parameters\nclass mysql (\n  String $root_password,\n  String $version = '8.0'\n) {\n  package { 'mysql-server':\n    ensure => $version,\n  }\n  \n  service { 'mysql':\n    ensure  => running,\n    enable  => true,\n    require => Package['mysql-server'],\n  }\n}"
        },
        
        # User and group management
        {
            "text": "# Create a user\nuser { 'webapp':\n  ensure => present,\n  uid    => 1001,\n  shell  => '/bin/bash',\n  home   => '/home/webapp',\n}"
        },
        {
            "text": "# Create a group\ngroup { 'webadmin':\n  ensure => present,\n  gid    => 1002,\n}"
        },
        
        # Exec resources
        {
            "text": "# Execute a command\nexec { 'update-packages':\n  command => '/usr/bin/apt-get update',\n  unless  => '/usr/bin/test -f /var/cache/apt/pkgcache.bin',\n}"
        },
        
        # Defined types
        {
            "text": "# Define a custom resource type\ndefine webapp::vhost (\n  String $docroot,\n  Integer $port = 80\n) {\n  file { \"/etc/apache2/sites-available/${title}.conf\":\n    ensure  => file,\n    content => template('webapp/vhost.erb'),\n    notify  => Service['apache2'],\n  }\n}"
        },
        
        # Node definitions
        {
            "text": "# Define a node\nnode 'webserver01.example.com' {\n  include webserver\n  include mysql\n}"
        },
        
        # Multiple resources
        {
            "text": "# Install and configure nginx\npackage { 'nginx':\n  ensure => installed,\n}\n\nservice { 'nginx':\n  ensure  => running,\n  enable  => true,\n  require => Package['nginx'],\n}\n\nfile { '/etc/nginx/nginx.conf':\n  ensure  => file,\n  source  => 'puppet:///modules/nginx/nginx.conf',\n  notify  => Service['nginx'],\n  require => Package['nginx'],\n}"
        },
        
        # Complex class example
        {
            "text": "# Complete web server setup\nclass lamp_stack {\n  # Install packages\n  package { ['apache2', 'mysql-server', 'php', 'libapache2-mod-php']:\n    ensure => installed,\n  }\n  \n  # Configure Apache\n  service { 'apache2':\n    ensure  => running,\n    enable  => true,\n    require => Package['apache2'],\n  }\n  \n  # Configure MySQL\n  service { 'mysql':\n    ensure  => running,\n    enable  => true,\n    require => Package['mysql-server'],\n  }\n  \n  # Create web directory\n  file { '/var/www/html/index.php':\n    ensure  => file,\n    content => '<?php phpinfo(); ?>',\n    require => Package['apache2'],\n  }\n}"
        }
    ]
    
    return examples

def main():
    """Create enhanced training dataset"""
    print("Creating enhanced Puppet training dataset...")
    
    examples = create_enhanced_puppet_dataset()
    
    # Save to file
    with open('../data_processing/puppet_enhanced_training.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2)
    
    print(f"Created enhanced dataset with {len(examples)} examples")
    print("Saved to: ../data_processing/puppet_enhanced_training.json")

if __name__ == "__main__":
    main()
