import os
import time
import logging
import asyncio
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB (Telegram Bot API limit)
CONVERT_TIMEOUT = int(os.getenv("CONVERT_TIMEOUT", "180"))  # seconds
SUPPORTED_EXT = (".pptx", ".ppt", ".docx", ".doc")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me a PowerPoint (.pptx, .ppt) or Word (.docx, .doc) file "
        "and I will convert it to PDF.\n\n"
        "Max file size: 20 MB"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a .pptx, .ppt, .docx, or .doc file as a document. "
        "I will send back the converted PDF."
    )


async def convert_to_pdf(input_path: str, output_dir: str) -> str:
    """Convert a PPTX/PPT/DOCX/DOC file to PDF using LibreOffice headless."""
    # Isolated user profile per run. Prevents LibreOffice from hanging when the
    # default profile is missing, busy, or locked by another invocation.
    profile_dir = os.path.join(output_dir, "lo_profile")
    os.makedirs(profile_dir, exist_ok=True)

    cmd = [
        "libreoffice",
        f"-env:UserInstallation=file://{profile_dir}",
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--nologo",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path,
    ]

    start_t = time.monotonic()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=CONVERT_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        try:
            await proc.wait()
        except Exception:
            pass
        raise RuntimeError(
            f"Conversion took longer than {CONVERT_TIMEOUT}s and was stopped. "
            "The file may be very large or very complex."
        )

    elapsed = time.monotonic() - start_t
    logger.info("LibreOffice finished in %.1fs (code %s)", elapsed, proc.returncode)

    if proc.returncode != 0:
        raise RuntimeError(
            f"LibreOffice failed: {stderr.decode(errors='ignore')[:300]}"
        )

    output_path = os.path.join(output_dir, f"{Path(input_path).stem}.pdf")
    if not os.path.exists(output_path):
        raise RuntimeError("PDF was not created")

    return output_path


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        return

    filename = document.file_name or ""
    if not filename.lower().endswith(SUPPORTED_EXT):
        await update.message.reply_text(
            "Please send a .pptx, .ppt, .docx, or .doc file."
        )
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("File is too large. Max size is 20 MB.")
        return

    status = await update.message.reply_text("Downloading...")

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            input_path = os.path.join(tmpdir, filename)
            tg_file = await document.get_file()
            await tg_file.download_to_drive(input_path)

            await status.edit_text("Converting...")
            pdf_path = await convert_to_pdf(input_path, tmpdir)

            await status.edit_text("Uploading...")
            with open(pdf_path, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=Path(pdf_path).name,
                    read_timeout=120,
                    write_timeout=120,
                )

            await status.delete()

        except Exception as e:
            logger.exception("Conversion failed")
            try:
                await status.edit_text(f"Sorry, conversion failed. {str(e)[:150]}")
            except Exception:
                pass


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please send the file as a document, not as text or photo."
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Check your environment variables.")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(120)
        .write_timeout(120)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other)
    )
    app.add_handler(MessageHandler(filters.PHOTO, handle_other))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
