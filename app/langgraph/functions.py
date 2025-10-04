import fitz
import base64

def number_of_pages_in_pdf(pdf_path: str) -> int:
    """
    Get the number of pages in a PDF file.
    """
    pdf_document = fitz.open(pdf_path)
    return pdf_document.page_count
def pdf_page_to_base64(pdf_path: str, page_number: int, scale_factor: float = 1) -> str:
    """
    Convert a given PDF page into a base64-encoded string representing the image.
    """
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1) 
    pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor)) 
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")