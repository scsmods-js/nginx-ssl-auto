"""
Nginx SSL Auto - Automated SSL certificate management for Nginx using Let's Encrypt.

This package provides tools to automatically set up and manage SSL certificates
for web applications using Nginx and Let's Encrypt.
"""

__version__ = "1.0.0"
__author__ = "dibbed"
__telegram__ = "@dibbed"
__description__ = "Automated SSL certificate management for Nginx using Let's Encrypt"

from .core import Config, remove_ssl_certificate, setup_ssl_certificate

__all__ = ["setup_ssl_certificate", "remove_ssl_certificate", "Config"]
