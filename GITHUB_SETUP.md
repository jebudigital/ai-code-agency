# GitHub Integration Setup Guide 🔗

This guide explains how to set up GitHub integration for the AI Coding Agency, which will provide:

- **Separate Repositories**: Each project gets its own GitHub repository
- **Project Management**: Individual project boards with Kanban workflows
- **Issue Tracking**: Automated issue creation for development phases
- **Progress Monitoring**: Real-time status updates across repositories
- **Client Isolation**: Clean separation between different projects
- **Professional Workflow**: Industry-standard project management per repository

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install PyGithub
# or
pip install -r requirements.txt
```

### 2. Set Up GitHub Authentication

Create a `.env` file in your project root:
```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=your-org-name  # Optional: Use organization instead of user account

# Ollama Configuration  
OLLAMA_MODEL=phi:2.7b
OLLAMA_HOST=http://localhost:11434

# Optional: Logging
LOG_LEVEL=INFO
```

**To get your GitHub token:**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select `repo` scope (full control of repositories)
4. Copy the token immediately

**Organization vs User Account:**
- **User Account**: Repositories created under your personal account
- **Organization**: Repositories created under a GitHub organization (recommended for teams)

### 3. Test the Integration

```bash
# Run interactive mode
python main.py --interactive

# Create a test project
create my-test-project
# Enter requirements when prompted
# Choose repository privacy (private/public)
```

### 4. What Happens Next

When you create a project, the system will:
- ✅ Create a **new GitHub repository** for the project
- ✅ Set up initial project structure (README, requirements.txt, .gitignore)
- ✅ Create a **project board** with development phases
- ✅ Initialize **development phase issues**
- ✅ Show you the repository URL and project board

## 🔧 Advanced Configuration

### Repository Structure

Each project repository includes:

- **README.md**: Comprehensive project overview
- **PROJECT_STRUCTURE.md**: Development phase tracking
- **requirements.txt**: Python dependencies template
- **.gitignore**: Python-specific ignore rules
- **src/**: Source code directory
- **tests/**: Test files directory
- **docs/**: Documentation directory

### Development Phases

The system automatically creates these phases:

1. **🚀 Project Setup Complete** - Repository initialization
2. **📋 Requirements Analysis** - Planning phase
3. **🏗️ Architecture Design** - Technical specifications
4. **💻 Core Implementation** - Development phase
5. **🧪 Testing & Quality** - Testing and review
6. **📚 Documentation** - Documentation generation

### Project Board Columns

Each repository gets a Kanban board with:
- 📋 Planning
- 🚀 In Progress
- 🔍 Review
- 🧪 Testing
- ✅ Completed
- ❌ Failed

## 📊 Project Workflow

### 1. Project Creation
- Creates **new GitHub repository**
- Sets up initial project structure
- Creates project board with columns
- Initializes development phase issues

### 2. Development Execution
- Updates issue status as phases progress
- Moves issues between board columns
- Adds progress comments with timestamps
- Tracks completion of each phase

### 3. Project Completion
- All phases marked as completed
- Project ready for client delivery
- Repository can be transferred to client
- Complete development history preserved

## 🎯 Usage Examples

### Create Project with Separate Repository

```bash
python main.py --interactive

🤖 > create my-web-app
Enter project requirements: Create a modern web application with React frontend and Node.js backend
Make repository private? (y/n, default: y): y
```

This will:
1. Create a new GitHub repository: `my-web-app-123456`
2. Set up project structure and files
3. Create project board with development phases
4. Show repository URL and project board link

### Monitor Progress

```bash
# Check local project status
status proj_123

# Check GitHub project status
github-status proj_123

# List all GitHub repositories
list-github

# View individual project board
# (Open the project board URL shown in project creation)
```

### Execute Project

```bash
execute proj_123
```

This will:
1. Update GitHub issues as phases progress
2. Move issues between board columns
3. Add progress comments
4. Mark phases as completed

## 🔍 Troubleshooting

### Common Issues

#### 1. "GitHub token required" Error
```bash
# Check environment variable
echo $GITHUB_TOKEN

# Set it if missing
export GITHUB_TOKEN=ghp_your_token_here
```

#### 2. "Organization not found" Error
```bash
# Check organization name
echo $GITHUB_ORG

# Ensure you have access to the organization
# Or remove GITHUB_ORG to use user account
```

#### 3. Permission Denied
- Check token has correct scopes (`repo`)
- Ensure repository creation permissions
- Verify token hasn't expired

#### 4. Rate Limiting
- GitHub has API rate limits
- System includes automatic delays
- Consider using GitHub Enterprise for higher limits

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py --log-level DEBUG
```

## 🚀 Advanced Features

### Repository Management

- **Automatic naming**: Timestamp-based unique names
- **Privacy control**: Public or private repositories
- **Branch protection**: Main branch protection for organizations
- **Template files**: Pre-configured project structure

### Issue Management

Each development phase issue includes:
- Detailed description and objectives
- Progress tracking checkboxes
- Status labels and phase categorization
- Automatic status updates during execution

### Client Benefits

- **Clean separation**: Each project in its own repository
- **Professional presentation**: Ready-to-use project structure
- **Easy transfer**: Repository can be transferred to client
- **Complete history**: Full development timeline preserved

## 🔐 Security Considerations

### Token Security
- Never commit tokens to version control
- Use environment variables or secure vaults
- Rotate tokens regularly
- Use minimal required permissions

### Repository Access
- Consider using organization repositories
- Implement branch protection rules
- Use required status checks
- Enable security scanning

## 📈 Monitoring and Analytics

### Repository Insights
- Individual project progress tracking
- Development phase completion rates
- Issue resolution times
- Project timeline analytics

### Integration Benefits
- **Isolation**: Each project completely separate
- **Professionalism**: Client-ready repositories
- **Scalability**: Easy to manage multiple projects
- **Collaboration**: Team access per repository
- **History**: Complete development audit trail

## 🎉 Next Steps

1. **Set up your GitHub token** and organization (optional)
2. **Test with a small project** to verify integration
3. **Create your first project** and explore the repository
4. **Invite team members** to collaborate on projects
5. **Monitor progress** through individual project boards

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your GitHub token and permissions
3. Check the logs: `python utils/log_viewer.py --component main`
4. Ensure PyGithub is installed: `pip install PyGithub`

## 🔄 Migration from Old System

If you were using the previous milestone-based approach:

1. **Old projects**: Continue using existing milestones
2. **New projects**: Will automatically use separate repositories
3. **No data loss**: All existing project data preserved
4. **Gradual transition**: Mix of old and new approaches supported

---

**Ready to supercharge your AI Coding Agency with separate project repositories?** 🚀

Each project will now have its own professional GitHub repository with full project management capabilities!
