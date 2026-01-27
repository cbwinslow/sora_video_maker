#!/bin/bash

# Additional Tools Installation Script
set -e

echo "Installing additional tools..."

# Install yt-dlp for video downloading
pip install yt-dlp

# Install moviepy for video editing
pip install moviepy

# Install Pillow for image processing
pip install Pillow

# Install other useful libraries
pip install aiohttp asyncio requests beautifulsoup4 lxml

echo "Additional tools installed successfully!"
