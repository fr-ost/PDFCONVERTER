FROM python:3.12-slim

# Install LibreOffice Impress (for PPTX to PDF) and common fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-impress \
    fonts-liberation \
    fonts-noto \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

CMD ["python", "bot.py"]
