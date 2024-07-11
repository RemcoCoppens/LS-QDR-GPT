import os
from typing import Tuple

from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from PIL.PpmImagePlugin import PpmImageFile

import model.GC as GC

class PDF_Image_Parser:
    def __init__(self, file_path:str, max_pages_ingestion:int):
        self.__method__ = "IMAGE-PDF"

        self.file_path = file_path
        self.file_name, self.ext = os.path.splitext(file_path)
        self.page_delimiter = '\n\n\n'

        self.page_removal_patterns = GC.PAGE_REMOVAL_PATTERNS
        self.max_pages_ingestion = max_pages_ingestion
        self.preview_pages = GC.DOC_PREVIEW_PAGES

        self.images = self.read_images_from_path()
        self.raw_text, self.preview = self.read_text_from_images()

    def __str__(self) -> str:
        """Print the raw text.

        Returns:
            str: Raw text.
        """
        return self.raw_text

    def __len__(self) -> int:
        """Return the length of the raw text found in the PDF.

        Returns:
            int: Integer amount of words.
        """
        return len(self.raw_text)

    def convert_ppm_to_image(self, ppm_image:PpmImageFile) -> Image:
        """Convert the PPM output from the pdf2image library to a PIL.Image.

        Args:
            ppm_image (PpmImageFile): An image in PPM format (pdf2image library).

        Returns:
            Image: PIL Image of the PDF file.
        """
        if ppm_image.mode != 'RGB':
            ppm_image = ppm_image.convert('RGB')
        
        image = Image.new('RGB', ppm_image.size)
        image.paste(ppm_image)
        return image
    
    def read_images_from_path(self) -> Image:
        """Read the PDF from the path and convert it to a PIL.Image.

        Returns:
            Image: A PIL.Image of the PDF file.
        """
        ppm_images = convert_from_path(
            self.file_path,
            last_page=self.max_pages_ingestion + 3 # 3 as margin for potential removal due to patterns.
        )
        images = []
        for ppm_image in ppm_images:
            images.append(self.convert_ppm_to_image(ppm_image))
        
        return images
    
    def use_page(self, content:str) -> bool:
        """Decide whether to remove or use the page dependent on the occurrence of (a) removal pattern(s).

        Args:
            content (list): The content of the page (/image) that is validated.

        Returns:
            bool: False if a removal pattern is found, True otherwise.
        """
        for pattern in self.page_removal_patterns:
            if pattern in content:
                return False
        return True

    def read_text_from_images(self) -> Tuple[str, str]:
        """Convert all page images of the inserted PDF into a single raw text.

        Returns:
            Tuple[str, str]: Raw text and preview string describing the document.
        """
        text, preview = "", ""
        pages_added = 0

        for image in self.images:
            img_text = pytesseract.image_to_string(image, lang='nld').strip().lower()
            
            if self.use_page(content=img_text):
                text += (img_text + self.page_delimiter)
                if pages_added < self.preview_pages:
                    preview += img_text

                pages_added += 1

                if pages_added == self.max_pages_ingestion:
                    break

        return text, preview
