"""
Core functionality for Nginx SSL Auto.

This module contains the main functions for setting up and managing SSL certificates
using Let's Encrypt and Nginx.
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage environment variables with defaults."""

    # Nginx configuration paths
    NGINX_SITES_AVAILABLE = os.getenv(
        "NGINX_SITES_AVAILABLE", "/etc/nginx/sites-available"
    )
    NGINX_SITES_ENABLED = os.getenv("NGINX_SITES_ENABLED", "/etc/nginx/sites-enabled")

    # Let's Encrypt configuration
    LETSENCRYPT_EMAIL_DOMAIN = os.getenv("LETSENCRYPT_EMAIL_DOMAIN", "admin")
    LETSENCRYPT_WEBROOT = os.getenv("LETSENCRYPT_WEBROOT", "/var/www/html")

    # SSL configuration
    SSL_PROTOCOLS = os.getenv("SSL_PROTOCOLS", "TLSv1.2 TLSv1.3")
    SSL_CIPHERS = os.getenv("SSL_CIPHERS", "HIGH:!aNULL:!MD5")

    # Default ports
    DEFAULT_HTTP_PORT = int(os.getenv("DEFAULT_HTTP_PORT", "80"))
    DEFAULT_HTTPS_PORT = int(os.getenv("DEFAULT_HTTPS_PORT", "443"))

    # System commands
    SUDO_COMMAND = os.getenv("SUDO_COMMAND", "sudo")
    APT_GET_COMMAND = os.getenv("APT_GET_COMMAND", "apt-get")
    SYSTEMCTL_COMMAND = os.getenv("SYSTEMCTL_COMMAND", "systemctl")

    # Timeout settings
    PORT_TEST_TIMEOUT = int(os.getenv("PORT_TEST_TIMEOUT", "10"))


