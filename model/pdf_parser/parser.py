import os
from typing import Tuple

from model.pdf_parser.pdf_parser import PDF_Parser
from model.pdf_parser.img_parser import PDF_Image_Parser
from model.pdf_parser.utils import count_tokens_in_pdf

import model.GC as GC

class PdfParser:
    def __init__(self, file_path:str, max_pages:int=GC.MAX_PAGES_INGESTION):
        self.data_dir = "./data"
        self.file_name = os.path.basename(file_path)
        self.file_path, self.ext = os.path.splitext(file_path)
        assert self.is_pdf(), "The provided file is not a PDF."

        self.max_pages_ingestion = max_pages

        self.n_tokens = self.count_pdf_tokens()
        self.parser = self.parse_pdf()
        self.parse_method = self.parser.__method__

        self.raw_text = f"*File name*: {self.file_name} \n" + self.parser.raw_text
        self.preview = self.parser.preview
    
    def __str__(self) -> str:
        """Print the parsed information from the PDF file.

        Returns:
            str: File name, number of tokens, parse method and raw text.
        """
        msg = f"FILE_NAME:'{self.file_name}'. \n"
        msg += f"\t - N_TOKENS: {self.n_tokens}. \n"
        msg += f"\t - PARSE_METHOD: {self.parse_method}.\n\n"
        msg += "=" * 70
        msg += f"\n\n {self.raw_text}"
        return msg

    def is_pdf(self) -> bool:
        """Return whether the file concerns a pdf document.

        Returns:
            bool: True if the document concerns a PDF.
        """
        return self.ext.lower() == ".pdf"

    def count_pdf_tokens(self) -> int:
        """Count the number of tokens in a document.

        Returns:
            int: The amount of tokens in the PDF file.
        """
        filepath = os.path.join(self.file_path + self.ext)
        return count_tokens_in_pdf(filepath)
    
    def parse_pdf(self) -> object:
        """Parse PDF file using pure PDF parsing or OCR (Vision).

        Returns:
            object: Parser class instance containing all information.
        """
        if self.n_tokens > 0:
            parser = PDF_Parser(
                file_path=self.file_path + self.ext,
                max_pages_ingestion=self.max_pages_ingestion
            )
            if parser._output_accepted():
                return parser

        return PDF_Image_Parser(
            file_path=self.file_path + self.ext,
            max_pages_ingestion=self.max_pages_ingestion
        )
