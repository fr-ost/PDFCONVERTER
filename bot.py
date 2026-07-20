import os
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me a PPTX file and I will convert it to PDF.\n\n"
        "Max file size: 20 MB"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a .pptx or .ppt file as a document. "
        "I will send back the converted PDF."
    )


async def convert_pptx_to_pdf(input_path: str, output_dir: str) -> str:
    """Convert PPTX to PDF using LibreOffice in headless mode."""
    proc = await asyncio.create_subprocess_exec(
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"LibreOffice failed: {stderr.decode(errors='ignore')}")

    input_name = Path(input_path).stem
    output_path = os.path.join(output_dir, f"{input_name}.pdf")

    if not os.path.exists(output_path):
        raise RuntimeError("PDF was not created")

    return output_path


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        return

    filename = document.file_name or ""
    if not filename.lower().endswith((".pptx", ".ppt")):
        await update.message.reply_text("Please send a .pptx or .ppt file.")
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
            pdf_path = await convert_pptx_to_pdf(input_path, tmpdir)

            await status.edit_text("Uploading...")
            with open(pdf_path, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=Path(pdf_path).name,
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
        "Please send the PPTX as a file (document), not as text or photo."
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Check your .env file.")

    app = Application.builder().token(BOT_TOKEN).build()

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
