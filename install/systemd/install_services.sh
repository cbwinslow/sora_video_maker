#!/bin/bash
# Install systemd services for video generation toolkit
#
# Usage: sudo ./install_services.sh [username]

set -e

USERNAME=${1:-$USER}

echo "Installing systemd services for user: $USERNAME"

# Copy service files
echo "Copying service files..."
sudo cp systemd/comfyui@.service /etc/systemd/system/
sudo cp systemd/ollama@.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable services
echo "Enabling services..."
sudo systemctl enable comfyui@$USERNAME
sudo systemctl enable ollama@$USERNAME

echo ""
echo "Services installed successfully!"
echo ""
echo "To start services:"
echo "  sudo systemctl start comfyui@$USERNAME"
echo "  sudo systemctl start ollama@$USERNAME"
echo ""
echo "To check status:"
echo "  sudo systemctl status comfyui@$USERNAME"
echo "  sudo systemctl status ollama@$USERNAME"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u comfyui@$USERNAME -f"
echo "  sudo journalctl -u ollama@$USERNAME -f"
