# SCIENCEMENTOR - Complete Setup Guide for Windows

This guide will walk you through setting up SCIENCEMENTOR on Windows from scratch, even if you've never used Docker before.

---

## 📋 What You'll Need

- Windows 10/11 (64-bit)
- At least 4GB of RAM
- 10GB of free disk space
- Internet connection
- An Anthropic API key (for Claude AI)

---

## Step 1: Install Docker Desktop

### Download Docker Desktop

1. Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click **"Download for Windows"**
3. Wait for the installer to download (about 500MB)

### Install Docker

1. **Run the installer** (`Docker Desktop Installer.exe`)
2. Keep all default settings checked ✅
3. Click **"OK"** to start installation
4. Wait for installation to complete (5-10 minutes)
5. Click **"Close"** when done

### First-Time Setup

1. **Start Docker Desktop** from the Start menu
2. Click **"Accept"** on the Service Agreement
3. Choose **"Use recommended settings"**
4. **Sign in** or **Skip** (signing in is optional)
5. Wait for Docker to start (you'll see a green "Running" status)

> **Important:** Docker Desktop must be running for SCIENCEMENTOR to work!

---

## Step 2: Get the SCIENCEMENTOR Code

### Option A: Download ZIP (Easiest)

1. Go to the GitHub repository (ask your brother for the link)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to a folder (e.g., `C:\Users\YourName\science-mentor`)

### Option B: Using Git (Recommended)

1. Install Git from [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Open **Command Prompt** or **PowerShell**
3. Navigate to where you want the project:
   ```bash
   cd C:\Users\YourName\Documents
   ```
4. Clone the repository:
   ```bash
   git clone [repository-url]
   cd science-mentor
   ```

---

## Step 3: Configure Your API Key

### Get an Anthropic API Key

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-...`)

> **⚠️ Important:** Keep this key secret! Don't share it with anyone.

### Add the API Key to the Project

1. Open the `science-mentor` folder
2. Navigate to `backend` folder
3. Find the file named `.env.example`
4. **Right-click** → **Open with** → **Notepad**
5. You'll see something like:
   ```
   ANTHROPIC_API_KEY=sk-ant-your_key_here
   ```
6. Replace `sk-ant-your_key_here` with your actual API key
7. **Save As** → Change filename to `.env` (remove the `.example`)
8. Make sure **"Save as type"** is set to **"All Files"**
9. Click **Save**

**Your `.env` file should look like:**

```
ANTHROPIC_API_KEY=sk-ant-api03-xyz123abc456...
OPENAI_API_KEY=sk-your_key_here
GEMINI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://host.docker.internal:11434
DEFAULT_LLM_PROVIDER=claude
FLASK_DEBUG=true
DATABASE_URL=
```

> **Note:** You only need the Anthropic key. The others are optional.

---

## Step 4: Start SCIENCEMENTOR

### Using Command Prompt

1. Press **Windows + R**
2. Type `cmd` and press **Enter**
3. Navigate to your project folder:
   ```bash
   cd C:\Users\YourName\Documents\science-mentor
   ```
4. Start the application:
   ```bash
   docker-compose up -d
   ```

### What Happens Next

- Docker will download the required images (first time only, ~5 minutes)
- You'll see progress bars as things download
- When done, you'll see:
  ```
  ✔ Container science-mentor-backend-1   Started
  ✔ Container science-mentor-frontend-1  Started
  ```

---

## Step 5: Use SCIENCEMENTOR

### Open the App

1. Open your web browser (Chrome, Firefox, Edge)
2. Go to: **http://localhost:8080**
3. You should see the SCIENCEMENTOR welcome screen! 🎉

### Try It Out

- Click **"New Chat"** to start
- Ask a biology question like: "What is DNA?"
- Watch as the AI explains in detail!

---

## Common Commands

### Start the App

```bash
docker-compose up -d
```

> The `-d` flag runs it in the background

### Stop the App

```bash
docker-compose down
```

### View Logs (if something's wrong)

```bash
docker-compose logs backend
```

### Restart After Changes

```bash
docker-compose restart
```

### Rebuild Everything

```bash
docker-compose down
docker-compose up --build -d
```

---

## Troubleshooting

### ❌ "Docker is not running"

**Solution:**

1. Open Docker Desktop from the Start menu
2. Wait until you see "Docker Desktop is running"
3. Try the command again

### ❌ "Port 8080 is already in use"

**Solution:**

1. Another app is using that port
2. Stop that app, or
3. Edit `docker-compose.yml` and change `8080:80` to `8081:80`
4. Then access at http://localhost:8081

### ❌ "Cannot connect to the Docker daemon"

**Solution:**

1. Make sure Docker Desktop is running
2. Restart Docker Desktop
3. Restart your computer if needed

### ❌ API Key Error

**Solution:**

1. Check that your `.env` file exists in the `backend` folder
2. Make sure the API key is correct (no extra spaces)
3. Restart the containers:
   ```bash
   docker-compose restart backend
   ```

### ❌ Chatbot Responds in Wrong Language

**Solution:**

1. The latest version should auto-detect language
2. Make sure to ask in English if you want English responses
3. Restart if needed:
   ```bash
   docker-compose restart backend
   ```

### ❌ "Error: Cannot find module"

**Solution:**

```bash
docker-compose down
docker-compose up --build -d
```

---

## Updating SCIENCEMENTOR

If your brother sends you an update:

1. **Stop the app:**

   ```bash
   docker-compose down
   ```

2. **Get the new code:**

   - If using Git:
     ```bash
     git pull
     ```
   - If using ZIP: Download and extract new version

3. **Rebuild and start:**
   ```bash
   docker-compose up --build -d
   ```

---

## Understanding the Folder Structure

```
science-mentor/
├── backend/              ← Python code (API)
│   ├── .env             ← Your API keys (keep secret!)
│   ├── app.py           ← Main server
│   └── knowledge_base.json  ← Biology info
├── frontend/            ← Website files
│   ├── index.html       ← Main page
│   ├── style.css        ← Styling
│   └── script.js        ← Interactive code
├── docker-compose.yml   ← Docker configuration
└── Dockerfile           ← How to build the app
```

---

## Advanced: Running Without Docker

If you prefer to run without Docker:

### Install Python

1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Install with "Add to PATH" checked

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run Backend

```bash
cd backend
python app.py
```

### Run Frontend

1. Install a simple HTTP server:
   ```bash
   pip install http.server
   ```
2. In a new terminal:
   ```bash
   cd frontend
   python -m http.server 8080
   ```

---

## Still Need Help?

### Check Logs

```bash
docker-compose logs backend
docker-compose logs frontend
```

### Get More Details

```bash
docker-compose ps
docker-compose config
```

### Contact Support

- Check the terminal output for error messages
- Share the error logs with your brother
- Make sure Docker Desktop is running

---

## Security Tips

1. ✅ **Never share your `.env` file**
2. ✅ **Never commit `.env` to Git**
3. ✅ **Keep your API keys private**
4. ✅ **Use different API keys for testing vs production**
5. ✅ **Delete old API keys you're not using**

---

## Quick Reference Card

| Task         | Command                        |
| ------------ | ------------------------------ |
| Start app    | `docker-compose up -d`         |
| Stop app     | `docker-compose down`          |
| View logs    | `docker-compose logs backend`  |
| Restart      | `docker-compose restart`       |
| Rebuild      | `docker-compose up --build -d` |
| Check status | `docker-compose ps`            |

**Access URLs:**

- Frontend: http://localhost:8080
- Backend API: http://localhost:5000
- Health check: http://localhost:5000/health

---

## Next Steps

Once everything is running:

1. ✅ Test with a few biology questions
2. ✅ Try the chat history feature (sidebar)
3. ✅ Create a new chat and test session persistence
4. ✅ Delete old chats to test the delete feature
5. ✅ Check that responses are detailed and educational

**Enjoy learning Biology with SCIENCEMENTOR! 🧬**
