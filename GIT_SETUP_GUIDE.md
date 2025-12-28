# 🚀 Complete Git Setup Guide for Personal Assistant Bot

## Phase 1: Local Git Repository Setup

### Step 1.1: Initialize Git Repository

```powershell
cd d:\AI\Bot
git init
```

**What this does:**
- Creates a `.git` directory with Git metadata
- Initializes version control for your project
- No files are committed yet

**Output:**
```
Initialized empty Git repository in d:\AI\Bot\.git/
```

---

### Step 1.2: Configure Git Identity

Set your user name and email (required for commits):

```powershell
# Global configuration (applies to all projects)
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"

# OR Project-specific (only this repository)
git config user.name "Your Full Name"
git config user.email "your.email@example.com"
```

**Verify configuration:**
```powershell
git config --global --list
git config --list
```

---

### Step 1.3: Create .gitignore File

Create a file to specify what Git should ignore:

```powershell
# Navigate to project root (you should already be there)
```

Create `d:\AI\Bot\.gitignore`:

```
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
*.sublime-project
*.sublime-workspace

# Database
*.db
*.sqlite
*.sqlite3
bot_database.db

# Logs
logs/
*.log

# OS
Thumbs.db
.DS_Store

# Ngrok
ngrok.exe
.ngrok2/
ngrock_key.txt

# Credentials (NEVER commit these!)
credentials.json
token.json
*.key
*.pem
*.p12

# Node modules (if using any frontend)
node_modules/

# Temp files
*.tmp
*.bak
*.backup
temp/
tmp/
```

---

### Step 1.4: Create README.md (If Not Already Present)

Check if README exists:

```powershell
# Check if README exists
Test-Path d:\AI\Bot\README.md

# If it exists, you're good!
# If not, review your existing README.md in the project
```

**Your README is already excellent!** It contains all necessary information.

---

### Step 1.5: Check Status Before Committing

```powershell
git status
```

**Expected output:**
```
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore
        DEPLOY_NOW.md
        EXAMPLES.md
        ...
        (all your project files)

nothing added to commit but untracked files present (tracking will start after first commit)
```

---

## Phase 2: Create Remote Repository

### Step 2.1: Choose Platform

Options:
- **GitHub** (Most popular, free, best for open-source)
- **GitLab** (Better for private repos, free tier)
- **Bitbucket** (Free for small teams)

### Step 2.2: GitHub Setup (Recommended)

#### Option A: Via GitHub Website

1. Go to https://github.com/new
2. Sign in (create account if needed)
3. Fill in:
   - **Repository name:** `personal-assistant-bot` (or your preferred name)
   - **Description:** "AI-powered personal assistant bot with email, task scheduling, and Telegram integration"
   - **Visibility:** Select `Public` or `Private`
   - **Initialize repository:** Leave UNCHECKED (we already have code)
   - **Add .gitignore:** Select `Python` (optional, we created ours)
   - **Add license:** Select `MIT License` (recommended)

4. Click "Create repository"

#### Option B: Via GitHub CLI (if installed)

```powershell
gh repo create personal-assistant-bot `
  --source=. `
  --remote=origin `
  --public `
  --description "AI-powered personal assistant bot"
```

**Result:** GitHub gives you a repository URL:
```
https://github.com/YOUR-USERNAME/personal-assistant-bot.git
```

---

### Step 2.3: Set Up SSH Key (Optional but Recommended)

Using SSH is more secure than HTTPS passwords.

#### Check if you have SSH key:
```powershell
Test-Path $env:USERPROFILE\.ssh\id_rsa
```

#### If not, generate one:
```powershell
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa -N ""
```

#### Add to SSH agent:
```powershell
# Start SSH agent
ssh-agent -s

# Add your key
ssh-add $env:USERPROFILE\.ssh\id_rsa
```

#### Add public key to GitHub:
1. Copy your public key:
```powershell
Get-Content $env:USERPROFILE\.ssh\id_rsa.pub | Set-Clipboard
```

