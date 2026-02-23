# Video Generation Toolkit 🎥

A comprehensive, automated video generation toolkit that integrates multiple AI platforms and services for end-to-end video creation, from trending topic research to automated uploads.

## 🌟 Features

- **🔍 Automated Research**: Discover trending topics from Reddit, YouTube, Google Trends, and more
- **🎬 Multi-Platform Generation**: Integrate Sora, ComfyUI, OpenRouter, Ollama, Gemini, DALL-E and other AI platforms
- **📱 YouTube Shorts**: Create, analyze, and optimize Shorts from any video
- **🎨 Image Inpainting**: Modify images with AI-powered inpainting workflows
- **✨ Prompt Enhancement**: AI agent that expands simple prompts into detailed, production-ready prompts
- **📊 Video Analysis**: Comprehensive video analysis with quality assessment and recommendations
- **🛠️ Video Processing**: Complete suite of video editing utilities using FFmpeg
- **📤 Automated Upload**: Schedule and upload videos to YouTube and other platforms
- **⚡ ComfyUI Workflows**: Pre-configured workflows for image and video generation
- **🤖 AI Agents**: Intelligent agents for research, generation, and upload automation
- **🔧 Extensible**: Modular design for easy customization and adding new platforms

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cbwinslow/sora_video_maker.git
cd sora_video_maker

# Run the master installer (installs everything)
bash install/install_all.sh

# Or install manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

```bash
# Copy the template configuration
cp config/config.template.yaml config/config.yaml

# Edit config.yaml with your API keys
nano config/config.yaml
```

### Basic Usage

```bash
# Test your setup
python examples/test_connections.py

# Create YouTube Shorts from video
python examples/create_shorts.py

# Enhance prompts with AI
python examples/prompt_enhancement_demo.py

# Research trending topics
python main.py --research-only

# Generate videos from trending topics
python main.py --generate

# Run a basic example
python examples/basic_workflow.py
```

## 📦 What's Included

### Installation Scripts
- `install/install_all.sh` - Master installation script with optional platforms
- `install/install_comfyui.sh` - ComfyUI and extensions
- `install/install_ollama.sh` - Ollama and AI models
- `install/install_openai_media.sh` - OpenAI DALL-E and future Sora API
- `install/install_gemini.sh` - Google Gemini AI
- `install/install_additional_tools.sh` - Video processing tools

### AI Agents
- **Trending Topics Agent** - Researches viral content opportunities
- **Video Generation Agent** - Orchestrates video creation workflow
- **Video Upload Agent** - Handles automated uploads and scheduling
- **YouTube Shorts Agent** - Creates and optimizes YouTube Shorts
- **Video Analysis Agent** - Comprehensive video analysis and recommendations
- **Inpainting Agent** - AI-powered image modification and inpainting
- **Prompt Enhancement Agent** - Expands prompts into detailed descriptions
- **Deep Research Agent** - In-depth content research

### Scripts
- **API Integrations** - Clients for Sora, OpenRouter, Ollama, ComfyUI, Gemini, OpenAI
- **Video Utilities** - FFmpeg-based video processing functions
- **Shorts Creator** - Utilities for creating YouTube Shorts

### Workflows
- **ComfyUI Workflows** - Pre-configured JSON workflows for various generation tasks
- **Inpainting Workflows** - Image modification workflows
- **Main Orchestrator** - Complete automation pipeline

### Sample Content
- **Prompt Templates** - Professional prompt templates for various styles
- **Sample Prompts** - High-quality example prompts

## 🎯 Supported Platforms

### Video & Image Generation
- ✅ **Sora** (OpenAI) - When API becomes available
- ✅ **DALL-E 3** (OpenAI) - High-quality image generation
- ✅ **Gemini Pro & Pro Vision** (Google) - Text and image understanding
- ✅ **ComfyUI** - Local Stable Diffusion, AnimateDiff, Inpainting, and more
- ✅ **OpenRouter** - Access to various free AI models
- ✅ **Ollama** - Local LLM for script and content generation
- 🔧 Extensible to other platforms
- ✅ **Ollama** - Local LLM for script and content generation
- 🔧 Extensible to other platforms

### Content Sources
- ✅ Reddit trending posts
- ✅ YouTube trending videos
- ✅ Google Trends
- 🔧 Extensible to Twitter, TikTok, RSS feeds, etc.

### Upload Platforms
- ✅ YouTube (with OAuth2)
- ✅ YouTube Shorts (optimized format)
- 🔧 Extensible to TikTok, Instagram Reels, Twitter, etc.

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Complete Documentation](docs/README.md)** - Full guide with all features
- **[YouTube Shorts Guide](docs/YOUTUBE_SHORTS.md)** - Creating and optimizing Shorts
- **[AI Agents Guide](docs/AI_AGENTS.md)** - Using and creating AI agents
- **[Workflow Documentation](workflows/README.md)** - ComfyUI workflow usage
- **Configuration Examples** - Sample configs for various use cases

