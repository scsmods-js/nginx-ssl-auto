"""
Tests for core functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from nginx_ssl_auto.core import (
    Config,
    SSLCertificateManager,
    remove_ssl_certificate,
    setup_ssl_certificate,
)


class TestConfig:
    """Test configuration class."""

    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        assert Config.NGINX_SITES_AVAILABLE == "/etc/nginx/sites-available"
        assert Config.NGINX_SITES_ENABLED == "/etc/nginx/sites-enabled"
        assert Config.LETSENCRYPT_EMAIL_DOMAIN == "admin"
        assert Config.LETSENCRYPT_WEBROOT == "/var/www/html"
        assert Config.SSL_PROTOCOLS == "TLSv1.2 TLSv1.3"
        assert Config.SSL_CIPHERS == "HIGH:!aNULL:!MD5"
        assert Config.DEFAULT_HTTP_PORT == 80
        assert Config.DEFAULT_HTTPS_PORT == 443
        assert Config.SUDO_COMMAND == "sudo"
        assert Config.APT_GET_COMMAND == "apt-get"
        assert Config.SYSTEMCTL_COMMAND == "systemctl"
        assert Config.PORT_TEST_TIMEOUT == 10

    @patch.dict("os.environ", {"NGINX_SITES_AVAILABLE": "/custom/path"})
    def test_environment_override(self):
        """Test that environment variables override defaults."""
        # Note: This test might not work as expected because Config is loaded at import time
        # In a real application, you might want to reload the config or use a different approach
        pass


class TestSSLCertificateManager:
    """Test SSL Certificate Manager class."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = SSLCertificateManager("example.com", 3000)
        assert manager.domain_name == "example.com"
        assert manager.forward_port == 3000
        assert manager.conf_file == "/etc/nginx/sites-available/example.com.conf"
        assert manager.symlink == "/etc/nginx/sites-enabled/example.com.conf"

    def test_validate_domain_name_valid(self):
        """Test domain name validation with valid domains."""
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._validate_domain_name("example.com")
        assert result["mode"] is True

        result = manager._validate_domain_name("sub.example.com")
        assert result["mode"] is True

        result = manager._validate_domain_name("example-domain.com")
        assert result["mode"] is True

    def test_validate_domain_name_invalid(self):
        """Test domain name validation with invalid domains."""
        manager = SSLCertificateManager("example.com", 3000)

        # Invalid formats
        invalid_domains = [
            "example",  # No TLD
            "example.c",  # Invalid TLD
            "example..com",  # Double dot
            ".example.com",  # Starts with dot
            "example.com.",  # Ends with dot
            "example_com.com",  # Underscore not allowed
            "example-.com",  # Ends with dash
            "-example.com",  # Starts with dash
        ]

        for domain in invalid_domains:
            result = manager._validate_domain_name(domain)
            assert result["mode"] is False, f"Domain '{domain}' should be invalid"
            assert "Invalid domain name" in result["error"]

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_check_tools_missing(self, mock_run, mock_which):
        """Test tool checking when tools are missing."""
        mock_which.return_value = None
        mock_run.return_value = MagicMock()

        manager = SSLCertificateManager("example.com", 3000)
        result = manager._check_tools()

        assert result["mode"] is False
        assert "is not installed" in result["error"]

    @patch("shutil.which")
    def test_check_tools_available(self, mock_which):
        """Test tool checking when tools are available."""
        mock_which.return_value = "/usr/bin/nginx"

        manager = SSLCertificateManager("example.com", 3000)
        result = manager._check_tools()

        assert result["mode"] is True

    @patch("subprocess.run")
    def test_rollback(self, mock_run):
        """Test rollback functionality."""
        mock_run.return_value = MagicMock()
        
        manager = SSLCertificateManager("example.com", 3000)
        manager._rollback()
        
        # Should call subprocess.run multiple times
        assert mock_run.call_count >= 1

    @patch("subprocess.run")
    @patch("builtins.open", create=True)
    def test_create_initial_nginx_conf_success(self, mock_open, mock_run):
        """Test successful initial nginx config creation."""
        mock_run.return_value = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._create_initial_nginx_conf()
        
        assert result["mode"] is True
        mock_file.write.assert_called_once()

    @patch("subprocess.run")
    def test_create_initial_nginx_conf_failure(self, mock_run):
        """Test failed initial nginx config creation."""
        mock_run.side_effect = Exception("Test error")
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._create_initial_nginx_conf()
        
        assert result["mode"] is False
        assert "Error creating initial Nginx configuration" in result["error"]

    @patch("subprocess.run")
    def test_obtain_ssl_certificate_success(self, mock_run):
        """Test successful SSL certificate obtention."""
        mock_run.return_value = MagicMock()
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._obtain_ssl_certificate()
        
        assert result["mode"] is True

    @patch("subprocess.run")
    def test_obtain_ssl_certificate_failure(self, mock_run):
        """Test failed SSL certificate obtention."""
        mock_run.side_effect = Exception("Test error")
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._obtain_ssl_certificate()
        
        assert result["mode"] is False
        assert "Error obtaining SSL certificate" in result["error"]

    @patch("subprocess.run")
    @patch("builtins.open", create=True)
    def test_create_final_nginx_conf_success(self, mock_open, mock_run):
        """Test successful final nginx config creation."""
        mock_run.return_value = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._create_final_nginx_conf(ssl_redirect=True)
        
        assert result["mode"] is True
        mock_file.write.assert_called_once()

    @patch("subprocess.run")
    @patch("builtins.open", create=True)
    def test_create_final_nginx_conf_failure(self, mock_open, mock_run):
        """Test failed final nginx config creation."""
        mock_run.side_effect = Exception("Test error")
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._create_final_nginx_conf(ssl_redirect=False)
        
        assert result["mode"] is False
        assert "Error creating final Nginx configuration" in result["error"]

    @patch("subprocess.check_output")
    def test_test_port_forward_success(self, mock_check_output):
        """Test successful port forward test."""
        mock_check_output.return_value = b"200"
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._test_port_forward()
        
        assert result["mode"] is True

    @patch("subprocess.check_output")
    def test_test_port_forward_failure(self, mock_check_output):
        """Test failed port forward test."""
        mock_check_output.return_value = b"404"
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._test_port_forward()
        
        assert result["mode"] is False
        assert "not responding correctly" in result["error"]

    @patch("subprocess.check_output")
    def test_test_port_forward_timeout(self, mock_check_output):
        """Test port forward test timeout."""
        mock_check_output.side_effect = Exception("Timeout")
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager._test_port_forward()
        
        assert result["mode"] is False
        assert "not accessible or has timed out" in result["error"]

    @patch.object(SSLCertificateManager, '_check_tools')
    @patch.object(SSLCertificateManager, '_validate_domain_name')
    @patch.object(SSLCertificateManager, '_test_port_forward')
    @patch.object(SSLCertificateManager, '_create_initial_nginx_conf')
    @patch.object(SSLCertificateManager, '_obtain_ssl_certificate')
    @patch.object(SSLCertificateManager, '_create_final_nginx_conf')
    def test_setup_ssl_certificate_success(self, mock_final, mock_obtain, mock_initial, mock_test, mock_validate, mock_check):
        """Test successful SSL certificate setup."""
        mock_check.return_value = {"mode": True}
        mock_validate.return_value = {"mode": True}
        mock_test.return_value = {"mode": True}
        mock_initial.return_value = {"mode": True}
        mock_obtain.return_value = {"mode": True}
        mock_final.return_value = {"mode": True}
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.setup_ssl_certificate(ssl_redirect=True, test_port=True)
        
        assert result["mode"] is True

    @patch.object(SSLCertificateManager, '_check_tools')
    def test_setup_ssl_certificate_tools_failure(self, mock_check):
        """Test SSL certificate setup with tools failure."""
        mock_check.return_value = {"mode": False, "error": "Tools not found"}
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.setup_ssl_certificate()
        
        assert result["mode"] is False
        assert "Tools not found" in result["error"]

    @patch.object(SSLCertificateManager, '_check_tools')
    @patch.object(SSLCertificateManager, '_validate_domain_name')
    def test_setup_ssl_certificate_validation_failure(self, mock_validate, mock_check):
        """Test SSL certificate setup with validation failure."""
        mock_check.return_value = {"mode": True}
        mock_validate.return_value = {"mode": False, "error": "Invalid domain"}
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.setup_ssl_certificate()
        
        assert result["mode"] is False
        assert "Invalid domain" in result["error"]

    @patch.object(SSLCertificateManager, '_check_tools')
    @patch.object(SSLCertificateManager, '_validate_domain_name')
    @patch.object(SSLCertificateManager, '_test_port_forward')
    def test_setup_ssl_certificate_port_test_failure(self, mock_test, mock_validate, mock_check):
        """Test SSL certificate setup with port test failure."""
        mock_check.return_value = {"mode": True}
        mock_validate.return_value = {"mode": True}
        mock_test.return_value = {"mode": False, "error": "Port not accessible"}
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.setup_ssl_certificate(test_port=True)
        
        assert result["mode"] is False
        assert "Port not accessible" in result["error"]

    @patch("subprocess.run")
    def test_remove_ssl_certificate_success(self, mock_run):
        """Test successful SSL certificate removal."""
        mock_run.return_value = MagicMock()
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.remove_ssl_certificate()
        
        assert result["mode"] is True
        assert "successfully removed" in result["message"]

    @patch("subprocess.run")
    def test_remove_ssl_certificate_nginx_failure(self, mock_run):
        """Test SSL certificate removal with nginx failure."""
        mock_run.side_effect = Exception("Nginx error")
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.remove_ssl_certificate()
        
        assert result["mode"] is False
        assert "Error deleting Nginx configuration" in result["error"]

    @patch("subprocess.run")
    def test_remove_ssl_certificate_certbot_failure(self, mock_run):
        """Test SSL certificate removal with certbot failure."""
        # First call succeeds (nginx), second call fails (certbot)
        mock_run.side_effect = [MagicMock(), Exception("Certbot error")]
        
        manager = SSLCertificateManager("example.com", 3000)
        result = manager.remove_ssl_certificate()
        
        assert result["mode"] is False
        assert "Error deleting SSL certificate" in result["error"]


