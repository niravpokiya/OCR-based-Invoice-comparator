import os

TESSERACT_PATH = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = os.getenv(
	"POPPLER_PATH",
	r"C:/Users/91769/Downloads/Release-26.02.0-0/poppler-26.02.0/Library/bin",
)
UPLOAD_FOLDER = 'app/uploads'
