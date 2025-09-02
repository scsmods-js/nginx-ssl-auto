"""
Command-line interface for Nginx SSL Auto.
"""

import argparse
import sys
from typing import Optional

from .core import (
    Config,
    check_ssl_expiry,
    remove_ssl_certificate,
    setup_ssl_certificate,
)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automated SSL certificate management for Nginx using Let's Encrypt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup example.com 3000
  %(prog)s setup example.com 3000 --no-redirect --test-port
  %(prog)s remove example.com
  %(prog)s check example.com
  %(prog)s config
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Set up SSL certificate for a domain"
    )
    setup_parser.add_argument(
        "domain", help="Domain name to set up SSL for (e.g., example.com)"
    )
    setup_parser.add_argument(
        "port", type=int, help="Port to forward traffic to (e.g., 3000)"
    )
    setup_parser.add_argument(
        "--no-redirect",
        action="store_true",
        help="Don't redirect HTTP to HTTPS",
    )
    setup_parser.add_argument(
        "--test-port",
        action="store_true",
        help="Test port connectivity before setup",
    )

    # Remove command
    remove_parser = subparsers.add_parser(
        "remove", help="Remove SSL certificate for a domain"
    )
    remove_parser.add_argument("domain", help="Domain name to remove SSL from")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check SSL certificate expiry")
    check_parser.add_argument("domain", help="Domain name to check SSL expiry for")

    # Config command
    config_parser = subparsers.add_parser("config", help="Show current configuration")

    return parser


def show_config() -> None:
    """Display current configuration."""
    print("🔧 Current Configuration:")
    print("=" * 50)
    print(f"📁 Nginx sites-available: {Config.NGINX_SITES_AVAILABLE}")
    print(f"📁 Nginx sites-enabled: {Config.NGINX_SITES_ENABLED}")
    print(f"📧 Let's Encrypt email domain: {Config.LETSENCRYPT_EMAIL_DOMAIN}")
    print(f"🌐 Webroot path: {Config.LETSENCRYPT_WEBROOT}")
    print(f"🔒 SSL protocols: {Config.SSL_PROTOCOLS}")
    print(f"🔐 SSL ciphers: {Config.SSL_CIPHERS}")
    print(f"🌐 Default HTTP port: {Config.DEFAULT_HTTP_PORT}")
    print(f"🔒 Default HTTPS port: {Config.DEFAULT_HTTPS_PORT}")
    print(f"⚡ Sudo command: {Config.SUDO_COMMAND}")
    print(f"📦 Package manager: {Config.APT_GET_COMMAND}")
    print(f"🔧 System control: {Config.SYSTEMCTL_COMMAND}")
    print(f"⏱️  Port test timeout: {Config.PORT_TEST_TIMEOUT} seconds")


def setup_command(args: argparse.Namespace) -> int:
    """Handle setup command."""
    print(f"🚀 Setting up SSL certificate for {args.domain}")
    print(f"📡 Forwarding traffic to port {args.port}")
    print("-" * 50)

    result = setup_ssl_certificate(
        domain_name=args.domain,
        forward_port=args.port,
        ssl_redirect=not args.no_redirect,
        test_port=args.test_port,
    )

    if result["mode"]:
        print("✅ SSL certificate setup successful!")
        print(f"🌐 Your site is now available at: https://{args.domain}")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def remove_command(args: argparse.Namespace) -> int:
    """Handle remove command."""
    print(f"🗑️  Removing SSL certificate for {args.domain}")
    print("-" * 50)

    result = remove_ssl_certificate(args.domain)

    if result["mode"]:
        print(f"✅ {result['message']}")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def check_command(args: argparse.Namespace) -> int:
    """Handle check command."""
    print(f"🔍 Checking SSL certificate expiry for {args.domain}")
    print("-" * 50)

    result = check_ssl_expiry(args.domain)

    if result["success"]:
        if result["is_active"]:
            print("✅ SSL certificate is active and valid")
        else:
            print("⚠️  SSL certificate has expired")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "setup":
            return setup_command(args)
        elif args.command == "remove":
            return remove_command(args)
        elif args.command == "check":
            return check_command(args)
        elif args.command == "config":
            show_config()
            return 0
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
