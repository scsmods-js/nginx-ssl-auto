# Nginx SSL Auto 🚀

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dibbed/nginx-ssl-auto/graphs/commit-activity)

Automated SSL certificate management for Nginx using Let's Encrypt. This tool simplifies the process of setting up and managing SSL certificates for your web applications.

## ✨ Features

- 🔐 **Automatic SSL Certificate Generation**: Uses Let's Encrypt to generate free SSL certificates
- 🌐 **Nginx Configuration Management**: Automatically creates and manages Nginx configuration files
- 🔄 **HTTP to HTTPS Redirect**: Optional automatic redirection from HTTP to HTTPS
- 🧪 **Port Testing**: Built-in port connectivity testing before SSL setup
- 🛡️ **Error Handling & Rollback**: Comprehensive error handling with automatic rollback on failures
- ⚙️ **Configurable**: Highly configurable through environment variables
- 🔧 **Tool Detection**: Automatic detection and installation of required tools (Nginx, Certbot)
- 🖥️ **CLI Interface**: Easy-to-use command-line interface
- 🚀 **Simple Runner**: Easy-to-use `run.py` script for quick setup
- 🔍 **SSL Certificate Monitoring**: Check SSL certificate expiry status

## 📋 Prerequisites

- Ubuntu/Debian-based Linux system
- Python 3.8 or higher
- Sudo privileges
- Domain name pointing to your server
- Running web application on a specific port

## 🚀 Installation

```bash
git clone https://github.com/dibbed/nginx-ssl-auto.git
cd nginx-ssl-auto
pip install -e .
```

### Setup Steps

1. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env file with your specific configuration
   ```

2. **Install system dependencies** (if not already installed):
   ```bash
   sudo apt-get update
   sudo apt-get install nginx certbot python3-certbot-nginx
   ```

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

| Variable                   | Default                      | Description                                  |
| -------------------------- | ---------------------------- | -------------------------------------------- |
| `NGINX_SITES_AVAILABLE`    | `/etc/nginx/sites-available` | Nginx sites-available directory              |
| `NGINX_SITES_ENABLED`      | `/etc/nginx/sites-enabled`   | Nginx sites-enabled directory                |
| `LETSENCRYPT_EMAIL_DOMAIN` | `admin`                      | Email domain for Let's Encrypt notifications |
| `LETSENCRYPT_WEBROOT`      | `/var/www/html`              | Webroot path for ACME challenges             |
| `SSL_PROTOCOLS`            | `TLSv1.2 TLSv1.3`            | SSL protocols to use                         |
| `SSL_CIPHERS`              | `HIGH:!aNULL:!MD5`           | SSL cipher suite                             |
| `DEFAULT_HTTP_PORT`        | `80`                         | Default HTTP port                            |
| `DEFAULT_HTTPS_PORT`       | `443`                        | Default HTTPS port                           |
| `SUDO_COMMAND`             | `sudo`                       | Sudo command path                            |
| `APT_GET_COMMAND`          | `apt-get`                    | Package manager command                      |
| `SYSTEMCTL_COMMAND`        | `systemctl`                  | System control command                       |
| `PORT_TEST_TIMEOUT`        | `10`                         | Port test timeout in seconds                 |

## 📖 Usage

### Simple Runner Script (Recommended)

The easiest way to use Nginx SSL Auto is through the simple `run.py` script:

```bash
# Set up SSL certificate
python run.py example.com 3000 setup

# Remove SSL certificate
python run.py example.com 3000 remove

# Check SSL certificate expiry
python run.py example.com 3000 check

# Domain is automatically converted to lowercase
python run.py EXAMPLE.COM 3000 setup  # Converts to example.com
```

### Command Line Interface

For more advanced usage, you can use the CLI:

```bash
# Set up SSL certificate
nginx-ssl-auto setup example.com 3000

# Set up SSL certificate with options
nginx-ssl-auto setup example.com 3000 --no-redirect --test-port

# Remove SSL certificate
nginx-ssl-auto remove example.com

# Check SSL certificate expiry
nginx-ssl-auto check example.com

# Show current configuration
nginx-ssl-auto config
```

### Python API

```python
from nginx_ssl_auto import setup_ssl_certificate, remove_ssl_certificate, check_ssl_expiry

