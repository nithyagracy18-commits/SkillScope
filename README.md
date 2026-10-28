# Resume Skill Gap Analyzer — Starter

This starter implements the first milestone: extract text from PDF, DOCX, and image resumes, using OCR when needed.

## 1. Requirements
- Windows 10/11
- Python 3.10–3.12 recommended
- Tesseract OCR installed separately for scanned PDFs/images

## 2. Create and activate a virtual environment
Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Install Tesseract OCR on Windows
Install the Windows Tesseract OCR application from the official UB Mannheim builds:
https://github.com/UB-Mannheim/tesseract/wiki

During installation, note the executable path. Common example:
`C:\Program Files\Tesseract-OCR\tesseract.exe`

You can either add that folder to your Windows PATH, or set the path in `config.py`.
Then open a new terminal and test:
```powershell
tesseract --version
```

## 4. Run the extractor
```powershell
python extract_resume.py "C:\path\to\resume.pdf"
python extract_resume.py "C:\path\to\resume.docx"
python extract_resume.py "C:\path\to\scanned_resume.png"
```

Save extracted text to a file:
```powershell
python extract_resume.py "C:\path\to\resume.pdf" --output extracted.txt
```

## 5. How it works
- Digital PDF: extracts embedded text using PyMuPDF.
- Scanned PDF: if a page has very little embedded text, renders that page and runs Tesseract OCR.
- DOCX: extracts paragraph text and table-cell text with python-docx.
- PNG/JPG/TIFF/BMP: uses Tesseract OCR.
- The output states which method was used per page/document.

## 6. Troubleshooting
- `TesseractNotFoundError`: install Tesseract and set `TESSERACT_CMD` in `config.py`.
- `Poppler` is not required; PyMuPDF renders PDF pages itself.
- OCR is slower than direct extraction. It is only used on PDF pages that appear to lack embedded text.
- If OCR output is poor, try a clearer scan, higher resolution, straight pages, and good contrast.

## Privacy
Use sample, consented, anonymized, or appropriately licensed resumes for testing. Do not commit real resumes or extracted personal data to GitHub.
