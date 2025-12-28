# Git Quick Reference - Personal Assistant Bot

## Initial Setup (One Time)

```powershell
# Initialize repository
git init

# Configure user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/personal-assistant-bot.git

# First commit and push
git add .
git commit -m "Initial commit: Personal Assistant Bot"
git push -u origin master
```

---

## Daily Workflow

```powershell
# Check status
git status

# See what changed
git diff

# Stage changes
git add .
git add file.py

# Commit changes
git commit -m "feat: Add new feature"

# Push to remote
git push
```

---

## Viewing History

```powershell
# See commit history
git log

# Compact view
git log --oneline -10

# See branches
git log --all --graph --decorate --oneline

# Who changed what
git blame file.py

# Specific commit details
git show abc123d
```

---

## Branching

```powershell
# Create branch
git checkout -b feature/new-feature
git branch feature/new-feature

# List branches
git branch
git branch -a  # including remote

# Switch branch
git checkout master
git switch feature/new-feature

# Delete branch
git branch -d feature/new-feature
git branch -D feature/new-feature  # force

# Rename branch
git branch -m old-name new-name

# Push new branch
git push -u origin feature/new-feature
```

---

## Merging & Rebasing

```powershell
# Merge branch into current
git merge feature/new-feature

# Rebase current branch
git rebase master

# Interactive rebase
git rebase -i HEAD~3

# Abort merge/rebase
git merge --abort
git rebase --abort
```

---

## Undoing Changes

```powershell
# Discard changes in working directory
git checkout -- file.py

# Unstage file
git reset file.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert commit (new commit)
git revert abc123d

# View lost commits
git reflog
git reset --hard abc123d  # recover
```

---

## Stashing

```powershell
# Save changes temporarily
git stash

# List stashes
git stash list

# Apply stash
git stash apply
git stash apply stash@{0}

# Pop stash (apply and remove)
git stash pop

# Delete stash
git stash drop
git stash drop stash@{0}
```

---

## Remote Operations

```powershell
# List remotes
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git

# Remove remote
git remote remove origin

# Fetch changes (no merge)
git fetch origin

# Pull changes (fetch + merge)
git pull origin master

# Push changes
git push origin master

# Push all branches
git push origin --all

# Push tags
git push origin --tags

# Delete remote branch
git push origin --delete feature/old-feature
```

---

## Tagging

```powershell
# List tags
git tag

# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tags
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0

# Checkout tag
git checkout v1.0.0
```

---

## Cleaning Up

```powershell
# Remove untracked files
git clean -fd

# Remove untracked files and directories
git clean -fdx

# Check what would be deleted
git clean -fdxn

# Remove ignored files
git clean -fdX
```

---

## Useful Configurations

```powershell
# Set default editor
git config --global core.editor "code"

# Set default branch name
git config --global init.defaultBranch main

# Configure merge strategy
git config --global pull.rebase false

# Show detailed status
git config --global status.short true

# Set up aliases
git config --global alias.st "status"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.cm "commit -m"
git config --global alias.log-graph "log --all --graph --decorate --oneline"
```

---

## Common Scenarios

### Scenario 1: Oops, Committed to Master Instead of Feature Branch

```powershell
# Create feature branch from current commit
git branch feature/my-feature

# Reset master to before commit
git reset --hard origin/master

# Switch to feature branch
git checkout feature/my-feature
```

### Scenario 2: Need to Add One More File to Last Commit

```powershell
git add forgotten-file.py
git commit --amend --no-edit
git push --force-with-lease origin master
```

### Scenario 3: Committed Sensitive Data

```powershell
# Remove file from history
git filter-branch --tree-filter 'rm -f .env' HEAD

# Or reset and recommit
git reset --soft HEAD~1
git reset HEAD .env
git commit -m "Remove sensitive file"
```

### Scenario 4: Want to Undo a Pushed Commit

```powershell
# Create new commit that undoes changes
git revert abc123d
git push

# OR reset (dangerous if others are using this branch!)
git reset --hard HEAD~1
git push --force-with-lease
```

### Scenario 5: Merge Conflicts

```powershell
# During merge, conflicts appear
# Edit conflicting files manually

# Mark as resolved
git add conflicting-file.py

# Complete the merge
git commit

# For rebase conflicts
git rebase --continue
git rebase --abort
```

---

## Performance Tips

```powershell
# Shallow clone (faster for large repos)
git clone --depth 1 https://github.com/user/repo.git

# Sparse checkout (clone only part of repo)
git clone --sparse https://github.com/user/repo.git
cd repo
git sparse-checkout add app/

# Garbage collection
git gc --aggressive
```

---

## Debugging

```powershell
# Search for text in commits
git log -S "search term"

# Find who deleted a line
git log -p file.py | grep -A 5 -B 5 "deleted text"

# See all changes by author
git log --author="name"

# See changes between commits
git diff abc123d def456d

# See what's in a commit
git show abc123d

# Bisect to find problematic commit
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
```

---

## Safety First

```powershell
# Always check before destructive operations
git status
git log --oneline -5

# Use --dry-run with some commands
git clean -fdxn  # shows what would be deleted

# Create backup branch
git branch backup/before-rebase

# Use --force-with-lease instead of --force
git push --force-with-lease origin master

# Configure to prevent accidental pushes
git config --global receive.denyDeletes true
```

---

## Help

```powershell
# Get help
git help
git help commit
git help push

# Verbose output
git commit -v

# Dry run
git push --dry-run
```

---

## Most Important Commands

```powershell
# Remember these 5 commands for 90% of work:
git status          # Check what changed
git add .           # Stage changes
git commit -m "msg" # Create commit
git push            # Upload to remote
git pull            # Download from remote
```

---

**Need help?** Check: `git help <command>`