2. Go to GitHub → Settings → SSH and GPG keys → New SSH key
3. Paste and save

---

## Phase 3: Connect Local to Remote

### Step 3.1: Add Remote Repository

```powershell
cd d:\AI\Bot

# Using HTTPS (simpler, no SSH setup)
git remote add origin https://github.com/YOUR-USERNAME/personal-assistant-bot.git

# OR using SSH (more secure)
git remote add origin git@github.com:YOUR-USERNAME/personal-assistant-bot.git
```

**Replace:**
- `YOUR-USERNAME` with your GitHub username

### Step 3.2: Verify Remote Connection

```powershell
git remote -v
```

**Expected output:**
```
origin  https://github.com/YOUR-USERNAME/personal-assistant-bot.git (fetch)
origin  https://github.com/YOUR-USERNAME/personal-assistant-bot.git (push)
```

---

## Phase 4: Add Files and Create First Commit

### Step 4.1: Stage All Files

```powershell
# Add all files (respects .gitignore)
git add .

# OR add specific files
git add *.py
git add *.md
git add app/
git add requirements.txt
```

### Step 4.2: Check What Will Be Committed

```powershell
git status
```

**Should show green "Changes to be committed"**

### Step 4.3: Create First Commit

```powershell
git commit -m "Initial commit: Personal Assistant Bot with email, tasks, and Telegram integration"
```

**Best practices for commit messages:**
- ✅ `Initial commit: Set up bot structure with Gmail, Telegram, and scheduler`
- ✅ `feat: Add email summarization with OpenAI`
- ✅ `fix: Handle unknown commands gracefully`
- ✅ `docs: Add setup instructions and API documentation`
- ❌ `update` (too vague)
- ❌ `fix bug` (which bug?)
- ❌ `asdf` (meaningless)

### Step 4.4: Verify Commit

```powershell
git log --oneline
```

**Output:**
```
a1b2c3d (HEAD -> master) Initial commit: Personal Assistant Bot with email, tasks, and Telegram integration
```

---

## Phase 5: Push to Remote Repository

### Step 5.1: Set Upstream Branch

For first push, set the upstream branch:

```powershell
git push -u origin master
```

Or (if GitHub uses `main` as default):
```powershell
git push -u origin main
```

**What this does:**
- `-u` sets `origin/master` as upstream
- Future pushes only need `git push`

### Step 5.2: Authenticate

**For HTTPS (first time):**
- GitHub will prompt for credentials
- Use your GitHub username and Personal Access Token (not password)

**For SSH:**
- Should work automatically if SSH key is added

### Step 5.3: Verify Push

```powershell
git log --oneline
# Should show your commit with (HEAD -> master, origin/master)

git remote -v
# Should show origin URLs
```

**Check GitHub:** Go to your repository URL, you should see all your files!

---

## Phase 6: Ongoing Workflow (Future Commits)

### Making Changes and Committing

```powershell
# Make changes to files
# Edit app/services/telegram_service.py, etc.

# Check what changed
git status

# Stage changes
git add app/services/telegram_service.py

# Commit with meaningful message
git commit -m "feat: Improve command parsing with better error handling"

# Push to remote
git push
```

### Common Workflow Commands

```powershell
# Check status
git status

# View commit history
git log --oneline -10  # Last 10 commits

# View changes before committing
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Create a new branch
git checkout -b feature/new-feature

# Switch branches
git checkout master

# Merge branch into master
git checkout master
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

---

## Best Practices Checklist

### ✅ Before First Push

- [x] Create `.gitignore` (done)
- [x] README.md is present and complete (done)
- [x] Remove sensitive files (credentials, API keys)
- [x] Add LICENSE file (recommended: MIT)
- [x] Configure git user.name and user.email
- [ ] Add CONTRIBUTING.md (optional, for collaborative projects)

### ✅ Ongoing Development

- Write clear, descriptive commit messages
- Commit frequently (not everything at once)
- Use branches for features: `git checkout -b feature/your-feature`
- Create Pull Requests for code review (if collaborating)
- Keep remote repository in sync: `git pull` before making changes

### ✅ Commit Message Format (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (formatting)
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

**Examples:**
```
feat(telegram): Add keyboard shortcuts for common commands

