from pypdf import PdfReader
from transformers import GPT2Tokenizer

import model.GC as GC

def count_tokens_in_pdf(pdf_file_path:str) -> int:
    """Count the number of tokens within the given PDF file.

    Args:
        pdf_file_path (str): Path to PDF file.

    Returns:
        int: Total number of tokens in the concerning PDF file.
    """
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        total_tokens = 0

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            tokens = tokenizer.tokenize(text)
            total_tokens += len(tokens)

    return total_tokens
