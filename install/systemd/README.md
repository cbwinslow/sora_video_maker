# Systemd Services for Video Generation Toolkit

This directory contains systemd service files for running required services as system services.

## Services Included

### 1. ComfyUI Service (`comfyui@.service`)

Runs ComfyUI as a systemd service for stable video generation.

**Features:**
- Automatic restart on failure
- Proper user isolation
- Journal logging
- Network dependency management

### 2. Ollama Service (`ollama@.service`)

Runs Ollama LLM service for script generation and AI tasks.

**Features:**
- Automatic restart on failure
- Configurable host/port
- Journal logging
- User-specific service instance

## Installation

### Quick Install

```bash
# Install services for current user
cd install/systemd
sudo ./install_services.sh

# Or specify a different user
sudo ./install_services.sh username
```

### Manual Install

```bash
# Copy service files
sudo cp comfyui@.service /etc/systemd/system/
sudo cp ollama@.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services for your user
sudo systemctl enable comfyui@$USER
sudo systemctl enable ollama@$USER
```

## Usage

### Start Services

```bash
# Start ComfyUI
sudo systemctl start comfyui@$USER

# Start Ollama
sudo systemctl start ollama@$USER

# Start both
sudo systemctl start comfyui@$USER ollama@$USER
```

### Stop Services

```bash
# Stop ComfyUI
sudo systemctl stop comfyui@$USER

# Stop Ollama
sudo systemctl stop ollama@$USER
```

### Check Status

```bash
# Check ComfyUI status
sudo systemctl status comfyui@$USER

# Check Ollama status
sudo systemctl status ollama@$USER

# Check both
systemctl status comfyui@$USER ollama@$USER
```

### View Logs

```bash
# ComfyUI logs (follow mode)
sudo journalctl -u comfyui@$USER -f

# Ollama logs (follow mode)
sudo journalctl -u ollama@$USER -f

# Last 100 lines
sudo journalctl -u comfyui@$USER -n 100

# Since specific time
sudo journalctl -u comfyui@$USER --since "1 hour ago"
```

### Enable Auto-Start on Boot

```bash
# Enable ComfyUI
sudo systemctl enable comfyui@$USER

# Enable Ollama
sudo systemctl enable ollama@$USER
```

### Disable Auto-Start

```bash
# Disable ComfyUI
sudo systemctl disable comfyui@$USER

# Disable Ollama
sudo systemctl disable ollama@$USER
```

## Configuration

### ComfyUI Configuration

Edit `/etc/systemd/system/comfyui@.service`:

```ini
# Change listen address
ExecStart=/home/%i/ComfyUI/venv/bin/python main.py --listen 0.0.0.0 --port 8188

# Add GPU support
Environment="CUDA_VISIBLE_DEVICES=0"

# Change working directory
WorkingDirectory=/path/to/ComfyUI
```

### Ollama Configuration

Edit `/etc/systemd/system/ollama@.service`:

```ini
# Change host/port
Environment="OLLAMA_HOST=0.0.0.0:11434"

# Add model path
Environment="OLLAMA_MODELS=/path/to/models"

# Change memory limit
Environment="OLLAMA_MAX_LOADED_MODELS=2"
```

After editing, reload systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl restart comfyui@$USER ollama@$USER
```

## Troubleshooting

### Service won't start

1. Check service status:
   ```bash
   sudo systemctl status comfyui@$USER
   ```

2. Check logs:
   ```bash
   sudo journalctl -u comfyui@$USER -n 50
   ```

3. Verify paths:
   ```bash
   # Check ComfyUI installation
   ls -la /home/$USER/ComfyUI
   
   # Check Ollama installation
   which ollama
   ```

4. Check permissions:
   ```bash
   # Service files should be owned by root
   ls -la /etc/systemd/system/comfyui@.service
   ```

### Service restarts frequently

1. Check for errors in logs:
   ```bash
   sudo journalctl -u comfyui@$USER -p err -n 50
   ```

2. Increase restart delay:
   Edit service file and change `RestartSec=10` to higher value

3. Check resource usage:
   ```bash
   systemctl status comfyui@$USER
   ```

### Port conflicts

1. Check what's using the port:
   ```bash
   sudo netstat -tulpn | grep 8188
   sudo netstat -tulpn | grep 11434
   ```

2. Change port in service file

### Permission issues

1. Verify service user:
   ```bash
   ps aux | grep comfyui
   ps aux | grep ollama
   ```

2. Check directory permissions:
   ```bash
   ls -la /home/$USER/ComfyUI
   ```

## Advanced Usage

### Multiple Instances

You can run multiple instances for different users:

```bash
# Start for user1
sudo systemctl start comfyui@user1

# Start for user2
sudo systemctl start comfyui@user2
```

### Resource Limits

Add resource limits to service files:

```ini
[Service]
MemoryLimit=8G
CPUQuota=200%
```

### Network Restrictions

Restrict network access:

```ini
[Service]
IPAddressDeny=any
IPAddressAllow=127.0.0.1/8
```

### Automatic Cleanup

Add cleanup on stop:

```ini
[Service]
ExecStopPost=/usr/bin/cleanup_script.sh
```

## Health Checks

Create a health check script:

```bash
#!/bin/bash
# check_services.sh

echo "Checking ComfyUI..."
if systemctl is-active --quiet comfyui@$USER; then
    echo "✓ ComfyUI is running"
else
    echo "✗ ComfyUI is not running"
fi

echo "Checking Ollama..."
if systemctl is-active --quiet ollama@$USER; then
    echo "✓ Ollama is running"
else
    echo "✗ Ollama is not running"
fi
```

Make it executable:
```bash
chmod +x check_services.sh
./check_services.sh
```

## Uninstallation

```bash
# Stop services
sudo systemctl stop comfyui@$USER ollama@$USER

# Disable services
sudo systemctl disable comfyui@$USER ollama@$USER

# Remove service files
sudo rm /etc/systemd/system/comfyui@.service
sudo rm /etc/systemd/system/ollama@.service

# Reload systemd
sudo systemctl daemon-reload
```

## Integration with Tests

The test suite includes service verification:

```bash
# Run system integration tests
pytest tests/test_system_integration.py::TestSystemdServices -v
```

## See Also

- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [Systemd Service Units](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [journalctl Documentation](https://www.freedesktop.org/software/systemd/man/journalctl.html)

## Support

For issues:
1. Check logs: `sudo journalctl -u service@$USER`
2. Verify installation: `./check_services.sh`
3. Review main documentation: `../docs/`
4. Open an issue on GitHub