class SSLCertificateManager:
    """Main class for managing SSL certificates."""

    def __init__(self, domain_name: str, forward_port: int):
        """
        Initialize SSL Certificate Manager.

        Args:
            domain_name: The domain name to manage SSL for
            forward_port: The port to forward traffic to
        """
        self.domain_name = domain_name
        self.forward_port = forward_port
        self.conf_file = f"{Config.NGINX_SITES_AVAILABLE}/{domain_name}.conf"
        self.symlink = f"{Config.NGINX_SITES_ENABLED}/{domain_name}.conf"

    def _install_tool(self, tool_name: str, install_command: str) -> None:
        """Install a required tool using package manager."""
        subprocess.run([Config.SUDO_COMMAND, Config.APT_GET_COMMAND, "update"])
        subprocess.run([Config.SUDO_COMMAND] + install_command.split())

    def _check_tools(self) -> Dict[str, Any]:
        """Check if required tools are installed."""
        required_tools = {
            "nginx": "Nginx",
            "certbot": "Certbot",
        }
        for tool, name in required_tools.items():
            if not shutil.which(tool):
                self._install_tool(name, f"{Config.APT_GET_COMMAND} install -y {tool}")
                return {
                    "mode": False,
                    "error": f"{name} is not installed on your system. Please install it and try again.",
                }
        return {"mode": True}

    def _validate_domain_name(self, domain: str) -> Dict[str, Any]:
        """Validate domain name format."""
        # More strict regex that prevents invalid patterns
        if not re.match(
            r"^(?!-)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$", domain
        ) or re.search(r"-\.|\.-|-$", domain):
            return {
                "mode": False,
                "error": "Invalid domain name. Please enter in the format 'example.com'.",
            }
        return {"mode": True}

    def _rollback(self) -> None:
        """Rollback changes in case of error."""
        if os.path.isfile(self.conf_file):
            subprocess.run([Config.SUDO_COMMAND, "rm", self.conf_file])
        if os.path.islink(self.symlink):
            subprocess.run([Config.SUDO_COMMAND, "rm", self.symlink])
        subprocess.run(
            [Config.SUDO_COMMAND, Config.SYSTEMCTL_COMMAND, "restart", "nginx"]
        )

    def _create_initial_nginx_conf(self) -> Dict[str, Any]:
        """Create initial Nginx configuration without SSL."""
        config_content = f"""server {{
		listen {Config.DEFAULT_HTTP_PORT};
		listen [::]:{Config.DEFAULT_HTTP_PORT};
		server_name {self.domain_name};
		location /.well-known/acme-challenge/ {{
			root {Config.LETSENCRYPT_WEBROOT};
		}}
		location / {{
			proxy_pass http://127.0.0.1:{self.forward_port};
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
		}}
	}}
	"""
        try:
            with open("temp_nginx.conf", "w") as f:
                f.write(config_content)
            subprocess.run(
                [Config.SUDO_COMMAND, "mv", "temp_nginx.conf", self.conf_file],
                check=True,
            )
            if os.path.islink(self.symlink):
                subprocess.run([Config.SUDO_COMMAND, "rm", self.symlink], check=True)
            subprocess.run(
                [Config.SUDO_COMMAND, "ln", "-sfn", self.conf_file, self.symlink],
                check=True,
            )
            subprocess.run([Config.SUDO_COMMAND, "nginx", "-t"], check=True)
            subprocess.run(
                [Config.SUDO_COMMAND, Config.SYSTEMCTL_COMMAND, "restart", "nginx"],
                check=True,
            )
        except subprocess.CalledProcessError:
            self._rollback()
            return {
                "mode": False,
                "error": "Error creating initial Nginx configuration or restarting it.",
            }
        return {"mode": True}

    def _obtain_ssl_certificate(self) -> Dict[str, Any]:
        """Obtain SSL certificate from Let's Encrypt."""
        try:
            subprocess.run(
                [
                    Config.SUDO_COMMAND,
                    "mkdir",
                    "-p",
                    f"{Config.LETSENCRYPT_WEBROOT}/.well-known/acme-challenge",
                ],
                check=True,
            )
            subprocess.run(
                [
                    Config.SUDO_COMMAND,
                    "certbot",
                    "certonly",
                    "--webroot",
                    "-w",
                    Config.LETSENCRYPT_WEBROOT,
                    "-d",
                    self.domain_name,
                    "--agree-tos",
                    "--email",
                    f"{Config.LETSENCRYPT_EMAIL_DOMAIN}@{self.domain_name}",
                    "--non-interactive",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            self._rollback()
            return {"mode": False, "error": "Error obtaining SSL certificate."}
        return {"mode": True}

    def _create_final_nginx_conf(self, ssl_redirect: bool = True) -> Dict[str, Any]:
        """Create final Nginx configuration with SSL."""
        config_content = f"""server {{
		listen {Config.DEFAULT_HTTP_PORT};
		listen [::]:{Config.DEFAULT_HTTP_PORT};
		server_name {self.domain_name};
		{"return 301 https://$host$request_uri;" if ssl_redirect else ""}
	}}
	server {{
		listen {Config.DEFAULT_HTTPS_PORT} ssl;
		listen [::]:{Config.DEFAULT_HTTPS_PORT} ssl;
		server_name {self.domain_name};
		ssl_certificate /etc/letsencrypt/live/{self.domain_name}/fullchain.pem;
		ssl_certificate_key /etc/letsencrypt/live/{self.domain_name}/privkey.pem;
		ssl_trusted_certificate /etc/letsencrypt/live/{self.domain_name}/chain.pem;
		ssl_protocols {Config.SSL_PROTOCOLS};
		ssl_ciphers {Config.SSL_CIPHERS};
		location / {{
			proxy_pass http://127.0.0.1:{self.forward_port};
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
		}}
	}}
	"""
        try:
            with open("temp_nginx.conf", "w") as f:
                f.write(config_content)
            subprocess.run(
                [Config.SUDO_COMMAND, "mv", "temp_nginx.conf", self.conf_file],
                check=True,
            )
            subprocess.run([Config.SUDO_COMMAND, "nginx", "-t"], check=True)
            subprocess.run(
                [Config.SUDO_COMMAND, Config.SYSTEMCTL_COMMAND, "restart", "nginx"],
                check=True,
            )
        except Exception:
            return {
                "mode": False,
                "error": "Error creating final Nginx configuration with SSL or restarting it.",
            }
        return {"mode": True}

    def _test_port_forward(self) -> Dict[str, Any]:
        """Test port connection."""
        try:
            response = subprocess.check_output(
                [
                    "curl",
                    "--write-out",
                    "%{http_code}",
                    "--silent",
                    "--output",
                    "/dev/null",
                    "--connect-timeout",
                    str(Config.PORT_TEST_TIMEOUT),
                    f"http://127.0.0.1:{self.forward_port}",
                ],
                timeout=Config.PORT_TEST_TIMEOUT,
            )
            if response.decode().strip() != "200":
                return {
                    "mode": False,
                    "error": f"Port {self.forward_port} is not responding correctly.",
                }
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return {
                "mode": False,
                "error": f"Port {self.forward_port} is not accessible or has timed out.",
            }
        return {"mode": True}

    def setup_ssl_certificate(
        self, ssl_redirect: bool = True, test_port: bool = False
    ) -> Dict[str, Any]:
        """
        Set up SSL certificate for the domain.

        Args:
            ssl_redirect: Whether to redirect HTTP to HTTPS
            test_port: Whether to test the forward port before setup

        Returns:
            Dictionary with success status and error message if applicable
        """
        # Execute overall process
        for step in [
            self._check_tools,
            lambda: self._validate_domain_name(self.domain_name),
        ]:
            result = step()
            if not result["mode"]:
                return result

        if test_port:
            result = self._test_port_forward()
            if not result["mode"]:
                return result

        # Continue with main steps
        for step in [
            self._create_initial_nginx_conf,
            self._obtain_ssl_certificate,
            lambda: self._create_final_nginx_conf(ssl_redirect),
        ]:
            result = step()
            if not result["mode"]:
                return result

        return {"mode": True}

    def remove_ssl_certificate(self) -> Dict[str, Any]:
        """
        Remove SSL certificate and Nginx configuration for the domain.

        Returns:
            Dictionary with success status and message
        """

        def delete_ssl_certificate() -> Dict[str, Any]:
            """Delete SSL certificate using Certbot."""
            try:
                subprocess.run(
                    [
                        Config.SUDO_COMMAND,
                        "certbot",
                        "delete",
                        "--cert-name",
                        self.domain_name,
                        "-n",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError:
                return {
                    "mode": False,
                    "error": f"Error deleting SSL certificate for domain {self.domain_name}.",
                }
            return {"mode": True}

        def delete_nginx_config() -> Dict[str, Any]:
            """Delete Nginx configuration files."""
            try:
                if os.path.isfile(self.conf_file):
                    subprocess.run(
                        [Config.SUDO_COMMAND, "rm", self.conf_file], check=True
                    )
                if os.path.islink(self.symlink):
                    subprocess.run(
                        [Config.SUDO_COMMAND, "rm", self.symlink], check=True
                    )
                subprocess.run([Config.SUDO_COMMAND, "nginx", "-t"], check=True)
                subprocess.run(
                    [Config.SUDO_COMMAND, Config.SYSTEMCTL_COMMAND, "restart", "nginx"],
                    check=True,
                )
            except subprocess.CalledProcessError:
                return {
                    "mode": False,
                    "error": f"Error deleting Nginx configuration for domain {self.domain_name} or restarting.",
                }
            return {"mode": True}

        # Execute removal steps
        for step in [delete_nginx_config, delete_ssl_certificate]:
            result = step()
            if not result["mode"]:
                return result

        return {
            "mode": True,
            "message": f"Domain {self.domain_name} and its SSL settings have been successfully removed.",
        }


def setup_ssl_certificate(
    domain_name: str,
    forward_port: int,
    ssl_redirect: bool = True,
    test_port: bool = False,
) -> Dict[str, Any]:
    """
    Set up SSL certificate for a domain using Let's Encrypt and Nginx.

    Args:
        domain_name: The domain name to set up SSL for
        forward_port: The port to forward traffic to
        ssl_redirect: Whether to redirect HTTP to HTTPS
        test_port: Whether to test the forward port before setup

    Returns:
        Dictionary with success status and error message if applicable
    """
    manager = SSLCertificateManager(domain_name, forward_port)
    return manager.setup_ssl_certificate(ssl_redirect, test_port)


def remove_ssl_certificate(domain_name: str) -> Dict[str, Any]:
    """
    Remove SSL certificate and Nginx configuration for a domain.

    Args:
        domain_name: The domain name to remove SSL for

    Returns:
        Dictionary with success status and message
    """
    # We need a forward_port for the manager, but it's not used for removal
    # Using a default value of 80
    manager = SSLCertificateManager(domain_name, 80)
    return manager.remove_ssl_certificate()


def check_ssl_expiry(domain_name: str) -> Dict[str, Any]:
    """
    Check the expiration of an SSL certificate using the OpenSSL command-line tool.

    Args:
        domain_name (str): The domain name (e.g., example.com)

    Returns:
        dict: Includes the status of the check and certificate validity
            - success (bool): True if the check was successful, False if an error occurred
            - is_active (bool, optional): True if the certificate is still valid, False if it has expired
            - error (str, optional): Error message in case of failure
    """
    cert_path = f"/etc/letsencrypt/live/{domain_name}/fullchain.pem"

    try:
        # Run openssl command to get the expiration date
        result = subprocess.check_output(
            ["openssl", "x509", "-in", cert_path, "-noout", "-enddate"],
            stderr=subprocess.STDOUT,
        ).decode("utf-8")

        # Extract the expiration date from the output
        expiry_date_str = result.split("=")[1].strip()
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y GMT")

        # Compare with the current date
        current_date = datetime.utcnow()
        is_active = expiry_date >= current_date

        return {"success": True, "is_active": is_active}

    except FileNotFoundError:
        return {
            "success": False,
            "error": "OpenSSL tool is not installed on the system. Please install it.",
        }
    except subprocess.CalledProcessError:
        return {
            "success": False,
            "error": f"Certificate file not found or unreadable at {cert_path}",
        }
    except ValueError:
        return {
            "success": False,
            "error": "Error parsing the certificate expiration date.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
        }