## 🔑 API Keys Required

To use all features, you'll need API keys for:

- **OpenAI** (for DALL-E, Sora when available) - https://platform.openai.com/
- **Google AI** (for Gemini) - https://makersuite.google.com/app/apikey
- **OpenRouter** (for free models) - https://openrouter.ai/
- **YouTube Data API** (for uploads) - https://console.cloud.google.com/
- **Anthropic** (optional) - https://www.anthropic.com/
- **Hugging Face** (optional, for model downloads) - https://huggingface.co/

Add them to `config/config.yaml` after installation.

## 🏗️ Architecture

```
sora_video_maker/
├── install/              # Installation scripts
│   ├── install_all.sh
│   ├── install_comfyui.sh
│   ├── install_gemini.sh
│   └── install_openai_media.sh
├── agents/               # AI agents for automation
│   ├── trending_topics_agent.py
│   ├── video_generation_agent.py
│   ├── youtube_shorts_agent.py
│   ├── video_analysis_agent.py
│   ├── inpainting_agent.py
│   └── prompt_enhancement_agent.py
├── scripts/              # Utility scripts
│   ├── api_integrations.py
│   ├── video_utils.py
│   ├── openai_tools/
│   └── gemini_tools/
├── workflows/            # ComfyUI workflow definitions
├── prompts/              # Prompt templates and samples
├── config/               # Configuration files
├── examples/             # Example usage scripts
├── docs/                 # Documentation
├── main.py              # Main workflow orchestrator
└── requirements.txt     # Python dependencies
```

## 💡 Example Workflow

```python
# 1. Research trending topics
from agents.trending_topics_agent import TrendingTopicsAgent

agent = TrendingTopicsAgent(config)
trends = await agent.research()

# 2. Generate video from top topic
from agents.video_generation_agent import VideoGenerationOrchestrator

orchestrator = VideoGenerationOrchestrator(config)
result = await orchestrator.generate_video(trends[0])

# 3. Upload to YouTube
from agents.video_upload_agent import VideoUploadAgent

upload_agent = VideoUploadAgent(config)
metadata = upload_agent.generate_metadata(trends[0])
results = await upload_agent.upload_video(result['video_path'], metadata)
```

## 🛠️ Development

### Running Tests

Comprehensive test suite with agent communication tests:

```bash
# Quick test run
./run_tests.sh

# Run with coverage report
./run_tests.sh --coverage

# Run only unit tests
./run_tests.sh --unit

# Run only integration tests
./run_tests.sh --integration

# Run all tests including slow ones
./run_tests.sh --all --verbose
```

### Test Categories

- **Initialization Tests**: 100% coverage of agent, crew, and orchestrator initialization
- **Agent Communication Tests**: Tests for agent-to-agent communication and coordination
- **System Integration Tests**: File system, web services, and system resource access
- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end workflow tests

See [Comprehensive Testing Guide](docs/COMPREHENSIVE_TESTING.md) for details.

### Service Health Check

Check the status of all services:

```bash
./check_services.sh
```

### Starting Services

```bash
# Linux only - systemd services
# Requires a Linux system with systemd; on macOS/Windows, skip to "Or manually" below.
sudo systemctl start comfyui@$USER
sudo systemctl start ollama@$USER

# Or manually
# Start ComfyUI
cd ComfyUI
python main.py

# Start Ollama
ollama serve
```

For systemd setup, see [systemd services documentation](install/systemd/README.md).

## 📝 TODO / Future Enhancements

See [TASKS.md](TASKS.md) for comprehensive task tracking including:

- Agent communication & swarm improvements
- Testing coverage goals
- Platform integrations
- Infrastructure enhancements
- Documentation needs

Quick highlights:
- [ ] Complete OpenAI Swarm integration
- [ ] Achieve 100% test coverage for agents
- [ ] Add TikTok upload support
- [ ] Add Instagram Reels upload support
- [ ] Implement Sora API integration when available
- [ ] Add more ComfyUI workflows
- [ ] Add Twitter/X integration for research
- [ ] Add voice-over generation
- [ ] Add subtitle generation
- [ ] Add video analytics tracking
- [ ] Add scheduled batch processing
- [ ] Add web UI for monitoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This toolkit is for educational and research purposes. Always follow platform terms of service and content policies when using automated tools. Be responsible with API usage and respect rate limits.

## 🙏 Credits

Built with:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [Ollama](https://ollama.com/)
- [OpenRouter](https://openrouter.ai/)
- [FFmpeg](https://ffmpeg.org/)
- And many other open-source projects

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [documentation](docs/README.md)
- Run diagnostics: `python examples/test_connections.py`

---

**Happy Video Creating! 🎬✨**