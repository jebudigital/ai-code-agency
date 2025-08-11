# AI Coding Agency 🤖

An autonomous AI-powered coding agency that uses local LLM models (Ollama) to build complete projects from functional requirements. The system coordinates multiple AI agents to handle planning, coding, testing, and documentation automatically.

## 🚀 Features

- **Multi-Agent Architecture**: Coordinated AI agents for different aspects of software development
- **Local LLM Integration**: Uses Ollama with local models (phind-codellama:34b-v2, codellama:7b-code, phi:2.7b)
- **MCP-Style Tools**: Model Context Protocol integration for enhanced agent capabilities
- **Autonomous Project Execution**: Complete projects from requirements to delivery
- **Quality Assurance**: Automated testing, linting, and code review
- **Comprehensive Documentation**: Auto-generated docs with Mermaid diagrams
- **Project Packaging**: ZIP distribution with all project artifacts

## 🏗️ Architecture

### AI Agents

1. **Planner Agent** 📋
   - Analyzes requirements and creates detailed project plans
   - Breaks down projects into actionable tasks
   - Estimates timelines and resource requirements
   - Makes architecture decisions

2. **Coder Agent** 💻
   - Generates production-quality code using local LLMs
   - Implements features with proper patterns and error handling
   - Creates comprehensive test suites
   - Uses MCP tools for file operations and git integration

3. **Reviewer Agent** 🔍
   - Runs automated quality checks (pytest, ruff, bandit)
   - Performs code review and analysis
   - Ensures code meets production standards
   - Provides detailed feedback and suggestions

4. **Documentation Agent** 📚
   - Generates comprehensive project documentation
   - Creates architecture diagrams with Mermaid
   - Maintains developer guides and runbooks
   - Packages documentation for distribution

5. **Project Manager Agent** 🎯
   - Coordinates all other agents
   - Tracks project progress and status
   - Manages project lifecycle from creation to delivery
   - Handles project packaging and distribution

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Git (for version control integration)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-coding-agency
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama models**
   ```bash
   ollama pull phind-codellama:34b-v2
   ollama pull codellama:7b-code-q4_K_M
   ollama pull phi:2.7b
   ```

5. **Start Ollama service**
   ```bash
   ollama serve
   ```

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Make the install script executable and run it
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-coding-agency
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Install Ollama models**
   ```bash
   ollama pull phind-codellama:34b-v2
   ollama pull codellama:7b-code-q4_K_M
   ollama pull phi:2.7b
   ```

5. **Start Ollama service**
   ```bash
   ollama serve
   ```

### Testing the Installation

```bash
# Run the demo (in a new terminal with venv activated)
python demo.py

# Run interactive mode
python main.py --interactive

# Create and execute sample project
python main.py --create-sample
```

### Command Line Usage

```bash
# List all projects
python main.py --list-projects

# Create a new project
python main.py --create "My Project" --requirements "requirements.txt"

# Execute a specific project
python main.py --execute-project proj_123

# Show project status
python main.py --status proj_123

# Package completed project
python main.py --package proj_123
```

## 📋 Usage Examples

### 1. Create a New Project

```python
from agents.project_manager import ProjectManagerAgent

# Initialize the project manager
pm = ProjectManagerAgent()

# Create a new project
project_id = pm.create_project(
    title="Task Management API",
    requirements="""
    Create a REST API for task management with:
    - CRUD operations for tasks
    - SQLite database
    - JWT authentication
    - Comprehensive testing
    - API documentation
    """
)

# Execute the project
success = pm.execute_project(project_id)
```

### 2. Use Individual Agents

```python
from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent

# Planning
planner = PlannerAgent()
plan = planner.plan("My Feature", "Implement user authentication")

# Coding
coder = CoderAgent()
code = coder.generate_code("Create a login function", "auth.py", "python")

# Review
reviewer = ReviewerAgent()
results = reviewer.lint_and_test()
approved, notes = reviewer.evaluate(results)
```