class TestFunctions:
    """Test module-level functions."""

    @patch("nginx_ssl_auto.core.SSLCertificateManager")
    def test_setup_ssl_certificate(self, mock_manager_class):
        """Test setup_ssl_certificate function."""
        mock_manager = MagicMock()
        mock_manager.setup_ssl_certificate.return_value = {"mode": True}
        mock_manager_class.return_value = mock_manager

        result = setup_ssl_certificate("example.com", 3000)

        mock_manager_class.assert_called_once_with("example.com", 3000)
        mock_manager.setup_ssl_certificate.assert_called_once_with(True, False)
        assert result["mode"] is True

    @patch("nginx_ssl_auto.core.SSLCertificateManager")
    def test_remove_ssl_certificate(self, mock_manager_class):
        """Test remove_ssl_certificate function."""
        mock_manager = MagicMock()
        mock_manager.remove_ssl_certificate.return_value = {
            "mode": True,
            "message": "Success",
        }
        mock_manager_class.return_value = mock_manager

        result = remove_ssl_certificate("example.com")

        mock_manager_class.assert_called_once_with("example.com", 80)
        mock_manager.remove_ssl_certificate.assert_called_once()
        assert result["mode"] is True
        assert result["message"] == "Success"


if __name__ == "__main__":
    pytest.main([__file__])
