# 📥 Install Git on Windows - Step by Step

Git is not currently installed on your system. Follow these steps to install it.

---

## 🚀 Option 1: Download & Install Manually (Recommended)

### Step 1: Download Git for Windows
1. Go to: https://git-scm.com/download/win
2. Download will start automatically
3. Look for file named `Git-2.x.x-64-bit.exe` in your Downloads folder

### Step 2: Run the Installer
1. Double-click `Git-2.x.x-64-bit.exe`
2. Click "Next" through the installation wizard
3. **Important settings:**
   - ✅ Keep default installation path (usually `C:\Program Files\Git`)
   - ✅ Select "Git Bash Here" and "Git GUI Here"
   - ✅ Choose "Use Git from the command line and also from 3rd-party software"
   - ✅ Choose "Use bundled OpenSSL"
   - ✅ Choose "Checkout as-is, commit as-is"
   - ✅ Choose "Use MinTTY (the default terminal of MSYS2)"

### Step 3: Complete Installation
1. Click "Install"
2. Wait for completion
3. Click "Finish"

### Step 4: Verify Installation
Open a new PowerShell and run:
```powershell
git --version
```

Should show: `git version 2.x.x`

---

## 🍺 Option 2: Install via Package Manager

### Using Chocolatey (if installed)
```powershell
choco install git
```

### Using Windows Package Manager (if installed)
```powershell
winget install Git.Git
```

---

## ✅ Post-Installation Setup

After installing Git, run these commands:

```powershell
# Set your name and email (required)
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"

# Verify
git config --global user.name
git config --global user.email
```

---

## 🆘 Troubleshooting

### "Git not found" after installation
1. **Close and reopen PowerShell** - Important!
2. Try `git --version` again
3. If still not working, check installation path:
   - Look in `C:\Program Files\Git\bin` for `git.exe`

### Installation failed
1. Uninstall completely: Programs → Uninstall Git
2. Restart computer
3. Try installing again

### Need to reinstall
```powershell
# Check current version
git --version

# If needed, uninstall and download latest from:
# https://git-scm.com/download/win
```

---

## ✅ Next Steps

After Git is installed:
1. ✅ Verify with `git --version`
2. ✅ Run `git config` commands above
3. ✅ Go back to [GIT_EXECUTE_NOW.md](GIT_EXECUTE_NOW.md)
4. ✅ Follow the exact steps starting from Step 1

---

## 📚 Learn More

- Git Official: https://git-scm.com
- Windows Installation Guide: https://git-scm.com/download/win
- GitHub Setup: https://docs.github.com/en/get-started

---

**Once Git is installed, start with [GIT_EXECUTE_NOW.md](GIT_EXECUTE_NOW.md)** 🚀