### 3. Generate Documentation

```python
from agents.doc_agent import DocumentationAgent

doc_agent = DocumentationAgent()
readme = doc_agent.generate_readme(project_info)
architecture_docs = doc_agent.generate_architecture_docs(structure, files)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phind-codellama:34b-v2

# Optional: Cloud API fallbacks
OPENROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
FIREWORKS_API_KEY=your_key_here

# GitHub Integration (for reviewer agent)
GITHUB_TOKEN=your_token_here
GITHUB_REPO=your_repo_here
```

### Model Selection

The system automatically selects the best model for each task:

- **phind-codellama:34b-v2**: Best for complex planning and architecture
- **codellama:7b-code**: Good for code generation and review
- **phi:2.7b**: Fast for simple tasks and documentation

## 📊 Project Lifecycle

1. **Planning Phase** 📋
   - Requirements analysis
   - Task breakdown
   - Timeline estimation
   - Architecture decisions

2. **Implementation Phase** 💻
   - Project structure setup
   - Core functionality development
   - Test creation
   - Code generation

3. **Quality Assurance Phase** 🔍
   - Automated testing
   - Code review
   - Linting and security checks
   - Issue resolution

4. **Documentation Phase** 📚
   - README generation
   - Architecture documentation
   - API documentation
   - Developer guides

5. **Packaging Phase** 📦
   - Project compilation
   - Documentation packaging
   - ZIP creation
   - Distribution preparation

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents

# Run specific test file
pytest tests/test_planner.py
```

## 📚 Documentation

The system generates comprehensive documentation including:

- **README.md**: Project overview and setup instructions
- **ARCHITECTURE.md**: System architecture and design decisions
- **DEVELOPER_GUIDE.md**: Development setup and guidelines
- **RUNBOOK.md**: Production operations and troubleshooting
- **API_DOCS.md**: API documentation with examples

## 🔍 Monitoring and Debugging

### Logging System

The AI Coding Agency includes a comprehensive logging system that captures all operations, errors, and performance metrics:

```bash
# View available logs
python utils/log_viewer.py

# View specific component logs
python utils/log_viewer.py --component planner
python utils/log_viewer.py --component ollama --lines 100

# Follow logs in real-time
python utils/log_viewer.py --component main --follow

# Export all logs
python utils/log_viewer.py --export

# Show performance summary
python utils/log_viewer.py --performance
```

### Log Files

- **main.log**: Main application operations
- **planner.log**: Planning agent activities
- **coder.log**: Code generation operations
- **reviewer.log**: Quality assurance activities
- **doc_agent.log**: Documentation generation
- **project_manager.log**: Project coordination
- **ollama.log**: LLM interaction details
- **performance.log**: Performance metrics
- **errors.log**: Error tracking and stack traces

### Project Status

Check project progress and status:

```bash
python main.py --status proj_123
```

### Logs and Debugging

The system provides detailed logging for each phase:

- Task execution logs
- Error tracking and reporting
- Performance metrics
- Quality assessment results
- Ollama interaction details

## 🚀 Advanced Features

### MCP Integration

The system implements Model Context Protocol concepts:

- **Tool Access**: Agents can use development tools
- **File Operations**: Read/write files and directories
- **Git Integration**: Version control operations
- **Testing Tools**: Automated test execution
- **Linting**: Code quality checks

### Quality Gates

Automatic routing between local and cloud models:

- Simple tasks → Local LLM
- Complex tasks → Cloud API fallback
- Quality assessment → Best available model

### Project Templates

Pre-built templates for common project types:

- Web applications
- REST APIs
- CLI tools
- Data science projects
- Mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Model Context Protocol](https://modelcontextprotocol.io/) for agent tool integration
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the generated docs in your projects

---

**Ready to build the future of software development?** 🚀

Start with `python main.py --interactive` and watch your AI coding agency come to life!