fix(parser): Handle weather queries gracefully

docs: Add production deployment guide

chore: Update dependencies
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Committing .env Files
**Problem:** Exposes API keys and sensitive data
**Solution:** Add to `.gitignore` and use `.env.example`

```bash
# Create template
cp .env .env.example
echo ".env" >> .gitignore
```

### ❌ Mistake 2: Committing Large Files
**Problem:** Slows down Git, wastes space
**Solution:** Use `.gitignore` for binaries, databases, logs

```
__pycache__/
*.db
logs/
venv/
```

### ❌ Mistake 3: Vague Commit Messages
**Problem:** Hard to understand what changed
**Solution:** Use descriptive messages

```
❌ "update"
✅ "feat: Add email priority classification with AI"
```

### ❌ Mistake 4: Pushing to Master Directly
**Problem:** Can break production code
**Solution:** Use feature branches and code review

```powershell
git checkout -b feature/new-feature
# Make changes
git push origin feature/new-feature
# Create Pull Request on GitHub
```

### ❌ Mistake 5: Not Pulling Before Pushing
**Problem:** Merge conflicts
**Solution:** Always pull first

```powershell
git pull origin master
git push origin master
```

---

## Sensitive Data Handling

### Create .env.example

```bash
# Create template without actual values
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_user_id_here
OPENAI_API_KEY=your_openai_key_here
GMAIL_CREDENTIALS_FILE=credentials.json
```

### Document Setup

In your README:

```markdown
## Setup Instructions

1. Copy .env.example to .env
2. Fill in your actual credentials in .env
3. Never commit .env file
```

---

## Optional: Add License

### MIT License (Recommended for Open Source)

Create `LICENSE` file in root:

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
```

Then commit:
```powershell
git add LICENSE
git commit -m "docs: Add MIT License"
git push
```

---

## Branching Strategy (Best Practice)

### Git Flow for Teams

```
main (or master)
  ↑
  └─ release/v1.0.0
        ↑
        └─ develop
              ↑
              ├─ feature/emails-ai-summarization
              ├─ feature/weather-integration
              └─ bugfix/fix-parsing-issue
```

### Setup:

```powershell
# Create develop branch
git checkout -b develop
git push -u origin develop

# For each feature
git checkout -b feature/my-feature develop
# Make changes and commit
git push -u origin feature/my-feature

# Create Pull Request on GitHub
# After review, merge to develop
# When ready for release, merge develop to main
```

---

## Tags and Releases

### Create a Release Tag

```powershell
# After stable code is merged
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release"

# Push tags
git push origin --tags

# View tags
git tag -l
```

---

## Quick Reference Commands

```powershell
# Initial setup
git init
git config user.name "Name"
git config user.email "email@example.com"

# Create .gitignore and add files
git add .
git commit -m "Initial commit"

# Connect to remote
git remote add origin https://github.com/username/repo.git

# First push
git push -u origin master

# Daily workflow
git status
git add .
git commit -m "feat: description"
git push

# Branching
git checkout -b feature-name
git push -u origin feature-name

# View history
git log --oneline --graph --all
```

---

## Summary

| Phase | Commands | Time |
|-------|----------|------|
| 1. Local setup | `git init`, `git config` | 2 min |
| 2. Remote setup | Create on GitHub | 5 min |
| 3. Connect | `git remote add origin` | 1 min |
| 4. First commit | `git add .`, `git commit` | 2 min |
| 5. First push | `git push -u origin master` | 1 min |
| **Total** | | **~11 minutes** |

---

**Next Step:** Follow Phase 1 → Phase 5 in order, then choose your branching strategy!

