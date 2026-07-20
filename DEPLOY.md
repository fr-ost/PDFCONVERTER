# PPTX to PDF Telegram Bot: Railway Deploy Guide

Fully browser based. No local machine, no terminal on your side.

## Files in this project

- `bot.py` - the bot code
- `requirements.txt` - Python packages
- `Dockerfile` - tells Railway to install LibreOffice
- `.gitignore` - keeps secrets out of the repo

You do NOT upload `.env` to GitHub. The token goes in Railway settings instead.

## 1. Get a Bot Token

1. Open Telegram, search for `@BotFather`.
2. Send `/newbot`.
3. Follow the prompts (bot name, then a username ending in `bot`).
4. Copy the token. Keep it safe.

## 2. Create a GitHub Repo

1. Go to github.com and log in (or sign up, it is free).
2. Click the **+** at the top right, then **New repository**.
3. Name it `pptx-pdf-bot`.
4. Set it to **Private** (recommended).
5. Do NOT check "Add a README". Leave it empty.
6. Click **Create repository**.

## 3. Upload the Files to GitHub

On the new empty repo page:

1. Click the link **uploading an existing file**.
2. Download these four files from this chat, then drag them into the browser:
   - `bot.py`
   - `requirements.txt`
   - `Dockerfile`
   - `.gitignore`
3. Scroll down, click **Commit changes**.

Your repo now has all four files.

## 4. Deploy on Railway

1. Go to railway.com and log in with your GitHub account.
2. Click **New Project**.
3. Choose **Deploy from GitHub repo**.
4. If asked, give Railway permission to see your repos.
5. Select your `pptx-pdf-bot` repo.
6. Railway detects the Dockerfile and starts building.

The first build takes a few minutes because it installs LibreOffice.

## 5. Add Your Bot Token

While it builds (or after):

1. In your Railway project, click the service.
2. Go to the **Variables** tab.
3. Click **New Variable**.
4. Name: `BOT_TOKEN`
5. Value: paste your token from BotFather.
6. Click **Add**.

Railway will redeploy automatically with the token.

## 6. Check It Works

1. Go to the **Deployments** tab, open the latest deployment.
2. Click **View Logs**.
3. You should see `Bot starting...`.
4. Open Telegram, find your bot, send `/start`, then send a PPTX file.
5. It replies with the PDF.

## Updating the Bot Later

1. Edit any file directly on GitHub (open the file, click the pencil icon, save).
2. Railway sees the change and redeploys automatically.

No terminal, ever.

## Common Issues

**Bot does not respond**: check Railway logs. Most common cause is a wrong or missing `BOT_TOKEN` variable.

**Build fails**: make sure the `Dockerfile` was uploaded and is named exactly `Dockerfile` with no extension.

**File too large error**: Telegram Bot API caps uploads at 20 MB. Bigger files need a local Bot API server (advanced).

**Fonts look wrong**: the Dockerfile already installs common fonts. If a specific font is missing, tell me which and I will add it.

## Cost

Railway gives a small monthly usage credit on the free/trial plan. A low traffic bot like this often fits inside it. If you convert a lot, you may need the Hobby plan (a few dollars a month). Check railway.com for current pricing.
