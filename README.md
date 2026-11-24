<div align="center">

<img width="100%" alt="PDFCONVERTER — Telegram bot that turns PowerPoint and Word files into PDF" src="https://capsule-render.vercel.app/api?type=waving&color=0:6C2BD9,50:FF2E93,100:FFB703&height=210&section=header&text=PDFCONVERTER&fontSize=50&fontColor=ffffff&fontAlignY=30&animation=fadeIn&desc=PowerPoint%20and%20Word%20to%20PDF%20%C2%B7%20Telegram&descAlignY=62&descAlign=50&descSize=18"/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3600&pause=700&color=FFB703&center=true&vCenter=true&width=780&height=48&lines=Send+a+PowerPoint+or+Word+file;Get+a+PDF+back+in+Telegram;PPTX%2C+PPT%2C+DOCX%2C+and+DOC;LibreOffice+headless+%C2%B7+20+MB+limit" />
  <source media="(prefers-color-scheme: light)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3600&pause=700&color=6C2BD9&center=true&vCenter=true&width=780&height=48&lines=Send+a+PowerPoint+or+Word+file;Get+a+PDF+back+in+Telegram;PPTX%2C+PPT%2C+DOCX%2C+and+DOC;LibreOffice+headless+%C2%B7+20+MB+limit" />
  <img width="780" alt="Send a PowerPoint or Word file. Get a PDF back in Telegram. Supports PPTX, PPT, DOCX, and DOC. LibreOffice headless, 20 MB limit." src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3600&pause=700&color=6C2BD9&center=true&vCenter=true&width=780&height=48&lines=Send+a+PowerPoint+or+Word+file;Get+a+PDF+back+in+Telegram;PPTX%2C+PPT%2C+DOCX%2C+and+DOC;LibreOffice+headless+%C2%B7+20+MB+limit" />
</picture>

**A Telegram bot that converts PowerPoint and Word documents to PDF with headless LibreOffice.**

<br/>

<img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img alt="Telegram bot" src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"/>
<img alt="LibreOffice headless" src="https://img.shields.io/badge/LibreOffice-headless-18A303?style=for-the-badge&logo=libreoffice&logoColor=white"/>
<img alt="python-telegram-bot 21.6" src="https://img.shields.io/badge/python--telegram--bot-21.6-6C2BD9?style=for-the-badge"/>
<img alt="Dockerfile included" src="https://img.shields.io/badge/Docker-Dockerfile-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>

</div>

## 📄 Overview

PDFCONVERTER is a long-polling Telegram bot. You send a PowerPoint (`.pptx`, `.ppt`) or Word (`.docx`, `.doc`) file **as a document**, and the bot sends back a PDF.

Conversion is done by LibreOffice in headless mode. Each run gets its own LibreOffice user profile, so a missing, busy, or locked default profile does not hang the process. Files larger than **20 MB** are rejected (Telegram Bot API limit). A conversion that runs longer than `CONVERT_TIMEOUT` (default **180 seconds**) is stopped.

A single long-polling process handles every chat.

## ✨ Features

| | What it does |
| --- | --- |
| **Formats** | `.pptx`, `.ppt`, `.docx`, `.doc` in. A PDF named from the original file stem out. |
| **Commands** | `/start` explains what to send. `/help` lists the accepted formats. |
| **Progress** | Replies `Downloading...`, then `Converting...`, then `Uploading...`, then the PDF. The status message is removed after a successful upload. |
| **Wrong input** | A document with another extension, a text message, or a photo gets a short reply asking for a document in one of the formats above. |
| **Size cap** | 20 MB. Larger files are refused before download. |
| **Timeouts** | LibreOffice is killed after `CONVERT_TIMEOUT` seconds. Telegram read and write timeouts are 120 seconds; connect and pool timeouts are 30 seconds. |
| **Failures** | Conversion errors are logged, and the chat gets a short message (the first 150 characters of the error). |
| **Fonts in Docker** | The image installs Liberation, Noto, and DejaVu so common documents render with real fonts. |

<details>
<summary><strong>How a conversion actually runs</strong></summary>

<br/>

`bot.py` shells out to the `libreoffice` binary. For each file it creates a fresh profile directory inside a temporary folder and passes it as `-env:UserInstallation=file://...`. The process is started with `--headless`, `--norestore`, `--nolockcheck`, `--nologo`, `--convert-to pdf`, and `--outdir` set to that same temp folder.

The PDF is expected at `<original stem>.pdf`. If LibreOffice exits non-zero, or that file never appears, the bot reports the failure instead of sending an empty document. The temp directory (input, profile, and PDF) is deleted when the handler finishes.

</details>

## 🧰 Tech stack

| Piece | Where it shows up |
| --- | --- |
| **Python 3.12** | Base image in the `Dockerfile` (`python:3.12-slim`) |
| **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 21.6** | Handlers, document download, and `run_polling` |
| **python-dotenv 1.0.1** | Loads a local `.env` when you run outside Docker |
| **LibreOffice Impress and Writer** | Headless conversion (`libreoffice-impress`, `libreoffice-writer`) |
| **Liberation, Noto, DejaVu** | Fonts installed in the image |

## 🚀 Getting started

