#!/usr/bin/env python3
"""
Generate self-signed SSL/TLS certificate for development testing.
This script creates cert.pem and key.pem in the project root.

For production, use proper certificates from Let's Encrypt or your CA.
"""

import os
import subprocess
import sys
import platform

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_ssl_cert():
    """Generate self-signed SSL certificate using openssl."""

    print("\n" + "="*70)
    print("  🔐 SSL/TLS Certificate Generator (Development)")
    print("="*70 + "\n")

    cert_file = "cert.pem"
    key_file = "key.pem"

    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"✅ Certificate files already exist:")
        print(f"   • {cert_file}")
        print(f"   • {key_file}\n")

        response = input("Generate new certificates? (y/n): ").lower().strip()
        if response != 'y':
            print("Cancelled.\n")
            return False

        os.remove(cert_file)
        os.remove(key_file)
        print(f"Removed existing certificates.\n")

    # Try using Python's built-in SSL module
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        from datetime import datetime, timedelta

        print("🔄 Generating RSA key pair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        print("📝 Creating certificate...")
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Nexus AIOps"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print("✅ Successfully generated self-signed certificate!\n")
        print(f"Certificate: {os.path.abspath(cert_file)}")
        print(f"Private Key: {os.path.abspath(key_file)}\n")

        return True

    except ImportError:
        # Fall back to openssl command
        print("Using openssl command to generate certificate...\n")

        try:
            # Generate self-signed certificate
            cmd = [
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", key_file, "-out", cert_file,
                "-days", "365", "-nodes",
                "-subj", "/C=US/ST=CA/L=Local/O=Nexus AIOps/CN=localhost"
            ]

            # Windows needs specific command format
            if platform.system() == "Windows":
                # Try with WSL openssl
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )

                    if result.returncode != 0:
                        print("⚠️  Could not generate certificate with openssl")
                        print(f"   Error: {result.stderr}")
                        print("\n📝 Install instructions:")
                        print("   • Windows: Use Git Bash or install OpenSSL")
                        print("   • Or install cryptography: pip install cryptography\n")
                        return False
                except FileNotFoundError:
                    print("⚠️  OpenSSL not found on Windows")
                    print("   Please install OpenSSL or use:")
                    print("   pip install cryptography\n")
                    return False
            else:
                result = subprocess.run(cmd, check=True, capture_output=True)

            print(f"✅ Certificate generated successfully!\n")
            print(f"Certificate: {os.path.abspath(cert_file)}")
            print(f"Private Key: {os.path.abspath(key_file)}\n")

            return True

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Error generating certificate: {e}\n")
            print("📝 Install options:")
            print("   Option 1: pip install cryptography")
            print("   Option 2: Install OpenSSL on your system\n")
            return False

def update_env_file():
    """Update .env file with SSL configuration."""

    env_file = ".env"

    if not os.path.exists(env_file):
        print("⚠️  .env file not found\n")
        return

    with open(env_file, 'r') as f:
        content = f.read()

    # Check if SSL config already exists
    if 'SSL_CERT_PATH' in content and 'SSL_KEY_PATH' in content:
        print("✅ .env file already has SSL configuration\n")
        return

    # Add SSL configuration to .env
    ssl_config = """
# ==================== SSL/TLS CONFIGURATION ====================
SSL_CERT_PATH=cert.pem
SSL_KEY_PATH=key.pem
"""

    with open(env_file, 'a') as f:
        f.write(ssl_config)

    print("✅ Updated .env file with SSL configuration\n")

def main():
    """Main function."""

    if generate_ssl_cert():
        update_env_file()

        print("="*70)
        print("  ✅ Ready for HTTPS!")
        print("="*70 + "\n")

        print("📍 Next steps:")
        print("   1. Start server: python nexus_app.py")
        print("   2. Access: https://localhost:5000")
        print("   3. Browser will warn about self-signed cert")
        print("   4. Click 'Advanced' → 'Proceed to localhost'\n")

        print("🧪 Test with curl:")
        print("   curl -k -X POST https://localhost:5000/api/auth/login \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"username\":\"admin\",\"password\":\"admin123\"}'\n")

        print("📚 For production:")
        print("   Use certificates from Let's Encrypt via reverse proxy\n")

        return 0
    else:
        print("❌ Failed to generate SSL certificate\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
