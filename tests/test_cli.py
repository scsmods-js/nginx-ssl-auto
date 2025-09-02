"""
Tests for CLI functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from nginx_ssl_auto.cli import create_parser, show_config, setup_command, remove_command, main


class TestCLI:
    """Test CLI functionality."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
        assert parser.description == "Automated SSL certificate management for Nginx using Let's Encrypt"

    def test_show_config(self, capsys):
        """Test config display."""
        show_config()
        captured = capsys.readouterr()
        assert "Current Configuration" in captured.out
        assert "Nginx sites-available" in captured.out
        assert "Let's Encrypt email domain" in captured.out

    @patch('nginx_ssl_auto.cli.setup_ssl_certificate')
    def test_setup_command_success(self, mock_setup):
        """Test successful setup command."""
        mock_setup.return_value = {"mode": True}
        
        args = MagicMock()
        args.domain = "example.com"
        args.port = 3000
        args.no_redirect = False
        args.test_port = False
        
        result = setup_command(args)
        assert result == 0
        mock_setup.assert_called_once_with(
            domain_name="example.com",
            forward_port=3000,
            ssl_redirect=True,
            test_port=False
        )

    @patch('nginx_ssl_auto.cli.setup_ssl_certificate')
    def test_setup_command_failure(self, mock_setup):
        """Test failed setup command."""
        mock_setup.return_value = {"mode": False, "error": "Test error"}
        
        args = MagicMock()
        args.domain = "example.com"
        args.port = 3000
        args.no_redirect = True
        args.test_port = True
        
        result = setup_command(args)
        assert result == 1
        mock_setup.assert_called_once_with(
            domain_name="example.com",
            forward_port=3000,
            ssl_redirect=False,
            test_port=True
        )

    @patch('nginx_ssl_auto.cli.remove_ssl_certificate')
    def test_remove_command_success(self, mock_remove):
        """Test successful remove command."""
        mock_remove.return_value = {"mode": True, "message": "Success"}
        
        args = MagicMock()
        args.domain = "example.com"
        
        result = remove_command(args)
        assert result == 0
        mock_remove.assert_called_once_with("example.com")

    @patch('nginx_ssl_auto.cli.remove_ssl_certificate')
    def test_remove_command_failure(self, mock_remove):
        """Test failed remove command."""
        mock_remove.return_value = {"mode": False, "error": "Test error"}
        
        args = MagicMock()
        args.domain = "example.com"
        
        result = remove_command(args)
        assert result == 1
        mock_remove.assert_called_once_with("example.com")

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_no_command(self, mock_create_parser):
        """Test main function with no command."""
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = None
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        result = main([])
        assert result == 1
        mock_parser.print_help.assert_called_once()

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_setup_command(self, mock_create_parser):
        """Test main function with setup command."""
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = "setup"
        mock_args.domain = "example.com"
        mock_args.port = 3000
        mock_args.no_redirect = False
        mock_args.test_port = False
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        with patch('nginx_ssl_auto.cli.setup_command') as mock_setup:
            mock_setup.return_value = 0
            result = main(["setup", "example.com", "3000"])
            assert result == 0
            mock_setup.assert_called_once_with(mock_args)

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_remove_command(self, mock_create_parser):
        """Test main function with remove command."""
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = "remove"
        mock_args.domain = "example.com"
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        with patch('nginx_ssl_auto.cli.remove_command') as mock_remove:
            mock_remove.return_value = 0
            result = main(["remove", "example.com"])
            assert result == 0
            mock_remove.assert_called_once_with(mock_args)

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_config_command(self, mock_create_parser):
        """Test main function with config command."""
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        with patch('nginx_ssl_auto.cli.show_config') as mock_show_config:
            result = main(["config"])
            assert result == 0
            mock_show_config.assert_called_once()

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_unknown_command(self, mock_create_parser):
        """Test main function with unknown command."""
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = "unknown"
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        result = main(["unknown"])
        assert result == 1

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_keyboard_interrupt(self, mock_create_parser):
        """Test main function with keyboard interrupt."""
        mock_parser = MagicMock()
        mock_parser.parse_args.side_effect = KeyboardInterrupt()
        mock_create_parser.return_value = mock_parser
        
        result = main([])
        assert result == 1

    @patch('nginx_ssl_auto.cli.create_parser')
    def test_main_exception(self, mock_create_parser):
        """Test main function with exception."""
        mock_parser = MagicMock()
        mock_parser.parse_args.side_effect = Exception("Test exception")
        mock_create_parser.return_value = mock_parser
        
        result = main([])
        assert result == 1