You need a Telegram bot token from [@BotFather](https://t.me/BotFather) (`/newbot`). Keep that token out of git. This repository does not include a `.gitignore`, so do not add a `.env` file to a commit.

### Local

Python 3.12 and a `libreoffice` binary on your `PATH`. On Debian or Ubuntu, the same packages the image installs:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  libreoffice-impress \
  libreoffice-writer \
  fonts-liberation \
  fonts-noto \
  fonts-dejavu
```

```bash
pip install -r requirements.txt
```

Put the token in a `.env` file in the project directory (variables are listed under Configuration), then:

```bash
python bot.py
```

The log line `Bot starting...` means polling has started.

### Docker

The `Dockerfile` installs LibreOffice, the fonts, and the Python dependencies, then runs `python bot.py`.

```bash
docker build -t pdfconverter .
docker run --rm -e BOT_TOKEN="your_token_from_botfather" pdfconverter
```

`CONVERT_TIMEOUT` can be passed the same way (`-e CONVERT_TIMEOUT=180`). The first image build is slow because it installs LibreOffice.

### Railway

A fully browser-based walkthrough (no local terminal) is in [DEPLOY.md](DEPLOY.md). Short version:

1. Create the bot with @BotFather and copy the token.
2. Host this repository on GitHub. Do not commit the token.
3. In Railway, create a project with **Deploy from GitHub repo** and select the repo. Railway builds the `Dockerfile`. The file must be named exactly `Dockerfile`.
4. On the service, open **Variables** and add `BOT_TOKEN`. Railway redeploys when the variable is saved.
5. In **Deployments**, open the logs. You should see `Bot starting...`. Then message the bot on Telegram.

Railway includes a small monthly usage credit on the free or trial plan. A low-traffic bot often stays inside that credit. Heavier use may need a paid plan. Check [railway.com](https://railway.com) for current pricing.

Editing a file on GitHub is enough to trigger a new Railway deploy when the project is connected to the repo.

## ⚙️ Configuration

Names only. Never commit a real token, and never paste one into a chat or a pull request.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Yes | — | Telegram bot token from @BotFather. The process exits on startup if this is missing. |
| `CONVERT_TIMEOUT` | No | `180` | Seconds before an in-flight LibreOffice conversion is killed. |

Example `.env` for a local run (do not commit this file):

```bash
BOT_TOKEN=your_token_from_botfather
CONVERT_TIMEOUT=180
```

On Railway, set `BOT_TOKEN` in the service **Variables** tab instead of uploading a `.env`.

## 💬 Usage

1. Open the bot in Telegram and send `/start`.
2. Attach the file with the **document** (paperclip) picker. A photo or a plain text message gets a reply asking for a document instead.
3. Wait for `Downloading...`, `Converting...`, and `Uploading...`.
4. The bot replies with the PDF, using the original file name and a `.pdf` extension.
5. `/help` repeats the accepted extensions.

| You send | The bot does |
| --- | --- |
| `/start` | Greeting plus the 20 MB limit |
| `/help` | Asks for a `.pptx`, `.ppt`, `.docx`, or `.doc` document |
| A supported document under 20 MB | Returns the PDF |
| Another extension | Asks for a supported file |
| A file over 20 MB | `File is too large. Max size is 20 MB.` |
| Text or a photo | Asks you to send the file as a document |

<details>
<summary><strong>When something goes wrong</strong></summary>

<br/>

| Symptom | What to check |
| --- | --- |
| The bot never replies | Logs. The usual cause is a missing or wrong `BOT_TOKEN`. Locally the process raises `BOT_TOKEN is not set` and exits. |
| `Sorry, conversion failed...` | LibreOffice failed, the PDF was not written, or the run exceeded `CONVERT_TIMEOUT`. The message includes a short slice of the error. Very large or complex files hit the timeout. |
| Docker or Railway build fails | The `Dockerfile` has to be present and named exactly `Dockerfile`, with no extra extension. |
| PDF fonts look wrong | The image ships Liberation, Noto, and DejaVu. A face that is not in that set is substituted. |
| File rejected for size | Telegram's Bot API caps bot downloads at 20 MB. This bot enforces that cap in code. Going past it means running a [local Bot API server](https://core.telegram.org/bots/api#using-a-local-bot-api-server), which this project does not set up. |

</details>

## 🗂️ Project structure

```text
.
├── bot.py             # Telegram handlers and the LibreOffice conversion
├── requirements.txt   # python-telegram-bot==21.6, python-dotenv==1.0.1
├── Dockerfile         # Python 3.12, LibreOffice Impress + Writer, fonts
├── DEPLOY.md          # Browser-based Railway deploy guide
├── .gitattributes     # Line-ending normalization
└── README.md
```

## 👤 Credits

Built by **[Shahriar Ahmed](https://github.com/fr-ost)**, Co-Founder & COO of **[Unique Labs](https://www.uniquelabs.org)**.

<div align="center">

<a href="https://github.com/fr-ost"><img alt="Shahriar Ahmed on GitHub" src="https://img.shields.io/badge/Shahriar_Ahmed-6C2BD9?style=for-the-badge&logo=github&logoColor=white"/></a>
<a href="https://www.uniquelabs.org"><img alt="Unique Labs" src="https://img.shields.io/badge/Unique_Labs-FF2E93?style=for-the-badge"/></a>
<a href="https://shahriarahmed.net"><img alt="shahriarahmed.net" src="https://img.shields.io/badge/shahriarahmed.net-FFB703?style=for-the-badge&logoColor=1A1024"/></a>

<br/>

<img width="100%" alt="Footer wave" src="https://capsule-render.vercel.app/api?type=waving&color=0:FFB703,50:FF2E93,100:6C2BD9&height=120&section=footer"/>

</div>
