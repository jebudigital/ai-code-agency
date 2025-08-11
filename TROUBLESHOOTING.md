# Troubleshooting Guide 🔧

This guide helps you resolve common issues with the AI Coding Agency.

## 🚨 Common Issues

### 1. Ollama Timeout Errors

**Symptoms:**
```
Ollama CLI failed: Command timed out after 60 seconds
```

**Causes:**
- Model is too large for your hardware
- Insufficient RAM or GPU memory
- Model is still loading

**Solutions:**
```bash
# Check available models
ollama list

# Use a smaller model
export OLLAMA_MODEL=phi:2.7b

# Check system resources
top
htop  # if available

# Restart Ollama with more resources
OLLAMA_NUM_GPU_LAYERS=99 ollama serve
```

### 2. Import Errors

**Symptoms:**
```
ImportError: attempted relative import with no known parent package
```

**Solutions:**
```bash
# Install in development mode
pip install -e .

# Or run from the correct directory
cd ai-coding-agency
python main.py --interactive
```

### 3. Permission Errors

**Symptoms:**
```
Permission denied: 'install.sh'
```

**Solutions:**
```bash
# Make script executable
chmod +x install.sh

# Run installation
./install.sh
```

### 4. Model Not Found

**Symptoms:**
```
Error: model 'phind-codellama:34b-v2' not found
```

**Solutions:**
```bash
# Pull the required model
ollama pull phind-codellama:34b-v2

# Or use an available model
export OLLAMA_MODEL=phi:2.7b
```

## 📊 Performance Issues

### Slow Response Times

**Check Performance:**
```bash
# View performance logs
python utils/log_viewer.py --performance

# Monitor Ollama interactions
python utils/log_viewer.py --component ollama --follow
```

**Optimization Tips:**
- Use smaller models for simple tasks
- Increase timeout values in agent configurations
- Ensure sufficient system resources
- Use GPU acceleration if available

### Memory Issues

**Symptoms:**
- System becomes unresponsive
- Ollama crashes
- Out of memory errors

**Solutions:**
```bash
# Check memory usage
free -h  # Linux
vm_stat   # macOS

# Reduce model size
export OLLAMA_MODEL=phi:2.7b

# Restart Ollama
pkill ollama
ollama serve
```

## 🔍 Debugging

### Enable Debug Logging

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py --log-level DEBUG
```

### View Detailed Logs

```bash
# View all logs
python utils/log_viewer.py --export

# Follow specific component
python utils/log_viewer.py --component planner --follow

# Check error logs
python utils/log_viewer.py --component errors
```

### Common Log Locations

```bash
# Application logs
logs/main.log
logs/planner.log
logs/coder.log

# Performance data
logs/performance.log

# Error tracking
logs/errors.log

# Ollama interactions
logs/ollama.log
```

## 🛠️ System Requirements

### Minimum Requirements
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.8+
- **Ollama**: Latest version

### Recommended Requirements
- **RAM**: 32GB+
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Storage**: SSD with 50GB+ free space
- **CPU**: 8+ cores

## 🔧 Configuration Issues

### Environment Variables

**Check Configuration:**
```bash
# View current settings
echo $OLLAMA_MODEL
echo $OLLAMA_HOST
echo $LOG_LEVEL

# Set configuration
export OLLAMA_MODEL=phind-codellama:34b-v2
export OLLAMA_HOST=http://localhost:11434
export LOG_LEVEL=INFO
```

### Model Selection

**For Different Tasks:**
```bash
# Planning and Architecture
export OLLAMA_MODEL=phind-codellama:34b-v2

# Code Generation
export OLLAMA_MODEL=codellama:7b-code-q4_K_M

# Simple Tasks
export OLLAMA_MODEL=phi:2.7b
```

## 📱 Platform-Specific Issues

### macOS
```bash
# Install Ollama
brew install ollama

# Start service
ollama serve

# Check GPU support
system_profiler SPDisplaysDataType
```

### Linux
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
sudo systemctl start ollama

# Check GPU
nvidia-smi
```

### Windows
```bash
# Download from https://ollama.ai/
# Run as administrator
ollama serve
```

## 🆘 Getting Help

### 1. Check Logs First
```bash
python utils/log_viewer.py --export
```

### 2. Verify Ollama Setup
```bash
ollama list
curl http://localhost:11434/api/tags
```

### 3. Test Basic Functionality
```bash
python demo.py
```

### 4. Check System Resources
```bash
# Memory
free -h  # Linux
vm_stat  # macOS

# Disk space
df -h

# CPU usage
top
```

### 5. Common Commands
```bash
# Restart Ollama
pkill ollama
ollama serve

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

If you're still experiencing issues:

1. **Export logs**: `python utils/log_viewer.py --export`
2. **Check system info**: Include OS version, Python version, Ollama version
3. **Describe the issue**: What you were trying to do, what happened, what you expected
4. **Include error messages**: Copy the full error text

## 🎯 Performance Tips

### For Better Performance:
- Use smaller models for simple tasks
- Ensure sufficient RAM (16GB+)
- Use SSD storage
- Enable GPU acceleration if available
- Close unnecessary applications
- Monitor system resources during operation

### For Development:
- Use `pip install -e .` for development
- Set `LOG_LEVEL=DEBUG` for detailed logging
- Use the log viewer to monitor operations
- Test with simple projects first
