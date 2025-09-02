#!/usr/bin/env python3
"""
Simple runner script for Nginx SSL Auto.
Takes domain and port from command line arguments.
"""

import sys

from nginx_ssl_auto.core import remove_ssl_certificate, setup_ssl_certificate, check_ssl_expiry


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python run.py <domain> <port> [setup|remove|check]")
        print("Example: python run.py example.com 3000 setup")
        print("Example: python run.py example.com 3000 remove")
        print("Example: python run.py example.com 3000 check")
        sys.exit(1)

    # Get arguments
    domain = sys.argv[1].lower()  # Convert to lowercase
    port = int(sys.argv[2])
    action = sys.argv[3] if len(sys.argv) > 3 else "setup"

    print(f"🔧 Domain: {domain}")
    print(f"📡 Port: {port}")
    print(f"⚡ Action: {action}")
    print("-" * 50)

    try:
        if action.lower() == "setup":
            print("🚀 Setting up SSL certificate...")
            result = setup_ssl_certificate(domain, port)

            if result["mode"]:
                print("✅ SSL certificate setup successful!")
                print(f"🌐 Your site is now available at: https://{domain}")
            else:
                print(f"❌ Error: {result['error']}")
                sys.exit(1)

        elif action.lower() == "remove":
            print("🗑️ Removing SSL certificate...")
            result = remove_ssl_certificate(domain)

            if result["mode"]:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Error: {result['error']}")
                sys.exit(1)

        elif action.lower() == "check":
            print("🔍 Checking SSL certificate expiry...")
            result = check_ssl_expiry(domain)

            if result["success"]:
                if result["is_active"]:
                    print("✅ SSL certificate is active and valid")
                else:
                    print("⚠️  SSL certificate has expired")
            else:
                print(f"❌ Error: {result['error']}")
                sys.exit(1)

        else:
            print(f"❌ Unknown action: {action}")
            print("Available actions: setup, remove, check")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
