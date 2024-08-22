import re
from pypdf import PdfReader

def count_tokens_in_pdf(pdf_file_path: str) -> int:
    """Count the number of tokens within the given PDF file.

    Args:
        pdf_file_path (str): Path to PDF file.

    Returns:
        int: Total number of tokens in the concerning PDF file.
    """
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        total_tokens = 0

        for page in pdf_reader.pages:
            text = page.extract_text()
            # Tokenize by splitting on whitespace or punctuation using regex
            tokens = re.findall(r'\b\w+\b', text)
            total_tokens += len(tokens)

    return total_tokens