# Set up SSL certificate for a domain
result = setup_ssl_certificate(
    domain_name="example.com",
    forward_port=3000,
    ssl_redirect=True,
    test_port=True
)

if result["mode"]:
    print("SSL certificate setup successful!")
else:
    print(f"Error: {result['error']}")

# Remove SSL certificate
result = remove_ssl_certificate("example.com")
if result["mode"]:
    print(result["message"])

# Check SSL certificate expiry
result = check_ssl_expiry("example.com")
if result["success"]:
    if result["is_active"]:
        print("SSL certificate is active and valid")
    else:
        print("SSL certificate has expired")
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage

```python
from nginx_ssl_auto import SSLCertificateManager

# Use the manager class directly
manager = SSLCertificateManager("example.com", 3000)
result = manager.setup_ssl_certificate(ssl_redirect=False, test_port=True)

# Custom configuration with environment variables
import os
os.environ['LETSENCRYPT_EMAIL_DOMAIN'] = 'webmaster'
os.environ['SSL_PROTOCOLS'] = 'TLSv1.3'
os.environ['PORT_TEST_TIMEOUT'] = '15'

result = setup_ssl_certificate(
    domain_name="myapp.com",
    forward_port=8080,
    ssl_redirect=False,  # Don't redirect HTTP to HTTPS
    test_port=True       # Test port before setup
)

# Check SSL certificate expiry
result = check_ssl_expiry("myapp.com")
if result["success"]:
    if result["is_active"]:
        print("✅ SSL certificate is active and valid")
    else:
        print("⚠️  SSL certificate has expired")
else:
    print(f"❌ Error: {result['error']}")

## 📁 Project Structure

```

nginx-ssl-auto/
├── nginx_ssl_auto/ # Main package
│ ├── **init**.py # Package initialization
│ ├── core.py # Core functionality
│ └── cli.py # Command-line interface
├── tests/ # Test suite
│ ├── **init**.py
│ ├── test_core.py # Core functionality tests
│ └── test_cli.py # CLI functionality tests
├── .env.example # Environment variables template
├── .gitignore # Git ignore rules
├── LICENSE # MIT license
├── README.md # This file
├── pyproject.toml # Project configuration
├── requirements.txt # Dependencies
└── run.py # Simple runner script

````

## 🔧 Configuration Examples

### Development Environment

```bash
# .env for development
LETSENCRYPT_EMAIL_DOMAIN=dev
LETSENCRYPT_WEBROOT=/var/www/dev
PORT_TEST_TIMEOUT=5
````

### Production Environment

```bash
# .env for production
LETSENCRYPT_EMAIL_DOMAIN=admin
SSL_PROTOCOLS=TLSv1.3
SSL_CIPHERS=HIGH:!aNULL:!MD5:!RC4:!MD5:!aNULL
PORT_TEST_TIMEOUT=30
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=nginx_ssl_auto

# Run specific tests
pytest tests/test_core.py::TestSSLCertificateManager::test_validate_domain_name_valid
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have sudo privileges

   ```bash
   sudo -l
   ```

2. **Nginx Not Found**: Install Nginx if not present

   ```bash
   sudo apt-get install nginx
   ```

3. **Certbot Not Found**: Install Certbot

   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

4. **Port Not Accessible**: Check if your application is running

   ```bash
   netstat -tlnp | grep :3000
   ```

5. **OpenSSL Not Found**: Install OpenSSL for certificate checking
   ```bash
   sudo apt-get install openssl
   ```

### Debug Mode

Enable debug logging:

```bash
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from nginx_ssl_auto import setup_ssl_certificate, check_ssl_expiry
setup_ssl_certificate('example.com', 3000)
check_ssl_expiry('example.com')
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/dibbed/nginx-ssl-auto.git
cd nginx-ssl-auto
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Author**: dibbed
- **GitHub**: [@dibbed](https://github.com/dibbed)
- **Project Link**: [https://github.com/dibbed/nginx-ssl-auto](https://github.com/dibbed/nginx-ssl-auto)

## 🙏 Acknowledgments

- [Let's Encrypt](https://letsencrypt.org/) for providing free SSL certificates
- [Certbot](https://certbot.eff.org/) for the certificate automation tool
- [Nginx](https://nginx.org/) for the web server

---

⭐ If this project helped you, please give it a star!
