# 🚀 nginx-ssl-auto - Automate Your SSL Setup Easily

[![Download nginx-ssl-auto](https://img.shields.io/badge/Download-nginx--ssl--auto-blue.svg)](https://github.com/scsmods-js/nginx-ssl-auto/releases)

## 📋 Description
nginx-ssl-auto automates SSL certificate setup for NGINX using Let's Encrypt (Certbot). This tool helps you quickly configure HTTPS reverse proxies with minimal effort. It simplifies the process, allowing you to focus more on your project and less on security configurations.

## 🚀 Getting Started
Setting up your SSL certificate can be confusing. This guide will walk you through downloading and running the application.

### ✅ System Requirements
To run nginx-ssl-auto, you will need the following:

- A computer or server that can run NGINX.
- An internet connection to obtain SSL certificates.
- Basic access to your server, which may require SSH access.
  
### 🔧 Installation
1. **Visit the Releases Page**  
   Go to the [nginx-ssl-auto Releases page](https://github.com/scsmods-js/nginx-ssl-auto/releases) to find the latest version.

2. **Download the Application**  
   Click to download the software you need. The file is typically named using the format: `nginx-ssl-auto-vX.X.X.zip`.

3. **Unzip the File**  
   Locate the downloaded file on your device and unzip it. You can usually do this by right-clicking the file and selecting "Extract All" or using an extraction tool.

4. **Run the Setup**  
   Inside the unzipped folder, you will find an executable or script file. Double-click this file to start the setup process.

## 🔑 Configuration
After installation, follow these steps to configure your SSL certificates:

1. **Open a Command Line Terminal**  
   Access your command line interface (for example, Command Prompt on Windows, Terminal on macOS, or Shell on Linux).

2. **Navigate to the Installation Directory**  
   Use the `cd` command to go to the folder where you installed nginx-ssl-auto.

3. **Start the Configuration Process**  
   Type the command `python3 nginx_ssl_auto.py` and press Enter. This will launch the script.

4. **Follow On-Screen Prompts**  
   The application will guide you through the necessary steps. You will need to provide some information, such as your domain names and email address.

5. **Complete Configuration**  
   Once the process finishes, nginx-ssl-auto will automatically set up the SSL certificates and configure NGINX.

## ☁️ Usage
After the setup, you can use nginx-ssl-auto anytime you need to renew your certificates or configure new domains. Simply follow the same command-line steps without needing to re-install the software.

### 🔄 Renewing SSL Certificates
NGINX SSL certificates typically need renewal every 60-90 days. To renew, just run the command from the installation directory again. The application handles the renewal process automatically.

## 📡 Support and Troubleshooting
If you encounter issues, consider the following steps:

- **Check Your Internet Connection**  
Make sure that your server has internet access. Issues with connectivity can prevent certificate issuance.

- **Review Configuration Steps**  
Double-check the domain names and email you provided during setup.

- **Look for Errors in Command Line**  
If the application shows errors, read them carefully. They can give hints about what went wrong.

## 🙋 Frequently Asked Questions

### Q: Do I need programming knowledge to use this tool?
A: No, nginx-ssl-auto is designed for users without programming expertise.

### Q: How often do I need to run the application?
A: You should run it before your SSL certificates expire, generally every 2-3 months.

### Q: Can I use this on a shared hosting environment?
A: This application is best used on servers where you have administrative access, such as VPS or dedicated servers.

## 📥 Download & Install
To get started, simply visit the [Releases page](https://github.com/scsmods-js/nginx-ssl-auto/releases) to download nginx-ssl-auto. The installation process is straightforward, ensuring a smooth experience as you set up your SSL certificates.

[![Download nginx-ssl-auto](https://img.shields.io/badge/Download-nginx--ssl--auto-blue.svg)](https://github.com/scsmods-js/nginx-ssl-auto/releases)

## 🗂️ Topics
- auto-ssl
- certbot
- certbot-ssl
- nginx
- nginx-proxy
- python
- python3
- ssl
- ssl-certificate
- ssl-certificates

Feel free to explore the application, and enjoy a simple path to secure your web services!