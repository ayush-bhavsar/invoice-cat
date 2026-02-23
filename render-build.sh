#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Tesseract OCR
apt-get update && apt-get install -y tesseract-ocr

pip install -r requirements.txt