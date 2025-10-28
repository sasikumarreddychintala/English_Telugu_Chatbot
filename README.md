Install Dependencies
pip install fastapi uvicorn pillow pytesseract googletrans==4.0.0-rc1

sudo apt install tesseract-ocr
Also install Tesseract OCR (system dependency):
https://github.com/UB-Mannheim/tesseract/wiki
Run the API
uvicorn main:app --reload
Response Example:
{
  "english_text": "Welcome to our hostel",
  "telugu_translation": "మా హాస్టల్‌కి స్వాగతం"
}

