# Tender Analyser

AI-powered government tender analysis tool built with Python and Claude AI.

## What it does

Upload any government tender PDF. The system reads it, extracts every 
relevant field, and produces two downloadable Word documents — a formatted 
One Pager and a full Bid Intelligence Report — in under 30 seconds.

## Features

- PDF upload with drag and drop
- AI extracts all tender fields automatically
- Editable preview before generating documents
- One Pager DOCX in exact organisational format
- Bid Intelligence Report DOCX with 8 structured sections
- Organisation Match Engine — checks 9 eligibility criteria
- Bid Strength Score out of 100
- Win Probability percentage with reasoning
- Auto-incrementing document reference numbers

## Tech stack

Python · FastAPI · Claude AI API · PyMuPDF · python-docx · HTML/CSS/JS

## How to run

cd tender-analyser
source venv/bin/activate
python3 main.py
# Open http://localhost:8001