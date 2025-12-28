# Contributing to Personal Assistant Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### 1. Fork the Repository
```bash
# On GitHub, click "Fork" button
# This creates your own copy of the repository
```

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR-USERNAME/personal-assistant-bot.git
cd personal-assistant-bot
```

### 3. Add Upstream Remote
```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/personal-assistant-bot.git
```

### 4. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Setup Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Make Your Changes

Follow these guidelines:

- **Code Style**: Use PEP 8 (Python style guide)
- **Type Hints**: Add type hints to functions
- **Documentation**: Add docstrings to all functions
- **Testing**: Test your changes locally
- **Comments**: Explain complex logic with comments

### 3. Test Your Changes
```bash
# Run the bot locally
python main.py

# Test in Telegram
# Send messages to your bot and verify responses
```

### 4. Commit Your Changes
```bash
# Add your changes
git add .

# Commit with meaningful message
git commit -m "feat: Add new feature description"

# Follow commit message format:
# feat(scope): Short description
# fix(scope): Bug fix
# docs: Documentation update
# style: Code formatting
# refactor: Code restructuring
# test: Adding tests
```

### 5. Keep Your Branch Updated
```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/master
```

### 6. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request
1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Add title and description
4. Click "Create pull request"

## Commit Message Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code change that neither fixes bugs nor adds features
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to build process, dependencies, or tools

### Examples
```
feat(telegram): Add support for keyboard shortcuts

fix(parser): Handle unknown commands gracefully

docs: Update setup instructions

style: Format code according to PEP 8

refactor(email): Simplify email parsing logic

test: Add unit tests for AIService

chore: Update dependencies to latest versions
```

## Code Style Guidelines

### Python Code Style (PEP 8)

```python
# Good: Clear variable names, proper spacing
def parse_command(text: str) -> Dict[str, Any]:
    """Parse natural language command using AI"""
    text_lower = text.lower().strip()
    
    # Check for keywords
    if "email" in text_lower:
        return {"action": "read_emails"}
    
    return {"action": "unknown"}

# Bad: Unclear variable names, poor formatting
def parse_cmd(t):
    tl=t.lower()
    if "email" in tl:return {"action":"read_emails"}
    return{"action":"unknown"}
```

### Function Documentation

```python
def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Send an email via Gmail
    
    Args:
        recipient: Email address to send to
        subject: Email subject line
        body: Email body content
        
    Returns:
        True if sent successfully, False otherwise
        
    Raises:
        ValueError: If recipient email is invalid
        
    Example:
        >>> send_email("john@example.com", "Hello", "Hi John!")
        True
    """
    # Implementation
    pass
```

### Type Hints

```python
from typing import Dict, List, Optional, Tuple

def get_emails(limit: int = 5) -> List[Dict[str, str]]:
    """Get unread emails"""
    pass

def find_task(task_id: int) -> Optional[Task]:
    """Find task by ID, return None if not found"""
    pass
```

## Project Structure

```
Bot/
├── app/
│   ├── services/          # Business logic
│   │   ├── ai_service.py
│   │   ├── gmail_service.py
│   │   └── telegram_service.py
│   ├── routers/           # API endpoints
│   │   ├── email.py
│   │   ├── telegram.py
│   │   └── scheduler.py
│   ├── models/            # Database models
│   │   ├── database.py
│   │   └── schemas.py
│   ├── workers/           # Background tasks
│   │   ├── scheduler.py
│   │   └── tasks.py
│   ├── config.py          # Configuration
│   └── utils.py           # Utilities
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # Documentation
```

## What to Work On

### Good First Issues
- [ ] Improve error messages
- [ ] Add more keyword patterns to command parser
- [ ] Write unit tests
- [ ] Improve documentation
- [ ] Fix code style issues

### Feature Ideas
- [ ] Weather service integration
- [ ] Calendar integration
- [ ] Database migrations
- [ ] Email template system
- [ ] Multi-language support
- [ ] Better email summarization
- [ ] Task prioritization

## Pull Request Guidelines

### Before Creating PR
- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints are added
- [ ] Changes are tested locally
- [ ] Commit messages are clear
- [ ] No credentials or secrets committed

### PR Title Format
```
feat(scope): Brief description
fix(scope): Brief description
docs: Brief description
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update

## Testing
How to test these changes

## Screenshots (if applicable)
Before/after screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Changes are tested
- [ ] Documentation is updated
- [ ] No breaking changes
```

## Review Process

1. **Automated Checks**: Code style, tests
2. **Manual Review**: Project maintainers review code
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, PR is merged

## Common Mistakes to Avoid

- ❌ Committing `.env` file with real credentials
- ❌ Large commits with multiple unrelated changes
- ❌ Vague commit messages
- ❌ Not testing changes before PR
- ❌ Committing commented-out code
- ❌ Making changes to master directly
- ❌ Not updating documentation

## Questions?

- Check existing issues: https://github.com/USERNAME/personal-assistant-bot/issues
- Read documentation: See README.md and IMPLEMENTATION.md
- Start a discussion: Use GitHub Discussions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Accept criticism gracefully
- Help others learn

Thank you for contributing! 🚀
