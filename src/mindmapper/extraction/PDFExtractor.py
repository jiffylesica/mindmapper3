from pathlib import Path
import fitz  # PyMuPDF


class PDFExtractor:
    """Extracts text from PDF files using PyMuPDF."""

    def __init__(self):
        """Initialize the PDFExtractor."""
        pass

    def extract_text_from_pdf(self, pdf_path: Path | str) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text as a single string.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the file is not a valid PDF or extraction fails.
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num, page in enumerate(doc):
                try:
                    page_text = page.get_text()
                    text += page_text
                except Exception as e:
                    raise ValueError(
                        f"Failed to extract text from page {page_num + 1}: {str(e)}"
                    )

            doc.close()
            return text

        except fitz.FileError as e:
            raise ValueError(f"Invalid PDF file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
