import os
import base64
from typing import List
from pdf2image import convert_from_path
import io

class PDFProcessor:
    def convert_pdf_to_base64_images(self, pdf_path: str) -> List[str]:
        """
        Convert PDF pages to base64 encoded images.
        """
        images = convert_from_path(pdf_path)
        base64_images = []
        for img in images:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            base64_images.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
        return base64_images

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Fallback text extraction using pdftotext.
        """
        import subprocess
        try:
            result = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error extracting text: {str(e)}"
